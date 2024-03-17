from datetime import datetime, date

import time

from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from shelly2sgready.sgready import SGReadyStates, SGReadyControl

from waermepumpensteuerung.config import Config
from waermepumpensteuerung.simple_hysteresis import SimpleHysteresis
from waermepumpensteuerung.test_helper import load_testhelper

class ControllerLoop:

    def __init__(self, cfg: Config, logging, waermepumpe: SGReadyControl) -> None:
        self.logging = logging
        self.conf = cfg
        self.waermepumpe = waermepumpe

        self.interval = self.conf.heatpump_interval  # seconds

        influxdb_client = InfluxDBClient(
            url=cfg.influxdb_url,
            token=cfg.influxdb_token,
            org=cfg.influxdb_org
        )
        self.influxdb_write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
        self.influxdb_query_api = influxdb_client.query_api()

        # Used to track the transition to the next day for daily measurements
        self.todays_date = date.today()

        actual_price = self.get_actual_electricity_price()
        self.hyst_battery = SimpleHysteresis(upper_bound=self.get_actual_battery_soc_limit(actual_price), lower_bound=self.get_actual_battery_soc_limit(actual_price) - self.conf.battery_hysteresis)
        self.hyst_consumption = SimpleHysteresis(upper_bound=self.get_actual_consumption_limit(actual_price) + self.conf.consumption_hysteresis, lower_bound=self.get_actual_consumption_limit(actual_price), direction='down')

        self.hyst_battery_high = SimpleHysteresis(upper_bound=self.get_actual_battery_soc_limit(actual_price + self.conf.price_limit_force_state_dif),
                                             lower_bound=self.get_actual_battery_soc_limit(
                                                 actual_price + self.conf.price_limit_force_state_dif) - self.conf.battery_hysteresis)
        self.hyst_consumption_high = SimpleHysteresis(
            upper_bound=self.get_actual_consumption_limit(actual_price + self.conf.price_limit_force_state_dif) + self.conf.consumption_hysteresis,
            lower_bound=self.get_actual_consumption_limit(actual_price + self.conf.price_limit_force_state_dif), direction='down')


    def run(self):
        error_count = 0
        while True:
            try:
                self.controller()
                time.sleep(self.interval)
            except :
                error_count += 1
                self.logging.warning("Error (%d/10)", error_count)
                if error_count >= 10:
                    # Give up after a while
                    raise
                pass

    def controller(self):
        actual_price = self.get_actual_electricity_price()
        production_limit = self.get_actual_production_limit(actual_price)
        battery_soc_limit = self.get_actual_battery_soc_limit(actual_price)
        consumption_limit = self.get_actual_consumption_limit(actual_price)
        battery_state = self.get_actual_battery_state()
        self.logging.info(f"actual price = {actual_price}")
        self.logging.info(f"actual production limit = {production_limit}")
        self.logging.info(f"actual battery_soc limit = {battery_soc_limit}")
        self.logging.info(f"actual consumption limit = {consumption_limit}")
        self.logging.info(f"actual battery state = {battery_state}")


        actual_production = self.get_actual_production()
        actual_battery_soc = self.get_actual_battery_soc()
        actual_consumption = self.get_actual_consumption()
        self.logging.info(f"actual production = {actual_production}")
        self.logging.info(f"actual battery_soc = {actual_battery_soc}")
        self.logging.info(f"actual consumption = {actual_consumption}")
        self.logging.info(f"used for consumption: {'balkon' if self.conf.use_small_as_limit else 'dach'}")
        # self.logging.info(f"last battery soc = {self._get_battery_soc_from_db()}")
        # self.logging.info(f"mean consumption last 3 minutes = {self._get_consumption_from_db()}")
        # self.logging.info(f"mean production balkon last 3 minutes = {self._get_production_balkon_from_db()}")
        # self.logging.info(f"mean production dach last 3 minutes = {self._get_production_dach_from_db()}")


        if (self.hyst_consumption.test(value=actual_consumption,
                                      upper_bound=consumption_limit + self.conf.consumption_hysteresis,
                                      lower_bound=consumption_limit) and
                self.hyst_battery.test(value=actual_battery_soc, upper_bound=battery_soc_limit,
                                       lower_bound=battery_soc_limit - self.conf.battery_hysteresis) and
                actual_production >= production_limit):

            if self.is_enough_for_force(actual_price=actual_price, actual_consumption=actual_consumption, actual_battery_soc=actual_battery_soc, actual_production=actual_production):
                # new state Force
                self.set_heatpump_state(SGReadyStates.state4_force)
            else:
                # new state Go
                self.set_heatpump_state(SGReadyStates.state3_go)
        else:
            # new state Normal
            self.set_heatpump_state(SGReadyStates.state2_normal)



    def get_actual_production_limit(self, actual_price) -> int:
        limit = 5000

        if actual_price <= self.conf.price_limit_extreme_low_price:
            limit = self.conf.production_limit_small_extreme_low_price if self.conf.use_small_as_limit else self.conf.production_limit_extreme_low_price
        elif actual_price <= self.conf.price_limit_low_price:
            limit = self.conf.production_limit_small_low_price if self.conf.use_small_as_limit else self.conf.production_limit_low_price
        elif actual_price <= self.conf.price_limit_normal_price:
            limit = self.conf.production_limit_small_normal_price if self.conf.use_small_as_limit else self.conf.production_limit_normal_price
        elif actual_price <= self.conf.price_limit_high_price:
            limit = self.conf.production_limit_small_high_price if self.conf.use_small_as_limit else self.conf.production_limit_high_price
        elif actual_price <= self.conf.price_limit_extreme_high_price:
            limit = self.conf.production_limit_small_extreme_high_price if self.conf.use_small_as_limit else self.conf.production_limit_extreme_high_price

        return limit


    def get_actual_battery_soc_limit(self, actual_price) -> int:
        soc = 100

        if actual_price <= self.conf.price_limit_extreme_low_price:
            soc = self.conf.battery_soc_extreme_low_price
        elif actual_price <= self.conf.price_limit_low_price:
            soc = self.conf.battery_soc_low_price
        elif actual_price <= self.conf.price_limit_normal_price:
            soc = self.conf.battery_soc_normal_price
        elif actual_price <= self.conf.price_limit_high_price:
            soc = self.conf.battery_soc_high_price
        elif actual_price <= self.conf.price_limit_extreme_high_price:
            soc = self.conf.battery_soc_extreme_high_price

        return soc

    def get_actual_consumption_limit(self, actual_price) -> int:
        limit = 5

        if actual_price <= self.conf.price_limit_extreme_low_price:
            limit = self.conf.consumption_limit_extreme_low_price
        elif actual_price <= self.conf.price_limit_low_price:
            limit = self.conf.consumption_limit_low_price
        elif actual_price <= self.conf.price_limit_normal_price:
            limit = self.conf.consumption_limit_normal_price
        elif actual_price <= self.conf.price_limit_high_price:
            limit = self.conf.consumption_limit_high_price
        elif actual_price <= self.conf.price_limit_extreme_high_price:
            limit = self.conf.consumption_limit_extreme_high_price

        return limit


    def get_actual_electricity_price(self) -> float:
        ret_val = 0.36
        if self.conf.test_mode:
            testhelper = load_testhelper("./test_values.yaml")
            ret_val = testhelper.price_actual
            testhelper = None

        return ret_val

    def get_actual_consumption(self) -> float:
        ret_val = 80
        if self.conf.test_mode:
            testhelper = load_testhelper("./test_values.yaml")
            ret_val = testhelper.consumption_actual
            testhelper = None
        else:
            ret_val = self._get_consumption_from_db()

        return ret_val

    def get_actual_battery_soc(self) -> int:
        ret_val = 39
        if self.conf.test_mode:
            testhelper = load_testhelper("./test_values.yaml")
            ret_val = testhelper.battery_soc_actual
            testhelper = None
        else:
            ret_val = self._get_battery_soc_from_db()

        return ret_val

    def get_actual_production(self) -> float:
        ret_val = 412
        if self.conf.test_mode:
            testhelper = load_testhelper("./test_values.yaml")
            ret_val = testhelper.production_actual
            testhelper = None
        else:
            ret_val = self._get_production_balkon_from_db() if self.conf.use_small_as_limit else self._get_production_dach_from_db()

        return ret_val

    def get_actual_battery_state(self) -> str:
        ret_val = "standby"
        state = self._get_battery_state_from_db()
        if state == 12:
            ret_val = "laden"
        elif state == 13:
            ret_val = "entladen"

        return ret_val

    def _get_battery_soc_from_db(self) -> int:

        query = f"""
        from(bucket: "{self.conf.influxdb_bucket_hr}")
            |> range(start: -5m)
            |> filter(fn: (r) => r["measurement-type"] == "battery")
            |> filter(fn: (r) => r["_field"] == "percentFull")
            |> last()
        """
        result = self.influxdb_query_api.query(query=query)
        soc = 0
        for table in result:
            for record in table.records:
                measurement_type = record['measurement-type']
                if measurement_type == "battery":
                    soc = record.get_value()
        return soc

    def _get_battery_state_from_db(self) -> int:

        query = f"""
        from(bucket: "{self.conf.influxdb_bucket_hr}")
            |> range(start: -5m)
            |> filter(fn: (r) => r["measurement-type"] == "battery")
            |> filter(fn: (r) => r["_field"] == "led_status")
            |> last()
        """
        result = self.influxdb_query_api.query(query=query)
        state = 0
        for table in result:
            for record in table.records:
                measurement_type = record['measurement-type']
                if measurement_type == "battery":
                    state = record.get_value()
        return state

    def _get_consumption_from_db(self) -> float:

        query = f"""
        from(bucket: "vzlogger")
          |> range(start: -3m)
          |> filter(fn: (r) => r["_measurement"] == "vz_measurement")
          |> filter(fn: (r) => r["_field"] == "value")
          |> filter(fn: (r) => r["measurement"] == "leistung")
          |> aggregateWindow(every: 3m, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        """
        result = self.influxdb_query_api.query(query=query)
        consumption = 0
        for table in result:
            for record in table.records:
                measurement_type = record['measurement']
                if measurement_type == "leistung":
                    consumption = record.get_value()
        return consumption

    def _get_production_balkon_from_db(self) -> float:

        query = f"""
        from(bucket: "balkonkraftwerk")
          |> range(start: -3m)
          |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
          |> filter(fn: (r) => r["topic"] == "inverter/HM-800/ch0/P_AC")
          |> filter(fn: (r) => r["_field"] == "value")
          |> aggregateWindow(every: 3m, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        """
        result = self.influxdb_query_api.query(query=query)
        production = 0
        for table in result:
            for record in table.records:
                measurement_type = record['_measurement']
                if measurement_type == "mqtt_consumer":
                    production = record.get_value()
        return production

    def _get_production_dach_from_db(self) -> float:

        query = f"""
        from(bucket: "envoy_high")
          |> range(start: -3m)
          |> filter(fn: (r) => r["source"] == "power-meter")
          |> filter(fn: (r) => r["measurement-type"] == "production")
          |> filter(fn: (r) => r["_field"] == "P")
          |> aggregateWindow(every: 3m, fn: mean, createEmpty: false)
          |> group(columns: ["_time"], mode:"by")
          |> sum(column: "_value")
          |> group()
          |> yield(name: "mean_dach")
        """
        result = self.influxdb_query_api.query(query=query)
        production = 0
        for table in result:
            for record in table.records:
                measurement_type = record['result']
                if measurement_type == "mean_dach":
                    production = record.get_value()
        return production

    def set_heatpump_state(self, new_state: SGReadyStates):
        actual_state = self.waermepumpe.getState()
        self.logging.info(f"actual state: {actual_state}")
        self.logging.info(f"new state: {new_state}")

        if not self.conf.test_mode and actual_state != new_state:
            self.waermepumpe.setState(new_state)

    def is_enough_for_force(self, actual_price, actual_consumption, actual_battery_soc, actual_production) -> bool:
        ret_val = False

        consumption_limit_high = self.get_actual_consumption_limit(actual_price + self.conf.price_limit_force_state_dif)
        battery_soc_limit_high = self.get_actual_battery_soc_limit(actual_price + self.conf.price_limit_force_state_dif)
        production_limit_high = self.get_actual_production_limit(actual_price + self.conf.price_limit_force_state_dif)

        if (self.hyst_consumption_high.test(value=actual_consumption,
                                       upper_bound=consumption_limit_high + self.conf.consumption_hysteresis,
                                       lower_bound=consumption_limit_high) and
                self.hyst_battery_high.test(value=actual_battery_soc, upper_bound=battery_soc_limit_high,
                                       lower_bound=battery_soc_limit_high - self.conf.battery_hysteresis) and
                actual_production >= production_limit_high):
            ret_val = True


        return ret_val

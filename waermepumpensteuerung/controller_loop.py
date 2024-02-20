from datetime import datetime, date

import time

from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from waermepumpensteuerung.config import Config
from waermepumpensteuerung.simple_hysteresis import SimpleHysteresis
from waermepumpensteuerung.test_helper import load_testhelper

class ControllerLoop:

    def __init__(self, cfg: Config, logging, waermepumpe) -> None:
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

        self.hyst_battery = SimpleHysteresis(upper_bound=self.get_actual_battery_soc_limit(), lower_bound=self.get_actual_battery_soc_limit() - self.conf.battery_hysteresis)
        self.hyst_consumption = SimpleHysteresis(upper_bound=self.get_actual_consumption_limit() + self.conf.consumption_hysteresis, lower_bound=self.get_actual_consumption_limit(), direction='down')


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
        production_limit = self.get_actual_production_limit()
        battery_soc_limit = self.get_actual_battery_soc_limit()
        consumption_limit = self.get_actual_consumption_limit()
        self.logging.info(f"actual price = {self.get_actual_electricity_price()}")
        self.logging.info(f"actual production limit = {production_limit}")
        self.logging.info(f"actual battery_soc limit = {battery_soc_limit}")
        self.logging.info(f"actual consumption limit = {consumption_limit}")


        actual_production = self.get_actual_production()
        actual_battery_soc = self.get_actual_battery_soc()
        actual_consumption = self.get_actual_consumption()
        self.logging.info(f"actual production = {actual_production}")
        self.logging.info(f"actual battery_soc = {actual_battery_soc}")
        self.logging.info(f"actual consumption = {actual_consumption}")

        self.logging.info(f"{self.waermepumpe.getState()}")

        if (self.hyst_consumption.test(value=actual_consumption,
                                      upper_bound=consumption_limit + self.conf.consumption_hysteresis,
                                      lower_bound=consumption_limit) and
                self.hyst_battery.test(value=actual_battery_soc, upper_bound=battery_soc_limit,
                                       lower_bound=battery_soc_limit - self.conf.battery_hysteresis) and
                actual_production >= production_limit):
            self.logging.info(f"new state Go")
        else:
            self.logging.info(f"new state Normal")



    def get_actual_production_limit(self) -> int:
        actual_price = self.get_actual_electricity_price()
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


    def get_actual_battery_soc_limit(self) -> int:
        actual_price = self.get_actual_electricity_price()
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

    def get_actual_consumption_limit(self) -> int:
        actual_price = self.get_actual_electricity_price()
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

    def get_actual_consumption(self) -> int:
        ret_val = 80
        if self.conf.test_mode:
            testhelper = load_testhelper("./test_values.yaml")
            ret_val = testhelper.consumption_actual
            testhelper = None

        return ret_val

    def get_actual_battery_soc(self) -> int:
        ret_val = 39
        if self.conf.test_mode:
            testhelper = load_testhelper("./test_values.yaml")
            ret_val = testhelper.battery_soc_actual
            testhelper = None

        return ret_val

    def get_actual_production(self) -> int:
        ret_val = 412
        if self.conf.test_mode:
            testhelper = load_testhelper("./test_values.yaml")
            ret_val = testhelper.production_actual
            testhelper = None

        return ret_val


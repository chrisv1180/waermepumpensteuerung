from datetime import datetime, date

import time

from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from waermepumpensteuerung.config import Config

class ControllerLoop:

    def __init__(self, cfg: Config, logging) -> None:
        self.logging = logging
        self.cfg = cfg

        self.interval = self.cfg.heatpump_interval  # seconds

        influxdb_client = InfluxDBClient(
            url=cfg.influxdb_url,
            token=cfg.influxdb_token,
            org=cfg.influxdb_org
        )
        self.influxdb_write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
        self.influxdb_query_api = influxdb_client.query_api()

        # Used to track the transition to the next day for daily measurements
        self.todays_date = date.today()


    def run(self):
        error_count = 0
        while True:
            try:
                production_limit = self.get_actual_production_limit()
                battery_soc_limit = self.get_actual_battery_soc_limit()
                consumption_limit = self.get_actual_consumption_limit()
                self.logging.info(f"actual production limit = {production_limit}")
                self.logging.info(f"actual battery_soc limit = {battery_soc_limit}")
                self.logging.info(f"actual consumption limit = {consumption_limit}")
                time.sleep(self.interval)
            except :
                error_count += 1
                self.logging.warning("Error (%d/10)", error_count)
                if error_count >= 10:
                    # Give up after a while
                    raise
                pass


    def get_actual_production_limit(self) -> int:
        actual_price = self.get_actual_electricity_price()
        limit = 5000

        if actual_price <= self.cfg.price_limit_extreme_low_price:
            limit = self.cfg.production_limit_small_extreme_low_price if self.cfg.use_small_as_limit else self.cfg.production_limit_extreme_low_price
        elif actual_price <= self.cfg.price_limit_low_price:
            limit = self.cfg.production_limit_small_low_price if self.cfg.use_small_as_limit else self.cfg.production_limit_low_price
        elif actual_price <= self.cfg.price_limit_normal_price:
            limit = self.cfg.production_limit_small_normal_price if self.cfg.use_small_as_limit else self.cfg.production_limit_normal_price
        elif actual_price <= self.cfg.price_limit_high_price:
            limit = self.cfg.production_limit_small_high_price if self.cfg.use_small_as_limit else self.cfg.production_limit_high_price
        elif actual_price <= self.cfg.price_limit_extreme_high_price:
            limit = self.cfg.production_limit_small_extreme_high_price if self.cfg.use_small_as_limit else self.cfg.production_limit_extreme_high_price

        return limit


    def get_actual_battery_soc_limit(self) -> int:
        actual_price = self.get_actual_electricity_price()
        soc = 100

        if actual_price <= self.cfg.price_limit_extreme_low_price:
            soc = self.cfg.battery_soc_extreme_low_price
        elif actual_price <= self.cfg.price_limit_low_price:
            soc = self.cfg.battery_soc_low_price
        elif actual_price <= self.cfg.price_limit_normal_price:
            soc = self.cfg.battery_soc_normal_price
        elif actual_price <= self.cfg.price_limit_high_price:
            soc = self.cfg.battery_soc_high_price
        elif actual_price <= self.cfg.price_limit_extreme_high_price:
            soc = self.cfg.battery_soc_extreme_high_price

        return soc

    def get_actual_consumption_limit(self) -> int:

        return self.cfg.consumption_limit


    def get_actual_electricity_price(self) -> float:

        return 0.36

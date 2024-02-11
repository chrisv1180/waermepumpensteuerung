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
                self.logging.info("loop start")
                time.sleep(self.interval)
            except :
                error_count += 1
                self.logging.warning("Error (%d/10)", error_count)
                if error_count >= 10:
                    # Give up after a while
                    raise
                pass

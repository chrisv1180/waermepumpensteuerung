import logging
import sys

import yaml

LOG = logging.getLogger("cfg")

class Config:
    def __init__(self, data) -> None:
        try:
            self.heatpump_interval = data['heatpump'].get('interval', 60)  # type: int

            self.influxdb_url = data['influxdb']['url']  # type: str
            self.influxdb_token = data['influxdb']['token']  # type: str
            self.influxdb_org = data['influxdb'].get('org', 'home')  # type: str

            bucket = data['influxdb'].get('bucket', None)
            bucket_lr = data['influxdb'].get('bucket_lr', None)
            bucket_hr = data['influxdb'].get('bucket_hr', None)
            bucket_mr = data['influxdb'].get('bucket_mr', None)
            self.influxdb_bucket_lr = bucket_lr or bucket
            self.influxdb_bucket_mr = bucket_mr or bucket
            self.influxdb_bucket_hr = bucket_hr or bucket

            self.production_limit_extreme_low_price = data['heatpump']['production_limit'].get('extreme_low_price', 500)  # type: int
            self.production_limit_low_price = data['heatpump']['production_limit'].get('low_price', 1000)  # type: int
            self.production_limit_normal_price = data['heatpump']['production_limit'].get('normal_price', 2000)  # type: int
            self.production_limit_high_price = data['heatpump']['production_limit'].get('high_price', 3000)  # type: int
            self.production_limit_extreme_high_price = data['heatpump']['production_limit'].get('extreme_high_price', 4000)  # type: int

            self.production_limit_small_extreme_low_price = data['heatpump']['production_limit_small'].get('extreme_low_price', 100)  # type: int
            self.production_limit_small_low_price = data['heatpump']['production_limit_small'].get('low_price', 200)  # type: int
            self.production_limit_small_normal_price = data['heatpump']['production_limit_small'].get('normal_price', 400)  # type: int
            self.production_limit_small_high_price = data['heatpump']['production_limit_small'].get('high_price', 500)  # type: int
            self.production_limit_small_extreme_high_price = data['heatpump']['production_limit_small'].get('extreme_high_price', 600)  # type: int

            self.price_limit_extreme_low_price = data['heatpump']['price_limit'].get('extreme_low_price', 0.2)  # type: float
            self.price_limit_low_price = data['heatpump']['price_limit'].get('low_price', 0.25)  # type: float
            self.price_limit_normal_price = data['heatpump']['price_limit'].get('normal_price', 0.3)  # type: float
            self.price_limit_high_price = data['heatpump']['price_limit'].get('high_price', 0.4)  # type: float
            self.price_limit_extreme_high_price = data['heatpump']['price_limit'].get('extreme_high_price', 0.45)  # type: float

            self.use_small_as_limit = data['heatpump'].get('use_small_as_limit', False)  # type: bool

            self.battery_soc_extreme_low_price = data['heatpump']['battery_soc_limit'].get('extreme_low_price', 10)  # type: int
            self.battery_soc_low_price = data['heatpump']['battery_soc_limit'].get('low_price', 20)  # type: int
            self.battery_soc_normal_price = data['heatpump']['battery_soc_limit'].get('normal_price', 25)  # type: int
            self.battery_soc_high_price = data['heatpump']['battery_soc_limit'].get('high_price', 60)  # type: int
            self.battery_soc_extreme_high_price = data['heatpump']['battery_soc_limit'].get('extreme_high_price', 100)  # type: int
            self.battery_hysteresis = data['heatpump']['battery_soc_limit'].get('hysteresis', 10)  # type: int

            self.consumption_limit_extreme_low_price = data['heatpump']['consumption_limit'].get('extreme_low_price', 300)  # type: int
            self.consumption_limit_low_price = data['heatpump']['consumption_limit'].get('low_price', 200)  # type: int
            self.consumption_limit_normal_price = data['heatpump']['consumption_limit'].get('normal_price', 100)  # type: int
            self.consumption_limit_high_price = data['heatpump']['consumption_limit'].get('high_price', 50)  # type: int
            self.consumption_limit_extreme_high_price = data['heatpump']['consumption_limit'].get('extreme_high_price', 10)  # type: int
            self.consumption_hysteresis = data['heatpump']['consumption_limit'].get('hysteresis', 100)  # type: int

            self.test_mode = data['heatpump'].get('testmode', False)  # type: bool





        except KeyError as e:
            LOG.error("Missing required config key: %s", e.args[0])
            sys.exit(1)


def load_config(path: str):
    LOG.info("Loading config: %s", path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)

    return Config(data)

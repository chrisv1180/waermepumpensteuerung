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

            self.price_limit_extreme_low_price = data['heatpump']['price_limit'].get('extreme_low_price', 0.2)  # type: float
            self.price_limit_low_price = data['heatpump']['price_limit'].get('low_price', 0.25)  # type: float
            self.price_limit_normal_price = data['heatpump']['price_limit'].get('normal_price', 0.3)  # type: float
            self.price_limit_high_price = data['heatpump']['price_limit'].get('high_price', 0.4)  # type: float
            self.price_limit_extreme_high_price = data['heatpump']['price_limit'].get('extreme_high_price', 0.45)  # type: float





        except KeyError as e:
            LOG.error("Missing required config key: %s", e.args[0])
            sys.exit(1)


def load_config(path: str):
    LOG.info("Loading config: %s", path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)

    return Config(data)

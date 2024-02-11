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




        except KeyError as e:
            LOG.error("Missing required config key: %s", e.args[0])
            sys.exit(1)


def load_config(path: str):
    LOG.info("Loading config: %s", path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)

    return Config(data)

import logging
import sys

import yaml

LOG = logging.getLogger("cfg")

class TestHelper:
    def __init__(self, data) -> None:
        try:

            self.consumption_actual = data['heatpump_test'].get('consumption_actual', 100)  # type: int
            self.production_actual = data['heatpump_test'].get('production_actual', 2000)  # type: int
            self.battery_soc_actual = data['heatpump_test'].get('battery_soc_actual', 50)  # type: int
            self.price_actual = data['heatpump_test'].get('price_actual', 0.36)  # type: float


        except KeyError as e:
            LOG.error("Missing required config key: %s", e.args[0])
            sys.exit(1)


def load_testhelper(path: str):
    LOG.info("Loading TestHelper: %s", path)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.load(f.read(), Loader=yaml.FullLoader)

    return TestHelper(data)
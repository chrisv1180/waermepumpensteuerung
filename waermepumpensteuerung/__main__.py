import logging
import argparse
import time
import ShellyPy
from waermepumpensteuerung.config import load_config
from shelly2sgready.sgready import SGReadyControl, SGReadyStates

from waermepumpensteuerung.controller_loop import ControllerLoop


parser = argparse.ArgumentParser()
parser.add_argument("cfg_path")
args = parser.parse_args()

conf = load_config(args.cfg_path)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s]: %(message)s"
)


while True:
    # Loop forever so that if an exception occurs, controller will restart
    try:
        waermepumpe = SGReadyControl(path_to_config=args.cfg_path)
        logging.info(waermepumpe.shelly_state_2_3.relay(0))
        logging.info(waermepumpe.shelly_optional.relay(0))
        logging.info(waermepumpe.getState())

        S = ControllerLoop(conf, logging, waermepumpe)

        S.run()
    except Exception as e:
        logging.error("%s: %s", str(type(e)), e)

        # sleep 5 minutes to recover
        time.sleep(300)
        logging.info("Restarting waermepumpensteuerung")
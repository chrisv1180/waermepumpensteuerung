import logging
import argparse
import time
import ShellyPy
from waermepumpensteuerung.config import load_config
from shelly2sgready.sgready import SGReadyControl, SGReadyStates

from waermepumpensteuerung.controller_loop import ControllerLoop


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cfg_path")
    args = parser.parse_args()

    conf = load_config(args.cfg_path)


    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s]: %(message)s"
    )

    # if conf.shelly_state_2_3_user is not None and conf.shelly_state_2_3_pw is not None:
    #     shelly_plug = ShellyPy.Shelly(conf.shelly_state_2_3_ip, conf.shelly_state_2_3_port,
    #                                             login={"username": conf.shelly_state_2_3_user,
    #                                                    "password": conf.shelly_state_2_3_pw})
    # else:
    #     shelly_plug = ShellyPy.Shelly(conf.shelly_state_2_3_ip, conf.shelly_state_2_3_port)
    #
    # # shelly_plug.relay(conf.shelly_state_2_3_relay, turn=True, timer=3)
    # shelly_plug.relay(conf.shelly_state_2_3_relay, turn=True)
    #
    # status = shelly_plug.relay(conf.shelly_state_2_3_relay)
    # print(status["output"])

    # waermepumpe = SGReadyControl(path_to_config=args.cfg_path)
    # #waermepumpe.setState(SGReadyStates.state2_normal)
    # print(waermepumpe.shelly_state_2_3.relay(0))
    # print(waermepumpe.shelly_optional.relay(0))
    # print(waermepumpe.getState())

    while True:
        # Loop forever so that if an exception occurs, controller will restart
        try:
            waermepumpe = SGReadyControl(path_to_config=args.cfg_path)
            logging.info(waermepumpe.shelly_state_2_3.relay(0))
            logging.info(waermepumpe.shelly_optional.relay(0))
            logging.info(waermepumpe.getState())

            S = ControllerLoop(conf, logging)

            S.run()
        except Exception as e:
            logging.error("%s: %s", str(type(e)), e)

            # sleep 5 minutes to recover
            time.sleep(300)
            logging.info("Restarting waermepumpensteuerung")


if __name__ == '__main__':
    main()

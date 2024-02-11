import logging
import argparse
import ShellyPy
from shelly2sgready.config import load_config
from shelly2sgready.sgready import SGReadyControl, SGReadyStates

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

    waermepumpe = SGReadyControl(path_to_config=args.cfg_path)
    #waermepumpe.setState(SGReadyStates.state2_normal)
    print(waermepumpe.shelly_state_2_3.relay(0))
    print(waermepumpe.shelly_optional.relay(0))
    print(waermepumpe.getState())


if __name__ == '__main__':
    main()

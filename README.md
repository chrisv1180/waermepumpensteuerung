# waermepumpensteuerung
A heatpump controller for SGReady controlled heatpumps.
Needs the production, consumption and battery state values stored in a InfluxDB. 

## Dependencies
This project uses [shelly2sgready](https://github.com/chrisv1180/shelly2sgready) in version 0.1.2 to send SGReady states to the heatpump.

For reading values from InfluxDB [influxdb-client](https://github.com/influxdata/influxdb-client-python) is used.

For configuring the wrapper [PyYAML](https://github.com/yaml/pyyaml) is used.

## Example
### Config file
config.yaml
```yaml
# Config file

# configuration for switching sgready device with one or two Shelly devices
shelly2sgready:
  use_all_4_states: true      # if true also set shelly_optional_states

  shelly_state_2_3:
    ip: 192.168.xxx.xx          # required
    port: 80                    # optional
    relay: 0                    # optional
    #username: admin             # optional
    #password: geheim            # optional

  # this shelly is optional; set use_all_4_states: false if second shelly is not used
  shelly_optional_states:
    ip: 192.168.xxx.xx          # required
    port: 80                    # optional
    relay: 0                    # optional
    #username: admin             # optional
    #password: geheim            # optional

# heatpump specific settings
heatpump:                       # optional
  testmode: false
  interval: 60
  use_small_as_limit: false

  production_limit:
    extreme_low_price: 500
    low_price: 1000
    normal_price: 2000
    high_price: 3000
    extreme_high_price: 4000
    hysteresis: 500

  production_limit_small:
    extreme_low_price: 100
    low_price: 200
    normal_price: 400
    high_price: 500
    extreme_high_price: 600
    hysteresis: 50

  price_limit:
    extreme_low_price: 0.20
    low_price: 0.25
    normal_price: 0.36
    high_price: 0.40
    extreme_high_price: 0.45
    force_state_dif: 0.02

  consumption_limit:
    extreme_low_price: 300
    low_price: 200
    normal_price: 100
    high_price: 50
    extreme_high_price: 10
    hysteresis: 100

  battery_soc_limit:
    extreme_low_price: 10
    low_price: 20
    normal_price: 25
    high_price: 60
    extreme_high_price: 100
    hysteresis: 10

# How to access InfluxDB
influxdb:
  url:
  token:
  org: home

  # Which InfluxDB bucket to send measurements.
  # This can be useful to control different data-retention rules
  # alternatively use the "bucket" key if you want everything to be sent to the
  # same bucket
  # bucket_hr:  # high resulution
  # bucket_lr:  # low resolution
  # bucket_mr:  # medium resolution
  bucket: all_data
```

### Usage

config.yaml, Dockerfile and docker-compose.yaml have to be in same directory. Then run 'docker-compose up --build -d'

#### Dockerfile
```dockerfile
FROM python:3.11-slim-bookworm

ADD https://raw.githubusercontent.com/chrisv1180/waermepumpensteuerung/main/launcher.sh /
RUN chmod +x /launcher.sh

# Install Stuff
RUN apt update
RUN apt -y install git

ENV WAERMEPUMPENSTEUERUNG_CFG_PATH=/etc/waermepumpensteuerung/config.yaml

# entrypoint
CMD /launcher.sh
```

#### docker-compose.yaml
```yaml
# Docker compose file

version: "3"

services:
  waermepumpensteuerung:
    build: .
    restart: unless-stopped
    environment:
      - WAERMEPUMPENSTEUERUNG_CFG_PATH=/etc/waermepumpensteuerung/config_real.yaml
    volumes:
      - ./:/etc/waermepumpensteuerung:rw
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
    network_mode: bridge
```

## License
This project is licensed under the [MIT License](LICENSE)  
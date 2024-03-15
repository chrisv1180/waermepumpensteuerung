#!/bin/sh
set -e

echo "Installing"
python3 -m pip install --force-reinstall git+https://github.com/chrisv1180/waermepumpensteuerung

echo "Starting waermepumpensteuerung"
python3 -m waermepumpensteuerung $WAERMEPUMPENSTEUERUNG_CFG_PATH

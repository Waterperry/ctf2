#!/bin/sh
set -eux;
env;

cd /root/server;
pypi-server run -p "$PYPI_PORT" -P . -a . /root/server/packages &

sleep 2;
cd /root;
./loop.sh

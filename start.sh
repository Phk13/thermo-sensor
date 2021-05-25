#!/bin/sh
nohup gunicorn -w 2 --threads 4 --pid server.pid -b 0.0.0.0:5002 thermo_sensor:app &
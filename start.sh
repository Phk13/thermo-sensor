#!/bin/sh
nohup uvicorn --workers 2 --host 0.0.0.0 --port 5002 main:app &
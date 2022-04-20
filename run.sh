#!/bin/bash

mkdir -p logs
cd /home/sergio/scripts/cotizacion_dolar/
. ./env/bin/activate
/home/sergio/scripts/cotizacion_dolar/env/bin/python3 /home/sergio/scripts/cotizacion_dolar/main.py >> logs/dolar-"`date +"%Y-%m-%d_%H.%M.%S"`".log 2>&1
deactivate

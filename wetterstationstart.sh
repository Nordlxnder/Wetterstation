#!/bin/bash

python /home/golfo/Wetterstation/wetterserver.py
echo "Start der Wetterstation: $(date)" >> /var/log/wetterstation.log

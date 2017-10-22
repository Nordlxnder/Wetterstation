#!/bin/bash

python /Wetterstation/wetterserver.py
echo "Start der Wetterstation: $(date)" >> /var/log/wetterstation.log

#!/bin/bash

python /Wetterstation/stop_wetterstation.py >> /var/log/wetterstation.log
echo "Stopp der Wetterstation: $(date)" >> /var/log/wetterstation.log

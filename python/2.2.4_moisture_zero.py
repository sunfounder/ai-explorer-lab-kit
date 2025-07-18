#!/usr/bin/env python3
from fusion_hat import ADC
import time

# Set up the soil moisture sensor
moisture = ADC('A1')

try:
    while True:
        # Get the current reading from the ADC port
        result = moisture.read()
        print('result = %d ' %result)

        # Wait for 1 seconds before reading again
        time.sleep(0.2)

# Graceful exit when 'Ctrl+C' is pressed
except KeyboardInterrupt: 
    pass

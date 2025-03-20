#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fusion_hat import ADC
import time
import math

thermistor = ADC('A3')

# Run the process in a try-except block
try:
    while True:
        # Read the voltage from the sensor
        Vr = thermistor.read_voltage()
        # Calculate the resistance of the thermistor
        if 3.3 - Vr < 0.1:
            print("Please check the sensor")
            continue
        else:
            Rt = 10000 * Vr / (3.3 - Vr)
            # Calculate the temperature in Kelvin
            temp = 1 / (((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
            # Convert Kelvin to Celsius
            Cel = temp - 273.15
            # Convert Celsius to Fahrenheit
            Fah = Cel * 1.8 + 32
            # Print the temperature in both Celsius and Fahrenheit
            print('Celsius: %.2f C  Fahrenheit: %.2f F' % (Cel, Fah))
            # Wait for 0.2 seconds before the next read
            time.sleep(0.2)

# Handle KeyboardInterrupt for graceful termination
except KeyboardInterrupt:
    pass

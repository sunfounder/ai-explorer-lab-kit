#!/usr/bin/env python3

from fusion_hat import ADC, PWM
import time

# Initialize a PWM LED on GPIO pin 22
led = PWM('P0')

# Set up the potentiometer
photoresistor = ADC('A0')

def MAP(x, in_min, in_max, out_min, out_max):
    """
    Map a value from one range to another.
    :param x: The value to be mapped.
    :param in_min: The lower bound of the value's current range.
    :param in_max: The upper bound of the value's current range.
    :param out_min: The lower bound of the value's target range.
    :param out_max: The upper bound of the value's target range.
    :return: The mapped value.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

try:
    while True:
        # Get the current reading from the ADC port
        result = photoresistor.read()
        print('result = %d ' %result)

        # Map the ADC value to a range suitable for setting LED brightness
        value = MAP(result, 0, 4095, 0, 100)

        # Set the LED brightness
        led.pulse_width_percent(value)

        # Wait for 1 seconds before reading again
        time.sleep(0.2)

# Graceful exit when 'Ctrl+C' is pressed
except KeyboardInterrupt: 
    led.pulse_width_percent(0)  # Turn off the LED

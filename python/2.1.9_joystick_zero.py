#!/usr/bin/env python3
from fusion_hat import Pin,ADC
import time

# Initialize the Joystick
BtnPin = Pin(17, Pin.IN, Pin.PULL_UP)
xAxis = ADC('A1')
yAxis = ADC('A0')

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
    # Main loop to read and print ADC values and button state
    while True:
        # Read X and Y values from ADC channels
        x_val = MAP(xAxis.read(),0,4095,-100,100)
        y_val = MAP(yAxis.read(),0,4095,-100,100)

        # Read the state of the button (pressed or not)
        Btn_val = BtnPin.value()

        # Print the X, Y, and button values
        print('X: %d  Y: %d  Btn: %d' % (x_val, y_val, Btn_val))

        # Delay of 0.2 seconds before the next read
        time.sleep(0.2)

# Gracefully handle script termination (e.g., via KeyboardInterrupt)
except KeyboardInterrupt: 
    pass

#!/usr/bin/env python3
from fusion_hat import Pin,ADC
from time import sleep

# Define GPIO pins where LEDs are connected
led_pins = [4, 17, 27, 22, 23, 24, 25, 5, 13, 26]

# Create LED objects for each pin
leds = [Pin(pin, Pin.OUT) for pin in led_pins]

# Set up the detection pin for the battery
btr = ADC('A0')


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


def LedBarGraph(value):
    # Turn off all LEDs
    for i in range(10):
        leds[i].off()
    # Turn on LEDs up to the specified value
    for i in range(value):
        leds[i].on()

try:
    # Main loop to continuously update LED bar graph
    while True:
        # Read voltage value 
        voltage = btr.read_voltage()
        print('voltage = %.2f' %(voltage))

        # Convert analog value to LED bar graph level
        LedBarGraph(int(MAP(voltage, 0, 3.3, 0, 10)))
        sleep(0.5)
        
except KeyboardInterrupt: 
    # Turn off all LEDs when program is interrupted
    for i in range(10):
        leds[i].off()

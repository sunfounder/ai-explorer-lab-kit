#!/usr/bin/env python3
from fusion_hat import Pin
from signal import pause  # Import pause function from signal module

TiltPin = Pin(17,Pin.IN, pull=Pin.PULL_DOWN)  # Tilt sensor connected to GPIO pin 17
green_led = Pin(27, Pin.OUT)  # Green LED connected to GPIO pin 27
red_led = Pin(22, Pin.OUT)   # Red LED connected to GPIO pin 22

def detect():
    """
    Detect the tilt sensor state and control the LEDs.
    Turns on the red LED and turns off the green LED when tilted.
    Turns off the red LED and turns on the green LED when not tilted.
    """
    if TiltPin.value() == 1:  # Check if the sensor is tilted
        print('    *************')
        print('    *   Tilt!   *')
        print('    *************')
        red_led.high()   # Turn on red LED
        green_led.low()  # Turn off green LED
    else:  # If the sensor is not tilted
        red_led.low()  # Turn off red LED
        green_led.high()  # Turn on green LED

try:
    # Set up a callback to detect changes in the tilt sensor state
    TiltPin.when_activated = detect 
    TiltPin.when_deactivated = detect  
    pause()

except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to exit the loop gracefully
    pass

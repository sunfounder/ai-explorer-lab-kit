#!/usr/bin/env python3
from fusion_hat import Pin
from signal import pause  # Import pause function from signal module

# Initialize the reed sensor
reed_switch = Pin(17,Pin.IN, pull=Pin.PULL_UP)  # reed sensor connected to GPIO pin 17, pull-up resistor disabled
green_led = Pin(27, Pin.OUT)  # Green LED connected to GPIO pin 27
red_led = Pin(22, Pin.OUT)   # Red LED connected to GPIO pin 22

def detect():
    if reed_switch.value() == 0:  # Check if the sensor is actived
        red_led.high()   # Turn on red LED
        green_led.low()  # Turn off green LED
    else:  # If the sensor is not actived
        red_led.low()  # Turn off red LED
        green_led.high()  # Turn on green LED

try:
    green_led.high() # Turn on green LED initially
    reed_switch.when_activated = detect  # Set up an interrupt to detect changes in the reed sensor state
    reed_switch.when_deactivated = detect  # Set up an interrupt to detect changes in the reed sensor state

    # Run an event loop that waits for button events and keeps the script running
    print("CTRL + C to exit")
    pause()


except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to exit the loop gracefully
    pass

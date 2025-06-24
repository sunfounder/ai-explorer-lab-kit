#!/usr/bin/env python3

from fusion_hat import Pin
from time import sleep

# Define GPIO pins where LEDs are connected
led_pins = [4, 17, 27, 22, 23, 24, 25, 5, 13, 26]

# Create LED objects for each pin
leds = [Pin(pin, Pin.OUT) for pin in led_pins]

def all_led_bar_graph():
    # Sequentially light up all LEDs one by one
    for led in leds:
        led.high()       # Turn on LED
        sleep(0.3)     # Delay for visual effect
        led.low()      # Turn off LED

def turn_off_all_leds():
    # Turn off all LEDs at once
    for led in leds:
        led.low()

try:
    # Main loop to cycle through LED patterns
    while True:
        all_led_bar_graph()   # Activate all LEDs
        sleep(0.3)            # Pause before restarting

except KeyboardInterrupt:
    # Handle interruption (Ctrl+C) gracefully
    turn_off_all_leds()      # Ensure all LEDs are turned off on exit
    pass

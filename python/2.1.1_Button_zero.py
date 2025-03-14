#!/usr/bin/env python3
from fusion_hat import Pin  
from signal import pause  # Import pause function from signal module

# Initialize an LED object on GPIO pin 22
led = Pin(22,Pin.OUT)
# Initialize a Button object on GPIO pin 17
button = Pin(17, Pin.IN, pull= Pin.PULL_DOWN)

# # Link the button's "when_activated" event to the LED's high() method
button.when_activated = led.high

# # Link the button's "when_deactivated" event to the LED's low() method
button.when_deactivated = led.low



# Run an event loop that waits for button events and keeps the script running
print("CTRL + C to exit")
pause()

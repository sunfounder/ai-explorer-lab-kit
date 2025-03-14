#!/usr/bin/env python3
from fusion_hat import Pin  
from signal import pause  # Import pause function from signal module

# Initialize a PIR Module object on GPIO pin 17
pir = Pin(17, Pin.IN, pull= Pin.PULL_DOWN)

def detect():
    if pir.value() == 1:  # Check if the PIR Module is triggered
        print("Detected Barrier!")
    else:
        print("No Barrier")

try:
    pir.when_activated = detect  # Set up an interrupt to detect changes in the pir sensor state
    pir.when_deactivated = detect  

    # Run an event loop that waits for button events and keeps the script running
    print("CTRL + C to exit")
    pause()


except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to exit the loop gracefully
    pass



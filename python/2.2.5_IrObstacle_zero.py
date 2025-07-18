#!/usr/bin/env python3
from fusion_hat import Pin 
from signal import pause  # Import pause function from signal module

# Initialize a IR Obstacle Module object on GPIO pin 17
IR_Obstacle = Pin(17, Pin.IN, pull= Pin.PULL_UP)

def detect():
    if IR_Obstacle.value() == 1:  # Check if the IR Obstacle Module is activated
        print("Detected Barrier!")
    else:
        print("No Barrier")

try:
    IR_Obstacle.when_activated = detect  # Set up an interrupt to detect changes in the reed sensor state
    IR_Obstacle.when_deactivated = detect
    
    # Run an event loop that waits for button events and keeps the script running
    print("CTRL + C to exit")
    pause()


except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to exit the loop gracefully
    pass



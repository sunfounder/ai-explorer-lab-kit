#!/usr/bin/env python3
from fusion_hat import Pin 
from time import sleep  # Import sleep for delay

# Initialize slider (Button) on GPIO pin 17
slider = Pin(17, Pin.IN, pull = Pin.PULL_DOWN) 

# Initialize LED1 connected to GPIO pin 22
led1 = Pin(22,Pin.OUT)
# Initialize LED2 connected to GPIO pin 27
led2 = Pin(27,Pin.OUT)

try:
    # Continuously monitor the state of the slider and control LEDs accordingly
    while True:
        if slider.value() == 1:  # Check if the slider is pressed
            led1.off()  # Turn off LED1
            led2.on()   # Turn on LED2
        else:  # If the sensor is not pressed
            led1.on()   # Turn on LED1
            led2.off()  # Turn off LED2

        sleep(0.5)  # Pause for 0.5 seconds before rechecking the sensor state

except KeyboardInterrupt:
    # Handle a keyboard interrupt (Ctrl+C) for a clean exit from the loop
    pass

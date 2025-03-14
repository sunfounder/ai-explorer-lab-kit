#!/usr/bin/env python3
from fusion_hat import Pin  
from time import sleep  # Import sleep function for delays

# Initialize micro switch on GPIO pin 17
micro_switch = Pin(17, Pin.IN, pull = Pin.PULL_DOWN)
# Initialize LED1 connected to GPIO pin 22
led1 = Pin(22,Pin.OUT)
# Initialize LED2 connected to GPIO pin 27
led2 = Pin(27,Pin.OUT)

try:
    # Continuously check the state of the micro switch and control LEDs accordingly
    while True:
        if micro_switch.value() == 1:  # If the micro switch is pressed
            led1.high()       # Turn on LED1
            led2.low()      # Turn off LED2
        else:  # If the micro switch is not pressed
            led1.low()      # Turn off LED1
            led2.high()       # Turn on LED2

        sleep(0.5)  # Pause for 0.5 seconds before checking the switch again

except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to exit the loop gracefully
    pass

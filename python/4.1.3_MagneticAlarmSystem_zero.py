#!/usr/bin/env python3
from fusion_hat import Pin, Buzzer
import time

# Initialize the buzzer on GPIO pin 27
buzzer = Buzzer(Pin(27))
# Initialize the reed switch on GPIO pin 17 with pull-up resistor enabled
reed_switch = Pin(17, Pin.IN, Pin.PULL_UP)

try:
    while True:
        # Check if the reed switch (the window) is closed
        if reed_switch.value() == 1:
            # Turn off the buzzer if reed switch (the window) closed
            buzzer.off()
        else:
            # If reed switch (the window) is not closed, beep the buzzer
            buzzer.on()
            time.sleep(0.1)  # Buzzer on for 0.1 seconds
            buzzer.off()
            time.sleep(0.1)  # Buzzer off for 0.1 seconds

except KeyboardInterrupt:
    # Turn off the buzzer when the program is interrupted (e.g., keyboard interrupt)
    buzzer.off()
    pass

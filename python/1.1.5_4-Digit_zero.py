#!/usr/bin/env python3
from fusion_hat import Pin
import time
import threading

# Define GPIO pins for the 74HC595 shift register
SDI = Pin(17,Pin.OUT)   # Serial Data Input
RCLK = Pin(4,Pin.OUT)  # Register Clock
SRCLK = Pin(27,Pin.OUT) # Shift Register Clock

# Define GPIO pins for digit selection on the 7-segment display
placePin = [Pin(pin,Pin.OUT) for pin in (23, 24, 25, 12)]

# Define segment codes for numbers 0-9 for the 7-segment display
number = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90)

counter = 0  # Initialize counter for display
timer1 = 0   # Initialize timer for counter increment

def clearDisplay():
    """ Clear the 7-segment display. """
    for _ in range(8):
        SDI.high()
        SRCLK.high()
        SRCLK.low()
    RCLK.high()
    RCLK.low()

def hc595_shift(data):
    """ Shift a byte of data to the 74HC595 shift register. """
    for i in range(8):
        SDI.value(0x80 & (data << i))  # Set SDI high/low based on data bit
        SRCLK.high()  # Pulse the Shift Register Clock
        SRCLK.low()
    RCLK.high()  # Latch data on the output by pulsing Register Clock
    RCLK.low()

def pickDigit(digit):
    """ Select a digit for display on the 7-segment display. """
    for pin in placePin:
        pin.low()  # Turn off all digit selection pins
    placePin[digit].high()  # Turn on the selected digit

def timer():
    """ Timer function to increment the counter every second. """
    global counter, timer1
    timer1 = threading.Timer(1.0, timer)  # Reset timer for next increment
    timer1.start()
    counter += 1  # Increment counter
    print("%d" % counter)  # Print current counter value

def setup():
    """ Setup initial state and start the timer. """
    global timer1
    timer1 = threading.Timer(1.0, timer)  # Initialize and start the timer
    timer1.start()

def loop():
    """ Main loop to update the 7-segment display with counter value. """
    global counter
    while True:
        for i in range(4):  # Loop through each digit
            clearDisplay()  # Clear display before setting new digit
            pickDigit(i)    # Select digit for display

            # Choose the digit of counter to display
            digit = (counter // (10 ** i)) % 10

            hc595_shift(number[digit])  # Shift digit value to 74HC595
            time.sleep(0.001)  # Short delay for display stability

def destroy():
    """ Cleanup GPIO resources and stop timer on exit. """
    global timer1
    timer1.cancel()  # Stop the timer
    for device in [SDI, RCLK, SRCLK] + placePin:
        device.close()  # Close GPIO devices

try:
    setup()  # Initialize the setup
    while True:
        loop()  # Start the main loop
        
except KeyboardInterrupt:
    # Handle script interruption (e.g., Ctrl+C)
    destroy()  # Cleanup resources on exit


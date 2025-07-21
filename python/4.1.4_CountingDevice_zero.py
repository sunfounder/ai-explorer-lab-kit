#!/usr/bin/env python3
from fusion_hat import Pin

# Initialize PIR motion sensor on GPIO 22
pir = Pin(22, Pin.IN, pull= Pin.PULL_DOWN)

# Define GPIO pins for the 74HC595 shift register
SDI = Pin(17,Pin.OUT)   # Serial Data Input
RCLK = Pin(4,Pin.OUT)  # Register Clock
SRCLK = Pin(27,Pin.OUT) # Shift Register Clock

# Define GPIO pins for digit selection on the 7-segment display
placePin = [Pin(pin,Pin.OUT) for pin in (23, 24, 25, 12)]

# Define digit codes for 7-segment display
number = (0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90)

# Counter for the displayed number
counter = 0

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


def display():
    # Updates the display with the current counter value
    global counter
    clearDisplay()
    pickDigit(3)
    hc595_shift(number[counter % 10])

    clearDisplay()
    pickDigit(2)
    hc595_shift(number[counter % 100//10])

    clearDisplay()
    pickDigit(1)
    hc595_shift(number[counter % 1000//100])

    clearDisplay()
    pickDigit(0)
    hc595_shift(number[counter % 10000//1000])

def loop():
    # Main loop to update display and check for motion
    global counter
    currentState = 0
    lastState = 0
    while True:
        display()
        currentState = 1 if pir.value()==1 else 0
        if currentState == 1 and lastState == 0:
            counter += 1
        lastState = currentState

try:
    loop()
except KeyboardInterrupt:
    # Turn off all pins when the script is interrupted
    SDI.low()
    SRCLK.low()
    RCLK.low()
    pass

#!/usr/bin/env python3
from fusion_hat import Pin,Buzzer,PWM
import time
import threading

# Initialize TonalBuzzer on PWM0
BeepPin = Buzzer(PWM('P0'))  # Update this pin number based on your setup

# Initialize LEDs on GPIO pins 22 and 27
ALedPin = Pin(22,Pin.OUT)
BLedPin = Pin(27,Pin.OUT)

# Initialize Button on GPIO pin 17
switchPin = Pin(17,Pin.IN, Pin.PULL_DOWN)

# Global flag to control the buzzer and LED states
flag = 0

def ledWork():
    """
    Control LED blinking pattern based on the flag state.
    When flag is set, alternately blink ALedPin and BLedPin.
    """
    while True:
        if flag:
            # Alternate blinking of LEDs
            ALedPin.on()
            time.sleep(0.5)
            ALedPin.off()
            BLedPin.on()
            time.sleep(0.5)
            BLedPin.off()
        else:
            # Turn off both LEDs if flag is not set
            ALedPin.off()
            BLedPin.off()

# Define the musical tune as a list of notes and their durations
tune = [
    ('C4', 0.1), ('E4', 0.1), ('G4', 0.1), 
    (None, 0.1), 
    ('E4', 0.1), ('G4', 0.1), ('C5', 0.1), 
    (None, 0.1), 
    ('C5', 0.1), ('G4', 0.1), ('E4', 0.1), 
    (None, 0.1), 
    ('G4', 0.1), ('E4', 0.1), ('C4', 0.1), 
    (None, 0.1)
]

def buzzerWork():
    """
    Play a tune using the buzzer based on the flag state.
    The tune is played only when the flag is set.
    """
    while True:
        for note, duration in tune:
            if flag == 0:
                break
            print(note)  # Output the current note to the console
            BeepPin.play(note,duration)  # Play the current note
        BeepPin.off()  # Stop the buzzer after playing the tune

def main():
    """
    Monitor button press to update the flag state.
    Sets the flag when the button is pressed.
    """
    global flag
    while True:
        flag = 1 if switchPin.value()==1 else 0


try:
    # Initialize and start threads for buzzer and LED control
    tBuzz = threading.Thread(target=buzzerWork)
    tBuzz.start()
    tLed = threading.Thread(target=ledWork)
    tLed.start()
    main()

except KeyboardInterrupt:
    # Stop the buzzer and turn off LEDs on program interruption
    BeepPin.off()
    ALedPin.off()    
    BLedPin.off()

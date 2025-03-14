#!/usr/bin/env python3

from fusion_hat import Pin,LCD1602,Keypad
from time import sleep
import random


# Game-related variables
count = 0
pointValue = 0
upper = 99
lower = 0

"""
Setup function for initializing the keypad and LCD display.
"""
global keypad, last_key_pressed, keys
# Configure rows, columns, and keypad layout
# pin from left to right - 4 17 27 22 23 24 25 12
rows_pins = [4, 17, 27, 22]
cols_pins = [23, 24, 25, 12]
keys = ["1", "2", "3", "A",
        "4", "5", "6", "B",
        "7", "8", "9", "C",
        "*", "0", "#", "D"]

# Create an instance of the Keypad class
keypad = Keypad(rows_pins, cols_pins, keys)
last_key_pressed = []

lcd = LCD1602(address=0x27, backlight=1)
lcd.clear()
lcd.write(0, 0, 'Welcome!')
lcd.write(0, 1, 'Press A to Start!')

def init_new_value():
    """
    Initialize a new target value and reset game parameters.
    """
    global pointValue, upper, lower, count
    pointValue = random.randint(0, 99)
    upper = 99
    lower = 0
    count = 0
    print('point is %d' % pointValue)

def detect_point():
    """
    Check if the guessed number is the target, too high, or too low.
    :return: 1 if correct guess, 0 otherwise.
    """
    global count, upper, lower
    if count > pointValue and count < upper:
        upper = count
    elif count < pointValue and count > lower:
        lower = count
    elif count == pointValue:
        count = 0
        return 1
    count = 0
    return 0

def lcd_show_input(result):
    """
    Display the current game state and results on the LCD.
    :param result: Result of the last guess (0 or 1).
    """
    lcd.clear()
    if result == 1:
        lcd.write(0, 1, 'You have got it!')
        sleep(5)
        init_new_value()
        lcd_show_input(0)
    else:
        lcd.write(0, 0, 'Enter number:')
        lcd.write(13, 0, str(count))
        lcd.write(0, 1, str(lower))
        lcd.write(3, 1, ' < Point < ')
        lcd.write(13, 1, str(upper))

def loop():
    """
    Main game loop for handling keypad input and updating game state.
    """
    global keypad, last_key_pressed, count
    while True:
        result = 0
        pressed_keys = keypad.read()
        if pressed_keys and pressed_keys != last_key_pressed:
            if pressed_keys == ["A"]:
                init_new_value()
                lcd_show_input(0)
            elif pressed_keys == ["D"]:
                result = detect_point()
                lcd_show_input(result)
            elif pressed_keys[0] in keys:
                if pressed_keys[0] in ["A", "B", "C", "D", "#", "*"]:
                    continue
                count = count * 10 + int(pressed_keys[0])
                if count >= 10:
                    result = detect_point()
                lcd_show_input(result)
            print(pressed_keys)
        last_key_pressed = pressed_keys
        sleep(0.1)

try:
    loop()
except KeyboardInterrupt:
    lcd.clear()  # Clear LCD on interrupt



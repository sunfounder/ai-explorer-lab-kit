#!/usr/bin/env python3

from fusion_hat import Pin,Keypad,LCD1602
from time import sleep


# Password verification setup
LENS = 4
password = ['1', '9', '8', '4']  # Preset password
testword = ['0', '0', '0', '0']  # User input storage
keyIndex = 0  # Index for input keys

def check():
    """
    Check if the entered password matches the preset password.
    :return: 1 if match, 0 otherwise.
    """
    for i in range(LENS):
        if password[i] != testword[i]:
            return 0
    return 1


def loop():
    """
    Main loop for handling keypad input and password verification.
    """
    global keyIndex, last_key_pressed
    while True:
        pressed_keys = keypad.read()
        if pressed_keys and pressed_keys != last_key_pressed:
            if keyIndex < LENS:
                lcd.clear()
                lcd.write(0, 0, "Enter password:")
                lcd.write(15 - keyIndex, 1, pressed_keys[0])
                testword[keyIndex] = pressed_keys[0]
                keyIndex += 1

            if keyIndex == LENS:
                if check() == 0:
                    lcd.clear()
                    lcd.write(3, 0, "WRONG KEY!")
                    lcd.write(0, 1, "please try again")
                else:
                    lcd.clear()
                    lcd.write(4, 0, "CORRECT!")
                    lcd.write(2, 1, "welcome back")
                keyIndex = 0  # Reset key index after checking

        last_key_pressed = pressed_keys
        sleep(0.1)


# Pin configuration for keypad
rows_pins = [4, 17, 27, 22]
cols_pins = [23, 24, 25, 12]
keys = ["1", "2", "3", "A",
        "4", "5", "6", "B",
        "7", "8", "9", "C",
        "*", "0", "#", "D"]

# Initialize keypad and LCD
keypad = Keypad(rows_pins, cols_pins, keys)
last_key_pressed = []
lcd = LCD1602(address=0x27, backlight=1)
lcd.clear()
lcd.write(0, 0, 'WELCOME!')
lcd.write(2, 1, 'Enter password')
sleep(2)

try:
    loop()
except KeyboardInterrupt:
    lcd.clear()  # Clear LCD display on interrupt

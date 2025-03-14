#!/usr/bin/env python3

import time
from fusion_hat import Ultrasonic, Buzzer, Pin,LCD1602

# Trigger pin is connected to GPIO 27, Echo pin to GPIO 22
sensor = Ultrasonic(trig=Pin(27), echo=Pin(22))

# Initialize the buzzer connected to GPIO pin 17
buzzer = Buzzer(Pin(17))

# Initialize the LCD with I2C address and enable backlight
lcd = LCD1602(address=0x27, backlight=1)
lcd.clear()  # Clear the LCD display
# Display startup messages on LCD
lcd.write(0, 0, 'Ultrasonic Starting')
lcd.write(1, 1, 'By SunFounder')
time.sleep(2)  # Wait for 2 seconds

def distance():
    # Calculate and return the distance measured by the sensor
    dis = sensor.read() # Convert distance to centimeters
    print('Distance: {:.2f} cm'.format(dis))  # Print distance with two decimal places
    time.sleep(0.3)  # Wait for 0.3 seconds before next measurement
    return dis

def loop():
    # Continuously measure distance and update LCD and buzzer
    while True:
        dis = distance()  # Get the current distance
        # Display distance and handle alerts based on distance
        if dis > 400:  # Check if distance is out of range
            lcd.clear()
            lcd.write(0, 0, 'Error')
            lcd.write(3, 1, 'Out of range')
            time.sleep(0.5)
        else:
            # Display current distance on LCD
            lcd.clear()
            lcd.write(0, 0, 'Distance is')
            lcd.write(5, 1, str(round(dis, 2)) + ' cm')
            # Adjust buzzer frequency based on distance
            if dis >= 50:
                time.sleep(0.5)
            elif 20 < dis < 50:
                # Medium distance: medium buzzer frequency
                for _ in range(2):
                    buzzer.on()
                    time.sleep(0.05)
                    buzzer.off()
                    time.sleep(0.2)
            elif dis <= 20:
                # Close distance: high buzzer frequency
                for _ in range(5):
                    buzzer.on()
                    time.sleep(0.05)
                    buzzer.off()
                    time.sleep(0.05)

try:
    loop()      # Start the measurement loop
except KeyboardInterrupt:
    # Turn off buzzer and clear LCD on user interrupt (e.g., Ctrl+C)
    buzzer.off()
    lcd.clear()

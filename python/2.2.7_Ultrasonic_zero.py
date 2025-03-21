#!/usr/bin/env python3
from fusion_hat import Ultrasonic,Pin
from time import sleep

# Initialize the DistanceSensor
# Trigger pin is connected to GPIO 27, Echo pin to GPIO 22
sensor = Ultrasonic(trig=Pin(27), echo=Pin(22))

try:
    # Main loop to continuously measure and report distance
    while True:
        dis = sensor.read() # Measure distance in centimeters
        print('Distance: {:.2f} cm'.format(dis))  # Print the distance with two decimal precision
        sleep(0.3)  # Wait for 0.3 seconds before the next measurement

except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to gracefully exit the loop
    pass

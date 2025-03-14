#!/usr/bin/env python3

from fusion_hat import Motor, PWM, Pin, ADC
from time import sleep
import math

# Initialize GPIO pins for the button and motor control
BtnPin = Pin(22, Pin.IN, Pin.PULL_DOWN)
motor = Motor(PWM('P11'), PWM('P10'))
thermistor = ADC('A3')

# Initialize variables to track the motor speed level and temperatures
level = 0
currentTemp = 0
markTemp = 0

def temperature():
    """
    Reads and calculates the current temperature from the sensor.
    Returns:
        float: The current temperature in Celsius.
    """
    # Read analog value from the thermistor
    analogVal = thermistor.read()
    # Convert analog value to voltage and then to resistance
    Vr = 3.3 * float(analogVal) / 4095
    if 3.3 - Vr <= 0.1:
        print("Please check the sensor")
        return None
    Rt = 10000 * Vr / (3.3 - Vr)
    # Calculate temperature in Celsius
    temp = 1 / (((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
    Cel = temp - 273.15
    return Cel

def motor_run(level):
    """
    Adjusts the motor speed based on the specified level.
    Args:
        level (int): Desired motor speed level.
    Returns:
        int: Adjusted motor speed level.
    """
    # Stop the motor if the level is 0
    if level == 0:
        motor.speed(0)
        return 0
    # Cap the level at 4 for maximum speed
    if level >= 4:
        level = 4
    # Set the motor speed
    motor.speed(level*25)
    return level

def changeLevel():
    """
    Changes the motor speed level when the button is pressed and updates the reference temperature.
    """
    global level, currentTemp, markTemp
    
    # Cycle through levels 0-4
    level = (level + 1) % 5
    print("Button pressed, level changed to:", level)
    # Update the reference temperature
    markTemp = currentTemp

# Bind the button press event to changeLevel function
BtnPin.when_activated = changeLevel

def main():
    """
    Main function to continuously monitor and respond to temperature changes.
    """
    global level, currentTemp, markTemp
    # Set initial reference temperature
    markTemp = temperature()
    while True:
        # Continuously read current temperature
        currentTemp = temperature()
        if currentTemp == None:
            continue
        # Adjust motor level based on temperature difference
        if level != 0:
            if currentTemp - markTemp <= -5:
                level -= 1
                markTemp = currentTemp
                print("Temperature decreased, level changed to:", level," ,temperature:",currentTemp)
            elif currentTemp - markTemp >= 5:
                if level < 4:
                    level += 1
                markTemp = currentTemp
                print("Temperature increased, level changed to:", level," ,temperature:",currentTemp)
        # Run the motor at the adjusted level
        level = motor_run(level)
        sleep(0.5)

# Run the main function and handle KeyboardInterrupt
try:
    main()
except KeyboardInterrupt:
    # Stop the motor when the script is interrupted
    motor.speed(0)

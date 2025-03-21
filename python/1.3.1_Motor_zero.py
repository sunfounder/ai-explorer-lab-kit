#!/usr/bin/env python3
from time import sleep
from fusion_hat import Motor, PWM

"""
Initialize a motor

motor = Motor(pwmA, pwmB, is_reversed=False)

:param pwmA pwmB: Motor speed control pwm pin
:type pwm: fusion_hat.pwm.PWM

:param is_reversed: Motor direction control
:type is_reversed: True or False
:default: False
"""

motor = Motor('M0')

try:
    while True:
        motor.speed(0)
        sleep(0.5)
        motor.speed(-50)
        sleep(1)
        motor.speed(0)
        sleep(0.5)
        motor.speed(75)
        sleep(1)
finally:
    motor.stop()
    sleep(.1)

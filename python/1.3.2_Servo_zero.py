from fusion_hat import Servo
from time import sleep

servo = Servo('P0')

while True:
    for i in range(-90, 91, 10):
        servo.angle(i)
        sleep(0.1)
    for i in range(90, -91, -10):
        servo.angle(i)
        sleep(0.1)

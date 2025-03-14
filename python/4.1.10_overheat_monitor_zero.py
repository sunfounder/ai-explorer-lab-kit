#!/usr/bin/env python3

from fusion_hat import Pin, Buzzer, ADC,LCD1602
import time
import math

# Initialize joystick button, buzzer, and LED
Joy_BtnPin = Pin(17, Pin.IN, Pin.PULL_UP)
xAxis = ADC('A1')
yAxis = ADC('A0')

buzzPin = Buzzer(Pin(22, Pin.OUT))
ledPin = Pin(27, Pin.OUT)
thermistor = ADC('A3')

# Set initial upper temperature threshold
upperTem = 40

# Setup LCD modules
lcd = LCD1602(address=0x27, backlight=1)

def MAP(x, in_min, in_max, out_min, out_max):
    """
    Map a value from one range to another.
    :param x: The value to be mapped.
    :param in_min: The lower bound of the value's current range.
    :param in_max: The upper bound of the value's current range.
    :param out_min: The lower bound of the value's target range.
    :param out_max: The upper bound of the value's target range.
    :return: The mapped value.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def get_joystick_value():
    """
    Reads the joystick values and returns a change value based on the joystick's position.
    """
    x_val = MAP(xAxis.read(),0,4095,-100,100)
    y_val = MAP(yAxis.read(),0,4095,-100,100)
    if x_val > 50:
        return 1
    elif x_val < -50:
        return -1
    elif y_val > 50:
        return -10
    elif y_val < -50:
        return 10
    else:
        return 0

def upper_tem_setting():
    """
    Adjusts and displays the upper temperature threshold on the LCD.
    """
    global upperTem
    lcd.write(0, 0, 'Upper Adjust: ')
    change = int(get_joystick_value())
    upperTem += change
    strUpperTem = str(upperTem)
    lcd.write(0, 1, strUpperTem)
    lcd.write(len(strUpperTem), 1, '              ')
    time.sleep(0.1)

def temperature():
    """
    Reads the current temperature from the sensor and returns it in Celsius.
    """
    analogVal = thermistor.read()
    Vr = 3.3 * float(analogVal) / 4095
    if 3.3 - Vr < 0.1:
        print("Please check the thermistor")
        time.sleep(1)
        return None
    Rt = 10000 * Vr / (3.3 - Vr)
    temp = 1 / (((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
    Cel = temp - 273.15
    return round(Cel, 2)

def monitoring_temp():
    """
    Monitors and displays the current temperature and upper temperature threshold. 
    Activates buzzer and LED if the temperature exceeds the upper limit.
    """
    global upperTem
    Cel = temperature()
    if Cel is None:
        return
    lcd.write(0, 0, 'Temp: ')
    lcd.write(0, 1, 'Upper: ')
    lcd.write(6, 0, str(Cel))
    lcd.write(7, 1, str(upperTem))
    time.sleep(0.1)
    if Cel >= upperTem:
        buzzPin.on()
        ledPin.on()
    else:
        buzzPin.off()
        ledPin.off()

# Main execution loop
try:
    lastState = 1
    stage = 0
    while True:
        currentState = Joy_BtnPin.value()
        # Toggle between settings and monitoring mode
        if currentState == 1 and lastState == 0:
            stage = (stage + 1) % 2
            time.sleep(0.1)
            lcd.clear()
        lastState = currentState
        if stage == 1:
            upper_tem_setting()
        else:
            monitoring_temp()

except KeyboardInterrupt:
    # Clean up and exit
    lcd.clear()

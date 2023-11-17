from machine import Pin
from time import sleep

# setup the rain sensor pin as an input
rain_sensor_pin = Pin(33, Pin.IN)

# check the status of the rain sensor
while True:
    if rain_sensor_pin.value() == 1:
        print("It is not raining")
    else:
        print("It is raining")
        
    sleep(1)
from machine import Pin
from time import ticks_ms, ticks_diff

IR = Pin(33,Pin.IN)
    
def time_for_revolution(self):
    start_time = ticks_ms()  # Record start time

  # Wait for sensor to trigger (e.g. object passes sensor)
    while not IR.value():
        pass

    end_time = ticks_ms()  # Record end time
    
  
  # Return time elapsed between start and end
    if((ticks_diff(end_time, start_time)) != 0):
        rpm = 60000/(ticks_diff(end_time, start_time))
        priemer = 5
        windspeed = (priemer*rpm) * 0.001885
        print("rýchlosť vetra: {} kmh".format(round(windspeed,2)))
    
    
IR.irq(trigger = Pin.IRQ_RISING, handler = time_for_revolution)
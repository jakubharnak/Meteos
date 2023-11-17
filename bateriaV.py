from machine import ADC, Pin
from time import sleep_ms

a = ADC(Pin(33), atten = ADC.ATTN_11DB)
while True:
    print("{:.2f} V".format(((a.read_uv() / 1_000_000 / 0.7874015)-3.7)*(100/(4.04-3.7))), end = "\r")
    sleep_ms(100)
    
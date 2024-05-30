from wifi import WiFi
from umqtt.simple import MQTTClient, MQTTException
from machine import ADC, Pin, I2C, Timer,reset
from bme680 import BME680_I2C as BME680
from time import sleep, sleep_ms, time,ticks_ms, ticks_diff

#-temy na mqtt
V = "harnak/meranie/vietor"
B = "harnak/meranie/bateria"
T = "harnak/meranie/teplota"
Vl = "harnak/meranie/vlhkost"
Tl = "harnak/meranie/tlak"
Vz = "harnak/meranie/vzduch"
D = "harnak/meranie/dazd"

def meranie():
    #-zaznamená čas začiatku otáčky 
    start_time = ticks_ms()

    b = True
  #-počká kým senzor zaznamená (objekt prejde cez IR branu)
    while not IR.value():
        if((ticks_diff(ticks_ms(), start_time)) > 1000):
            b = False
            break
        pass

    #-zaznamena konečný čas otáčky
    end_time = ticks_ms()
    
    #-vráti rýchlosť v kmh alebo ak sa točí veľmi pomaly vráti 0kmh
    if b and ((ticks_diff(end_time, start_time)) != 0):
        rpm = 60000/(ticks_diff(end_time, start_time))
        priemer = 18
        windspeed = (priemer*rpm) * 0.001885
        print("Rýchlosť vetra: {} kmh".format(round(windspeed,2)))
    else:
        windspeed = 0
        print("Vietor je veľmi slabý alebo je bezvetrie")
    #-nameranie hodnôt
    teplota = bme680.temperature
    vlhkost = bme680.humidity
    tlak = bme680.pressure
    dazd = rain_sensor_pin.value()
    bateria = (((battery.read_uv() / 1_000_000 / 0.7874015)-3.7)*(100/(4.04-3.7)))
    #-zahrievanie snezoru bme680-----------------------------------------------------------------
    plyn_max = 0
    while True:
        plyn = bme680.gas / 1000
        print("zahrievam:",plyn,end = "\r")
        if plyn <= plyn_max: break
        plyn_max = plyn
        sleep_ms(200)
    vzduch = plyn_max
    #-výpis hodnôt do sérioveho portu------------------------------------------------------------
    print("Teplota: {:.2f} °C, vlhkosť: {:.2f} %, tlak: {:.2f} hPa, batéria {:.2f} %, vzduch: {:.0f}, dazd: {:.0f}".format(teplota, vlhkost, tlak, bateria,vzduch, dazd))
    #-odoslanie nameraných hodnôt----------------------------------------------------------------
    mqtt.publish(T, str(round(teplota,2)), qos = 1)
    mqtt.publish(Vl, str(round(vlhkost,2)), qos = 1)
    mqtt.publish(Tl, str(round(tlak,2)), qos = 1)
    mqtt.publish(Vz, str(round(vzduch,2)), qos = 1)
    mqtt.publish(B, str(round(bateria,2)), qos = 1)
    mqtt.publish(D, str(round(dazd,2)), qos = 1)
    mqtt.publish(V, str(round(windspeed,1)), qos = 1)


wifi = WiFi()
bme680 = BME680(i2c = I2C(0, scl = Pin(18), sda = Pin(19)))
battery = ADC(Pin(34), atten = ADC.ATTN_11DB)
rain_sensor_pin = Pin(33, Pin.IN)
IR = Pin(32,Pin.IN)

#-udaje pre mqtt----------------------------------------------------------------
klient = "153"#153
ip = "192.168.1.48"
idc = 0
user = "harnac"
password = "harnac"
ssl = False
params = {}

mqtt = MQTTClient(klient, ip, idc, user, password, 600, ssl, params)
try:
    mqtt.connect()
except:
    print("Chyba spojenia s MQTT brokerom {}!".format(mqtt.server))

while True:
    try:
    #-pokusi sa merat----------------------------------------------------------------------------
        meranie()
    except Exception as e:
    #-ak sa vyskytne problem tak sa pokusi znova-------------------------------------------------
        reset()
    #-pocka 5 minut----------------------------------------------------------------------------  
    sleep(300)
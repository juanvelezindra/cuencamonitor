from m5stack import * 
from m5ui import *
from uiflow import *
import wifiCfg
import espnow
from m5mqtt import M5mqtt
import hat
import json
import unit
import machine
import urequests
import machine
from micropython import const
import ntptime

setScreenColor(0x111111)
macAddr = None
id_client_control = None
id_client_business = None
business_topic_p = None
business_topic_s = None
sensorData = None
mensaje = None
longitud = '6.292211'
latitud = '-75.217438'
ssid = 'JUAN ESTEBAN ' 
password_wifi = '43796254'

wifiCfg.wlan_sta.active(True)
wifiCfg.doConnect(ssid, password_wifi)

wifiCfg.wlan_ap.active(True)
wifiCfg.wlan_sta.active(True)
espnow.init()

while (not wifiCfg.wlan_sta.isconnected()):
    wifiCfg.doConnect(ssid, password_wifi)
    
ntp = ntptime.client(host='es.pool.ntp.org', timezone=1)
rtc.setTime((ntp.year()), (ntp.month()), (ntp.day()), (ntp.hour()), (ntp.minute()), (ntp.second()))

env20 = unit.get(unit.ENV2, unit.PORTA)

wifiCfg.wlan_ap.active(True)
wifiCfg.wlan_sta.active(True)
espnow.init()

label0 = M5TextBox(78, 0, "Campo 1", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label1 = M5TextBox(61, 0, "Campo 2", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label2 = M5TextBox(44, 0, "Campo 3", lcd.FONT_Default, 0xFFFFFF, rotate=90)
label3 = M5TextBox(26, 0, "Campo 4", lcd.FONT_Default, 0xFFFFFF, rotate=90)

macAddr = str((espnow.get_mac_addr()))
macAddr = macAddr.replace(':', '').upper()
id_client_control = macAddr
id_client_business = "b_"+id_client_control
frec=1
business_topic_p = "business/TEAM_2/ENT/server"
business_topic_s = "business/TEAM_2/ENT/device/"+id_client_business
label0.setText(str(macAddr))
label1.setText(str(id_client_business))
label3.setText('Hello GPS')
label0.setText(str(business_topic_p))
wait(3)

label0.setText('Inicio Envío')
label1.setText(str(str(macAddr)))
label3.setText('Searching for Sats')
wait(3)

m5mqtt = M5mqtt(str(id_client_business), 'iothub02.onesaitplatform.com', 8883, str(id_client_control), 'bQOj4Gan', 30, ssl = True)

def fun_business_d2c_(topic_data):
  global m5mqtt,business_topic_p
  label1.setText(str(topic_data))  
  m5mqtt.publish(str(business_topic_p),str((json.dumps(topic_data))))
  
m5mqtt.start()
while True:
    sensorData = {'humidity':(env20.humidity),'temperature':(env20.temperature),'pressure':(env20.pressure)}
    label2.setText(str(id_client_business))
    label3.setText(str(business_topic_p))
    mensaje = {'deviceId':macAddr,'timestamp':ntp.getTimestamp()}
    mensaje.update(sensorData)
    fun_business_d2c_(mensaje) 
    label0.setText('Publicando...')

    wait(1.5)
    mensaje.clear()
    sensorData.clear()
    wait(frec)
    while (not wifiCfg.wlan_sta.isconnected()):
        wifiCfg.doConnect(ssid, password_wifi)
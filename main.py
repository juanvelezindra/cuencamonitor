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

#####Funcion para enviar las medidas del json#####
def fun_envio_mqtt(topic_data):
  global m5mqtt,vUrl_out
  m5mqtt.publish(str(vUrl_out),str((json.dumps(topic_data))))

#####Funcion para recibir el json de respuesta#####  
def fun_recibir_mqtt(topic_data):
  global m5mqtt,respuesta,label1
  wait(1)
  jsonTopic_data=json.loads(topic_data)
  respuesta=jsonTopic_data["respuesta"]
  label1.setText(str(respuesta))
  wait(1)

#####Declaracion de variables#####
setScreenColor(0x111111)
vMac=None
vDate = None
vHour = None
vLon = None
vLat = None
vDId = None
vDId_b = None
vZH = None
vUrl_in = None
vUrl_out = None
vSsid = None
vPassword = None
vTokenMqtt = None
vUrl_ser = None
env20 = None
jsonMedida = None
envio = None
respuesta = None
nivel1 = None
caudal1 = None
ph1 = None

#####Iniciar y conectar wifi#####
vSsid = 'JUAN ESTEBAN ' 
vPassword = '43796254'
wifiCfg.wlan_sta.active(True)
wifiCfg.doConnect(vSsid, vPassword)
wifiCfg.wlan_ap.active(True)
wifiCfg.wlan_sta.active(True)
espnow.init()
while (not wifiCfg.wlan_sta.isconnected()):
  wifiCfg.doConnect(vSsid, vPassword)

#####Fija fecha y hora#####
vZH = ntptime.client(host='es.pool.ntp.org', timezone=-5)
rtc.setTime((vZH.year()), (vZH.month()), (vZH.day()), (vZH.hour()), (vZH.minute()), (vZH.second()))

#####Obtener mac del dispositivo#####
wifiCfg.wlan_ap.active(True)
wifiCfg.wlan_sta.active(True)
espnow.init()
vMac = str((espnow.get_mac_addr()))
vMac = vMac.replace(':', '').upper()

#####Inicializacion variables#####
vUrl_out = "business/TEAM_2/ENT/server"
vUrl_in = "business/TEAM_2/ENT/device/b_"+vMac
vLon = 4.7026
vLat = -73.5183
vDId = vMac
vDId_b="b_"+vMac
vDate = str(vZH.year()) + '/' + str(vZH.month()) + '/' + str(vZH.day())
vHour = str(vZH.hour()) + ':' + str(vZH.minute()) + ':' + str(vZH.second())
vTokenMqtt = 'bQOj4Gan'
vUrl_ser = 'iothub02.onesaitplatform.com'
wait(3)

#####Obtener medidas#####
env20 = unit.get(unit.ENV2, unit.PORTA)
wait(3)

#####Inicializar mqtt#####
m5mqtt = M5mqtt(str(vDId_b), str(vUrl_ser), 8883, str(vDId), str(vTokenMqtt), 30, ssl = True)
m5mqtt.subscribe(vUrl_in, fun_recibir_mqtt)
m5mqtt.start()
wait(3)


#####Creacion del entorno grafico#####
nivel0 = M5TextBox(2, 2, "Nivel:", lcd.FONT_Default, 0xFFFFFF, rotate=0)
nivel1 = M5TextBox(2, 18, "N", lcd.FONT_Default, 0xFFFFFF, rotate=0)
rectangle0 = M5Rect(2, 35, 80, 1, 0xFFFFFF, 0xff0303)
caudal0 = M5TextBox(2, 40, "Caudal:", lcd.FONT_Default, 0xFFFFFF, rotate=0)
caudal1 = M5TextBox(2, 56, "C", lcd.FONT_Default, 0xFFFFFF, rotate=0)
rectangle1 = M5Rect(2, 72, 80, 1, 0xFFFFFF, 0x0007ff)
ph0 = M5TextBox(2, 78, "Ph:", lcd.FONT_Default, 0xFFFFFF, rotate=0)
ph1 = M5TextBox(2, 92, "P", lcd.FONT_Default, 0xFFFFFF, rotate=0)
rectangle2 = M5Rect(0, 108, 80, 1, 0xFFFFFF, 0x00ff0c)
label0 = M5TextBox(2, 112, "Estado:", lcd.FONT_Default, 0xffffff, rotate=0)
label1 = M5TextBox(2, 130, "%", lcd.FONT_Default, 0xff0000, rotate=0)
wait(3)

while True:
  lHum=env20.humidity
  lTem=env20.temperature
  lPre=7*env20.pressure/800
  lPre=float("{:.3f}".format(lPre))
  nivel1.setText(str(lHum))
  caudal1.setText(str(lTem))
  ph1.setText(str(lPre))
  vDate = str(vZH.year()) + '/' + str(vZH.month()) + '/' + str(vZH.day())
  vHour = str(vZH.hour()) + ':' + str(vZH.minute()) + ':' + str(vZH.second())
  
  jsonMedida = {'level':(lHum),'flow':(lTem),'ph':(lPre),'longitude':vLon,'latitude':vLat,'date':vDate,'hour':vHour}
  envio = {'deviceId':vMac,'point':{'coordinates':[vLon,vLat],'type':'Point'} ,'timestamp':vZH.getTimestamp()}
  envio.update(jsonMedida)
  wait(3)
  fun_envio_mqtt(envio)
  wait(3)
  jsonMedida.clear()
  envio.clear()
  while (not wifiCfg.wlan_sta.isconnected()):
	wifiCfg.doConnect(ssid, password_wifi)
  




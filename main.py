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

#####Definicion de las funciones#####

#####Funcion para la creacion del entorno grafico#####
def fun_entorno_grafico():
  global nivel1,caudal1,ph1
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

#####Funcion para iniciar variables del wifi#####
def fun_ini_wifi():
  global vSsid,vPassword
  vSsid = 'JUAN ESTEBAN ' 
  vPassword = '43796254'

#####Funcion para realizar la conexion con el wifi#####
def fun_conectar_wifi():
  global vSsid,vPassword
  wifiCfg.wlan_sta.active(True)
  wifiCfg.doConnect(vSsid, vPassword)
  wifiCfg.wlan_ap.active(True)
  wifiCfg.wlan_sta.active(True)
  espnow.init()
  while (not wifiCfg.wlan_sta.isconnected()):
      wifiCfg.doConnect(vSsid, vPassword)

#####Funcion para la definicion de la hora#####
def fun_def_fechahora():
  global vZH
  vZH = ntptime.client(host='es.pool.ntp.org', timezone=-5)
  rtc.setTime((vZH.year()), (vZH.month()), (vZH.day()), (vZH.hour()), (vZH.minute()), (vZH.second()))

#####Funcion para obtener la Mac del dispositivo#####
def fun_obt_mac():
  global vMac
  wifiCfg.wlan_ap.active(True)
  wifiCfg.wlan_sta.active(True)
  espnow.init()
  vMac = str((espnow.get_mac_addr()))
  vMac = vMac.replace(':', '').upper()

#####Funcion para la inicializacion de variables#####
def fun_ini_var():
  global vMac,vDate,vHour,vLon,vLat,vDId,vUrl_in,vUrl_out,vZH
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


#####Funcion para crear mqtt#####
def fun_ini_mqtt():
  global vDId,vDId_b,vUrl_ser,vTokenMqtt,vUrl_ser,m5mqtt
  m5mqtt = M5mqtt(str(vDId_b), str(vUrl_ser), 8883, str(vDId), str(vTokenMqtt), 30, ssl = True)

#####Funcion para arrancar mqtt#####
def fun_arrancar_mqtt():
  global m5mqtt
  m5mqtt.start()

#####Funcion para obtener medida#####
def fun_obtener_medida():
  global env20
  env20 = unit.get(unit.ENV2, unit.PORTA)

#####Funcion construir el json#####
def fun_generar_json_envio():
  global env20,vZH,vMac,vLon,vLat,vDate,vHour,jsonMedida,envio,nivel1,caudal1,ph1
  lHum=env20.humidity
  lTem=env20.temperature
  lPre=7*env20.pressure/1000
  lPre=float("{:.3f}".format(lPre))
  nivel1.setText(str(lHum))
  caudal1.setText(str(lTem))
  ph1.setText(str(lPre))
  
  jsonMedida = {'level':(lHum),'flow':(lTem),'ph':(lPre),'longitude':vLon,'latitude':vLat,'date':vDate,'hour':vHour}
  envio = {'deviceId':vMac,'point':{'coordinates':[vLon,vLat],'type':'Point'} ,'timestamp':vZH.getTimestamp()}
  envio.update(jsonMedida)
  return envio

#####Funcion limpiar el json#####
def fun_limpiar_data():
  global jsonMedida,envio
  jsonMedida.clear()
  envio.clear()

#####Funcion para enviar las medidas del json#####
def fun_envio_mqtt(topic_data):
  global m5mqtt,vUrl_out
  m5mqtt.publish(str(vUrl_out),str((json.dumps(topic_data))))
  
#####Funcion para recibir el json de respuesta#####  
def fun_recibir_mqtt(topic_data):
  global m5mqtt,respuesta
  wait(1)
  jsonTopic_data=json.loads(topic_data)
  respuesta=jsonTopic_data["respuesta"]
  wait(1)

#####Funcion para la subscripcion del mqtt#####
def fun_subscripcion_mqtt():
  global m5mqtt,vUrl_in
  m5mqtt.subscribe(vUrl_in, fun_recibir_mqtt)



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
fun_ini_wifi()
fun_conectar_wifi()
#####Fija fecha y hora#####
fun_def_fechahora()
#####Obtener mac del dispositivo#####
fun_obt_mac()
#####Inicializacion variables#####
fun_ini_var()
#####Inicializar mqtt#####
fun_ini_mqtt()
fun_subscripcion_mqtt()
fun_arrancar_mqtt()
#####Obtener medidas#####
fun_obtener_medida()
#####Creacion del entorno grafico#####
fun_entorno_grafico()

while True:
  p_envio = fun_generar_json_envio()
  fun_limpiar_data()
  fun_envio_mqtt(p_envio)
  p_envio.clear()
  wait(1.5)

  while (not wifiCfg.wlan_sta.isconnected()):
      wifiCfg.doConnect(ssid, password_wifi)

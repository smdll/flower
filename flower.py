#/usr/bin/python
# coding=utf-8
import RPi.GPIO as GPIO
import dht11
import RPI_ADC0832

import time
import urllib
import configparser
import json
import threading

PUMP_PIN = 4
LIGHT_PIN = 22
DHT_PIN = 19

server = ''
root = '/flower/api'
water = False
dht = dht11.DHT11(pin = DHT_PIN) # 温湿度传感器
soil = RPI_ADC0832.ADC0832()

def writeConfig(section, **kwargs):
	config = configparser.ConfigParser()
	try:
		config[section] = kwargs
		with open('flower.ini', 'w') as file:
			config.write(file)
		return True
	except:
		return False

def readConfig(section, kw):
	config = configparser.ConfigParser()
	try:
		config.read('flower.ini')
		result = config[section][kw]
		return result
	except:
		return ''

serial = readConfig('deviceInfo', 'serial')

#1
#注册新设备
def regNewDevice():
	global serial
	if not serial == '':
		return True
	import uuid
	mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
	macstr = '-'.join([mac[e:e+2] for e in range(0,11,2)])
	url = 'http://%s%s/device?code=10014&mac=%s'%(server, root, macstr)
	f = urllib.urlopen(url)
	result = json.loads(f.read())
	f.close()
	code = result['code']
	if code == '0':
		serial = result['data']['serial']
		writeConfig('deviceInfo', serial = serial)
		return True
	return False

#2
#上传数据
def updateData():
	global serial
	while True:
		url = 'http://%s%s/device?code=10015&serial=%s&%s'%(server, root, serial, urllib.urlencode(getData()))
		f = urllib.urlopen(url)
		result = json.loads(f.read())
		f.close()
		code = result['code']
		time.sleep(20)

#3
#获取开关状态
def queryStat():
	global serial
	global water
	errcode = ['90014', '90015', '90010']
	recv = urllib.urlopen('http://%s%s/device?code=10016&serial=%s'%(server, root, serial))
	while True:
		data = ''
		while True:
			c = recv.read(1)
			if c == '!':
				break
			data += c
		print data
		if data in errcode:
			return False

		retcode = 0
		if data == '1':
			if water = True:
				retcode = 2
			else:
				t = threading.Thread(target = watering)
				t.start()
				retcode = 1
		#elif data == '2':
		#		lighting(True)
		#		retcode = 3
		urllib.urlopen('http://%s%s/device?code=10021&serial=%s&msg=%d'%(server, root, serial, retcode)).close()

# 硬件部分
# 浇花
def watering():
	global water
	water = True
	GPIO.output(4, GPIO.HIGH)
	time.sleep(5)
	GPIO.output(4, GPIO.LOW)
	water = False

# 开灯
def lighting(up):
	if up:
		GPIO.output(17, GPIO.HIGH)
	else:
		GPIO.output(17, GPIO.LOW)

# 获取各种传感器
def getData():
	data = {}
	result = dht.read()
	if result.is_valid():
		data['at'] = str(result.temperature)
		data['ah'] = str(result.humidity)
	data['sh'] = str(soil.read_adc(0))
	return data

if __name__ == '__main__':
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.cleanup()
	GPIO.setup(PUMP_PIN, GPIO.OUT)#water pump
	GPIO.setup(LIGHT_PIN, GPIO.OUT)#light
	queryStat()

#!/usr/bin/python
import sys
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import datetime
import logging
import schedule
from fbchat import Client
from fbchat.models import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)
GPIO.setup(13, GPIO.IN)
GPIO.setup(15, GPIO.IN)
GPIO.setup(12, GPIO.IN)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

moistTop =  GPIO.input(11)
moistMid = GPIO.input(13)
moistBot = GPIO.input(15)
waterLevel = GPIO.input(12)
GPIO.output(16, True) #active low
GPIO.output(18, True) #active low

logging.basicConfig(filename='/home/pi/mylog.txt', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

try:
  1/0
except ZeroDivisionError as err:
  logger.error(err)
start = 0
def StartDrip():
	global start
	#pause before login
	print('Please Wait.')
  time.sleep(2)

  startDT = datetime.datetime.now() #dripping start Date&Time
  startDT = startDT.replace(microsecond=0)
  now = str(startDT)
  introMsg = 'Dripping Just Started @ ' + now
  print(introMsg)
  start = time.time()
  humidity, temperature = Adafruit_DHT.read_retry(11, 4)
  print 'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)
  tempUp = 'Temperature Update: ' + str(temperature) + '`C'
  client = Client('RasPVi', 'dripsearch5') 
  client.send(Message(text=tempUp), thread_id='1357366101042061', thread_type=ThreadType.GROUP)
  client.send(Message(text=introMsg), thread_id='1357366101042061', thread_type=ThreadType.GROUP)

  print('Message Sent!')
  time.sleep(1)
  print('Signing Out.'),
  time.sleep(1)
  print('.'),
  time.sleep(1)
  print('.')
  client.logout()   
  return

def StopDrip():
  print('Please Wait.'),
  time.sleep(2)
  end = time.time()	#computation of time elapsed on drip
  tTime = end-start
	waterVol =tTime*0.46667
	if waterVol < 1000:
    waterVol = float(waterVol)
    waterVol = '%03.2f'%(waterVol)
    waterVol = 'Average drench per Plant: ' + str(waterVol) + 'ml'
	else:
		waterVol = waterVol/1000
    waterVol = float(waterVol)
    waterVol = '%03.2f'%(waterVol)
		waterVol =  'Average drench per Plant: ' + str(waterVol) + 'L'
    hours = tTime//3600
    temp = tTime - 3600*hours
    minutes = tTime//60
    seconds = int(tTime - 60*minutes)

	dripTime = 'Dripping Time per Plant: ' + str(int(hours)) + ':' + str(int(minutes)) + ':' + str(int(seconds))
  print('Watering Time per Plant: %d:%d:%d' %(hours,minutes,seconds))
	print(waterVol)

  client = Client('RasPVi', 'dripsearch5')
  client.send(Message(text='Your Plant has been Drench! ^_^'),  thread_id='1401216186621686', thread_type=ThreadType.GROUP)
  client.send(Message(text=dripTime),  thread_id='1357366101042061', thread_type=ThreadType.GROUP)
  client.send(Message(text=waterVol),  thread_id='1357366101042061', thread_type=ThreadType.GROUP)

	print('Message Sent!')
	time.sleep(1)
  print('Signing Out.'),
  time.sleep(0.5)
  print('.'),
  time.sleep(0.5)
  print('.')
	client.logout()
  return

def RefillTank():
  if  waterLevel == 1:
    GPIO.output(16, True)
    print('Refilling Tank.')
  else:
    GPIO.output(16, False)
    print('Tank has been Reflenished.')
	return

def RunSched():
  print('Please Wait...')
  time.sleep(2)
  humidity, temperature = Adafruit_DHT.read_retry(11, 4)
  print 'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)
  tempUp = 'Temperature: ' + str(temperature) + '`C'
  humidUp = 'Humidity:   ' + str(humidity) + '%'
  client = Client('RasPVi', 'dripsearch5')
  client.send(Message(text=tempUp), thread_id='1514413705338820', thread_type=ThreadType.GROUP)
  client.send(Message(text=HumidUp), thread_id='1514413705338820', thread_type=ThreadType.GROUP)
  print('Message Sent! '),
  print('Signing Out...')
  time.sleep(2)
  client.logout()
  print('Waiting for schedule update...')
	time.sleep(60)
  return




schedule.every().day.at("6:02").do(RunSched)
schedule.every().day.at("8:00").do(RunSched)
schedule.every().day.at("12:00").do(RunSched)
schedule.every().day.at("15:00").do(RunSched)


'''
Input:			Board
  soilMoisture1   --      11
  soilMoisture2   --      13
  soilMoisture3   --      15
  humidity        --      7 (4@BCM)
  WaterLevel      --      12
Output:
  inletValve      --      16
  outletValve     --      18
'''



while True:
	RefillTank()
	schedule.run_pending()
	if (moistTop == 1) or (moistMid == 1) or (moistBot == 1):
		while (moistTop == 1) or (moistMid == 1) or (moistBot == 1):
			GPIO.output(18, False) #active low
			print('Watering on going..'),
			RefillTank()
			time.sleep(1)
			schedule.run_pending()
		  GPIO.output(18, True)
	else:
		print('Still Wet.')


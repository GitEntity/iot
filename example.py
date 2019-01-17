import os, sys
import MPL3115A2 as AltiBar
from ctypes import *
import paho.mqtt.publish as publish
sensor = CDLL("./libMPL.so") #load t$
sensor.I2C_Initialize(AltiBar.MPL3115A2_ADDRESS) #initialize I2C and BCM$
def main(argv):

	topic = "/test"
	while True:
		AltiBar.ActiveMode() #puts sensor in active mode
		AltiBar.BarometerMode() #puts sensor in active mode
		pressure= AltiBar.ReadBarometricPressure()
		send = "Pressure: " + str(pressure)
		publish.single(topic, send, hostname="192.168.137.2") #this is the IP address on pi
		time.sleep(0.5)
		AltiBar.ActiveMode() #puts sensor in active mode
		time.sleep(0.5)
		#AltiBar.TemperatureMode()
		temperature = AltiBar.ReadTemperature()
		time.sleep(0.5)
		send = "temperature : " + str(temperature)
		if temperature>=30:
			publish.single(topic, send, hostname="192.168.137.2") #this is the IP address on pi
		time.sleep(1)
		AltiBar.ActiveMode() #puts sensor in active mode
		time.sleep(0.5)
		AltiBar.AltimeterMode()
		time.sleep(0.5)
		altitude = AltiBar.ReadAltitude()
		time.sleep(0.5)
		send = "altitude : " + str(altitude)
		publish.single(topic, send, hostname="192.168.137.2") #this is the IP address on pi
		time.sleep(1)
main(sys.argv[1:])
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import required libraries
import RPi.GPIO as GPIO
import time

# perform setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup( 12 , GPIO.OUT)

# perform ON/OFF LED switching
for i in range ( 10 ):
	# set LED ON through GPIO pin
	GPIO.output( 12 , GPIO.HIGH)
	# set sleep delay for a second
	time.sleep( 1 )
	# set LED OFF through GPIO pin
	GPIO.output( 12 , GPIO.LOW)
	# set sleep delay for a second
	time.sleep( 1 )
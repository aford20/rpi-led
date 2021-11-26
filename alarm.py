# This script is called by crontab at a certain time to function as an alarm clock.
# Random Leds slowly light up increasing brightness. Script only ends when a button is pressed.
# Modify the below variables to set a preferred section of strip and strength of preference

prefer_start = 36
prefer_end = 59
prefer_percent = 75

inWaitMode = False

# Turn off all lights and end script
def shutOff():
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i, 0, 0, 0)
        strip.show()
        sleep(.02)
    #Shutdown this script
    raise SystemExit

# Turn off side lights
def waitMode():
    global inWaitMode
    inWaitMode = True
    for i in range(prefer_start):
        strip.setPixelColorRGB(i, 0, 0, 0)
        strip.show()
        sleep(.05)

# Generate Loop. j = max brightness. x = pixels per loop
def pixelLoop(j,x):
    for i1 in range(1,j):
        for i2 in range(x):
            yield i1, i2

# Import Libriaries
from rpi_ws281x import *
from time import sleep

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import random
import math

from threading import Timer
timer = Timer(45.0,waitMode)

# Import Config File
import configparser
cfg = configparser.ConfigParser()
cfg.read('config.conf')

# Strip and GPIO Setup
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
strip = Adafruit_NeoPixel(int(cfg['strip1']['length']), int(cfg['strip1']['gpio_pin']), 800000, 10, False, 255,int(cfg['strip1']['channel']))
strip.begin()

# Increase Brightness. Random LED. 1 Color.
print("Increasing Brightness ...")
for a,b in pixelLoop(256,7):
    if random.randint(0,100) <= prefer_percent:
        strip.setPixelColorRGB(random.randint(prefer_start,prefer_end),int(a/2),a,a)
    else:
        strip.setPixelColorRGB(random.randint(0,prefer_start),int(a/2),a,a)
    strip.show()
    sleep(1 / math.ceil(a/12))
    if GPIO.input(23) == 0: #Btn Press
        waitMode() #Turn off side
        for i in range(prefer_start,prefer_end): #Top to full brightness
            strip.setPixelColorRGB(i,128,255,255)
            strip.show()
            sleep(.05)
        break

# Only if not already in waitMode
if not inWaitMode:
    # Make Sure Every LED is at full brightness
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i,128,255,255)
        sleep(0.05)
        strip.show()

    timer.start()

while True:
    GPIO.wait_for_edge(23,GPIO.FALLING)
    timer.cancel()
    if inWaitMode:
        shutOff()
    else:
        waitMode()

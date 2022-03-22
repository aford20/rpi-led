# This script is called by crontab at a certain time to function as an alarm clock.
# Random Leds slowly light up increasing brightness over 5 min. Script only ends when a button is pressed.

# Turn off all lights and end script
def shutOff():
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i, 0, 0, 0)
        strip.show()
        sleep(.04)
    #Shutdown this script
    raise SystemExit
        
# Generate Loop. j = max brightness. x = pixels per loop
def pixelLoop(j,x):
    for i1 in range(j):
        for i2 in range(x):
            yield i1, i2    

# Import Libriaries
from rpi_ws281x import *
from time import sleep

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import random

# Import Config File
import os.path
import configparser
cfg = configparser.ConfigParser()
cfg.read(os.path.abspath(os.path.dirname(__file__))+'/config.conf')

# Strip and GPIO Setup
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
strip = Adafruit_NeoPixel(int(cfg['strip1']['length']), int(cfg['strip1']['gpio_pin']), 800000, 10, False, 255,int(cfg['strip1']['channel']))
strip.begin()

# Increase Brightness. Random LED. 1 Color.
print("Increasing Brightness ...")
for a,b in pixelLoop(256,12):
    strip.setPixelColorRGB(random.randint(0,strip.numPixels()),int(a/2),a,a)
    strip.show()
    sleep(.1)
    if GPIO.input(23) == 0: #Break for Btn Press
        break             

print("Max Brightness")

while True:
    # Shutdown on btn press
    if GPIO.input(23) == 0:
        shutOff()
    GPIO.wait_for_edge(23, GPIO.FALLING)

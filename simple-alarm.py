# This script is called by crontab at a certain time to function as an alarm clock.
# Random Leds slowly light up increasing brightness over 5 min. Script only ends when a button is pressed.

# Turn off all lights and end script
def shutOff():
    for i in range(60):
        strip.setPixelColorRGB(i, 0, 0, 0)
        strip.show()
        sleep(.02)
    #Shutdown this script
    raise SystemExit

# Turn off side lights
def waitMode():
    for i in range(36):
        strip.setPixelColorRGB(i, 0, 0, 0)
        strip.show()
        sleep(.05)
        
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

from threading import Timer
timer = Timer(45.0,waitMode)

# Strip and GPIO Setup
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
strip = Adafruit_NeoPixel(60, 18, 800000, 10, False, 255)
strip.begin()

# Increase Brightness. Random LED. 1 Color.
print("Increasing Brightness ...")
for a,b in pixelLoop(256,12):
    strip.setPixelColorRGB(random.randint(0,60),int(a/2),a,a)
    strip.show()
    sleep(.1)
    if GPIO.input(23) == 0: #Btn Press
        waitMode() #Turn off side
        for i in range(36,60): #Top to full brightness
            strip.setPixelColorRGB(i,128,255,255)
            strip.show()
            sleep(.05)
        break             

# Only if not already in waitMode
if strip.getPixelColor(0) != 0:
    # Make Sure Every LED is at full brightness
    for i in range(60):
        strip.setPixelColorRGB(i,128,255,255)
    strip.show()

    timer.start()

while True:
    # Shutdown on btn press
    if GPIO.input(23) == 0:
        timer.cancel()
        shutOff()
    sleep(0.1)

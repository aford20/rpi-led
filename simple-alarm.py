# This script is called by crontab at a certain time to function as an alarm clock.
# Random Leds slowly light up increasing brightness over 5 min. Script only ends when a button is pressed.

# Turn off all lights and end script
def shutOff():
    for r in range(2):
        for p in range(12):
            for i in range(strip.numPixels()):
                c = strip.getPixelColorRGB(i)
                strip.setPixelColorRGB(i,max(0,c.r-5),max(0,c.g-5),max(0,c.b-5))
            strip.show()
            sleep(0.02)
        sleep(.25)
        for p in range(12):
            for i in range(strip.numPixels()):
                c = strip.getPixelColorRGB(i)
                strip.setPixelColorRGB(i,max(0,c.r+5),max(0,c.g+5),max(0,c.b+5))
            strip.show()
            sleep(0.02)
        sleep(.25)
    sleep(1)
    for p in range(128):
            for i in range(strip.numPixels()):
                c = strip.getPixelColorRGB(i)
                strip.setPixelColorRGB(i,max(0,c.r-2),max(0,c.g-2),max(0,c.b-2))
            strip.show()
            sleep(0.02)
    #Shutdown this script
    raise SystemExit
        
# Generate Loop. j = max brightness. x = pixels per loop
def pixelLoop(j,x):
    for i1 in range(1,j):
        for i2 in range(x):
            yield i1, i2    

# Import Libriaries
from time import sleep
import random
import math

# Setup Button
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Import Config File
import os.path
import configparser
cfg = configparser.ConfigParser()
cfg.read(os.path.abspath(os.path.dirname(__file__))+'/config.conf')

# Use real length of strip if a second strip is virtually on same pin
if cfg.has_option('strip1','real_length'):
    length = cfg['strip1']['real_length']
else:
    length = cfg['strip1']['length']

# Setup Light Strip
from rpi_ws281x import *
strip = Adafruit_NeoPixel(int(length), int(cfg['strip1']['gpio_pin']), 800000, 10, False, 255,int(cfg['strip1']['channel']))
strip.begin()

# Increase Brightness. Random LED. 1 Color.
print("Increasing Brightness ...")
for a,b in pixelLoop(256,7):
    strip.setPixelColorRGB(random.randint(0,strip.numPixels()),int(a/2),a,a)
    strip.show()
    sleep(1 / math.ceil(a/12))
    if GPIO.input(23) == 0: #Break for Btn Press
        break             

print("Max Brightness")

while True:
    # Shutdown on btn press
    if GPIO.input(23) == 0:
        shutOff()
    GPIO.wait_for_edge(23, GPIO.FALLING)

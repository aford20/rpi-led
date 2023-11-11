#!/usr/bin/env python3
# The following code is directly copied from or slightly modified from the below source
#https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/LICENSE
class RGBW(int):
    def __new__(self, r, g=None, b=None, w=None):
        if (g, b, w) == (None, None, None):
            return int.__new__(self, r)
        else:
            if w is None:
                w = 0
            return int.__new__(self, (w << 24) | (r << 16) | (g << 8) | b)

    @property
    def r(self):
        return (self >> 16) & 0xff

    @property
    def g(self):
        return (self >> 8) & 0xff

    @property
    def b(self):
        return (self) & 0xff

    @property
    def w(self):
        return (self >> 24) & 0xff

def Color(red, green, blue, white=0):
    return RGBW(red, green, blue, white)

class PixelStrip:
	def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0, strip_type=None, gamma=None):
		self.mem = []
		for x in range(int(num)):
			self.mem.append(0)
     
	def begin(self):
		self.live = self.mem
    
	def show(self):
		self.live = self.mem
    
	def setPixelColor(self, n, color):
		self.mem[n] = color

	def setPixelColorRGB(self, n, red, green, blue, white=0):
		self.setPixelColor(n, Color(red, green, blue, white))
    
	def numPixels(self):
		return len(self.mem)

	def getPixelColor(self, n):
		return self.live[n]

	def getPixelColorRGB(self, n):
		return RGBW(self.live[n])
    
# Shim for back-compatibility
class Adafruit_NeoPixel(PixelStrip):
    pass
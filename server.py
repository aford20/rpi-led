#!/usr/bin/env python3
import cherrypy
from cherrypy.process.plugins import SimplePlugin
import os.path
from time import sleep
import re
import math
#---
import configparser
cfg = configparser.ConfigParser()
cfg.read(os.path.abspath(os.path.dirname(__file__))+'/config.conf')
#---
from string import Template

cherrypy.config.update({
		'server.socket_host' : '0.0.0.0',
		'server.socket_port' : 80
})

config = {
	'/' : {# Set up file paths
		'tools.sessions.on': True,
		'tools.staticdir.root':os.path.abspath(os.path.dirname(__file__)),
		'tools.staticdir.on': True,
		'tools.staticdir.dir' : "./",
		'tools.staticdir.index': "index.html"
		}
}

from threading import Timer, Thread
class RepeatedTimer(object):
	def __init__(self, interval, function, *args, **kwargs):
		self._timer     = None
		self.interval   = interval
		self.function   = function
		self.args       = args
		self.kwargs     = kwargs
		self.is_running = False
		self.start()

	def _run(self):
		self.is_running = False
		self.start()
		self.function(*self.args, **self.kwargs)

	def start(self):
		if not self.is_running:
			self._timer = Timer(self.interval, self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		self._timer.cancel()
		self.is_running = False

@cherrypy.popargs('transition')
class Main(object):
	def __init__(self):

		self.led_strips = []
		html_string = ""
		def init_strips(section):
			# Initialize Strips
			s = list(map(int, cfg[section]['length'].split(",")))
			l = PixelStrip(sum(s), int(cfg[section]['gpio_pin']), 800000, 10, False, 255,int(cfg[section]['channel']))
			l.begin()

			for x in range(len(s)):
				# Create Object
				self.led_strips.append(Strip(l, s[x], sum(s[0:x])))
				#Build HTML String
				nonlocal html_string 
				html_string += '<label><input type="checkbox">' + cfg[section]['name'].split(",")[x] + '</label>'

		init_strips("strip1")

		if cfg.has_section("strip2"):
			init_strips("strip2")

		# Save HTML Checkboxes
		self.strips_html = {"strip_chks":html_string}

		# Turn off LEDS on shutdown
		def engine_stop():
			for x in self.led_strips:
				thread = Thread(target = x.dissolve, args = ('000000', ))
				thread.start()
				sleep(0.01)

		# Register Shutdown Subscriber
		cherrypy.engine.subscribe('stop', engine_stop)

	# Serve Static Pages
	@cherrypy.expose(['Leds', 'Pattern','IALeds'])
	def staticHTML(self):
		path = cherrypy.request.path_info

		class subTemplate(Template):
			delimiter = "$%^"
		
		f = open(os.path.abspath(os.path.dirname(__file__))+path + ".html", "r")
		html = subTemplate(f.read())
		f.seek(0)
		f.close()
		
		return html.safe_substitute(self.strips_html)

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def staticLive(self,transition,color='',strips = '0'):
		if color == '':
			try:
				d = cherrypy.request.json
				color = d['color']
				strips = str(d['strips'])
			except:
				color = ['110011']

		# Split Strips apart and convert to integers
		strips = list(map(int, strips.split(",")))

		if transition == 'take':
			for x in strips:
				self.led_strips[x].take(color)
		elif transition == 'dissolve':
			threads = {}
			for x in strips:
				threads[x] = Thread(target = self.led_strips[x].dissolve, args = (color, ))
				threads[x].start()
		elif transition == 'wipe':
			threads = {}
			for x in strips:
				threads[x] = Thread(target = self.led_strips[x].wipe, args = (color, ))
				threads[x].start()
		else:
			print("Unable to match function " + transition)
		
		try:
			threads[strips[0]].join() # Wait for first strip to finish
		finally:
			if isinstance(color,list):
				return self.led_strips[strips[0]].getStripColor()
			elif isinstance(color, str):
				return self.led_strips[strips[0]].getPixelColor(0)

	# Single Color Mode, Update Function
	@cherrypy.expose
	def returnColor(self, strip=0):
		return self.led_strips[int(strip)].getPixelColor(0)

	# IA Mode, Update Function
	@cherrypy.expose
	@cherrypy.tools.json_out()
	def IAreturn(self,strip=0):
		return self.led_strips[int(strip)].getStripColor()

	# Patterns
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def pattern(self,transition,data='',strips = '0'):
		if data == '':
			try:
				d = cherrypy.request.json
				data = d['color']
				strips = d['strips']
			except:
				data = ['110011,110000']
		elif type(data) == str:
			data = data.split(",")

		# Split Strips apart and convert to integers
		strips = list(map(int, strips.split(",")))
		interval = float(data[0])
		pattern = data[slice(1,len(data))]
		
		for x in strips:
			thread = Thread(target = self.led_strips[x].pattern, args = (pattern, interval, transition))
			thread.start()

	# Special Rainbow Endpoint
	@cherrypy.expose
	def rainbow(self,transition=0.1, strips='0'):
		yield('Rainbow Fade Endpoint. Transition Time: ' + str(transition))
		strips = list(map(int, strips.split(",")))
		for x in strips:
			thread = Thread(target = self.led_strips[x].rainbow, args = (transition,))
			thread.start()

	# Alarms
	@cherrypy.expose
	def getAlarms(self):
		cron = CronTab(user='root')
		jobs = ""
		for job in cron.find_comment(re.compile('alarm')):
			jobs += str(job) + "$"
		jobs = jobs[slice(0,-1)]
		return jobs

	# Remove Alarm
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def RemoveAlarm(self):
		# Get Data
		data = cherrypy.request.json

		# Setup Cron
		cron = CronTab(user='root')

		# Find Job
		for job in cron.find_comment(re.compile('ID' + str(data))):
			cron.remove(job)
		cron.write()

		return Main.getAlarms(self)

	# Save Alarm
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def SaveAlarm(self):
		# Get Data
		data = cherrypy.request.json
		# Setup Cron
		cron = CronTab(user='root')

		ID = data[slice(0,1)]
		alarm = data[slice(2,None)]

		# Find Job
		for job in cron.find_comment(re.compile('ID' + str(ID))):
			print(job)
		try: # Throw error if no job ...
			job.clear()
		except: # ... So create one
			job = cron.new(command = 'sudo python3 ' + os.path.abspath(os.path.dirname(__file__)) + '/simple-alarm.py' , comment='alarm ID' + str(ID))
		finally: # Edit properties

			# Check enabled state
			if alarm[slice(0,1)] == "#":
				alarm = alarm[slice(2,None)]
				job.enable(False)
			else:
				job.enable(True)

			# Change and save path if delay
			if alarm.split(" ")[5] == "true":
				path = os.path.abspath(os.path.dirname(__file__)) + '/alarmDelay.py'
				# Remove Delay from string
				alarm = alarm[slice(-5)]
			# Path if not delay
			else:
				path = os.path.abspath(os.path.dirname(__file__)) + '/simple-alarm.py'
				# Remove Delay from string
				alarm = alarm[slice(-6)]
			job.set_command("sudo python3 " + path)

			# Check for one-time run
			if alarm.split(" ")[4] == "*":
				job.set_comment("alarm ID" + str(ID))
				job.set_command("sudo python3 " + path + ' && sudo python3 ' + os.path.abspath(os.path.dirname(__file__)) + '/DeleteJob.py ' + str(ID))

			# Add all other properties
			job.setall(alarm)

		# Save
		cron.write()
		return Main.getAlarms(self)

	# Shutdown server function
	def ServerOff():
		#os.system('ifconfig wlan0 down')	# Shutdown Wifi
		cherrypy.engine.exit()

	cherrypy.tools.ServerOff = cherrypy.Tool('on_end_request', ServerOff) # Hook function to tool. End request to allow return to send before wifi goes down.

	# Shutdown Server Endpoint
	@cherrypy.expose
	@cherrypy.tools.ServerOff() # Connect Endpoint to tool
	def shutdown(self):
		return

	# Shutdown Raspberry Pi Endpoint
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def PiOff(self):
		data = cherrypy.request.json
		passwd = "kklla"

		if data == passwd:
			os.system('sudo shutdown')
			yield "Raspberry Pi shutting down in about a minute ... "
			cherrypy.engine.exit()
		else:
			return "Incorrect Password"

# LED Strip Object
class Strip():
	def __init__(self, strip, length, offset=0):
		self.strip = strip
		self.numPixels = length
		self.offset = offset

		def stuff(): # Setup the animation timer. It needs some function
			pass # and the others in the class don't exist yet
		self.animate = RepeatedTimer(100, stuff)
		self.animate.stop()

	def preprocess(self, color):
		if type(color) == str:
			c = [color]
		else:
			c = []
			for a in range(len(color)):
				c.append(color[a])
		
		# Make sure there is data for each pixel
		while len(c) < self.numPixels:
			c += c
		c[:self.numPixels]
		
		self.animate.stop() # Stop Animations

		return c

	def take(self, color):
		c = self.preprocess(color)

		for i in range(self.numPixels):
			self.strip.setPixelColor(self.offset+i,int(c[i],16))
		self.strip.show()

	def dissolve(self, color, sleep_length=0.01):
		color2 = self.preprocess(color)
		color1 = []
		for i in range(self.numPixels):
			# Get Current Color and pad with zeros - [-6:] = slice -6
			color1.append(("000000" + str(format(self.strip.getPixelColor(i),'x')))[-6:])

		# Set Changes
		for j in range(51):

			# Function to calculate value
			def sliceDiff(start, stop, index):
				# Calculate Before/After Difference for each GRB
				val = int(color2[index][slice(start,stop)],16) - int(color1[index][slice(start,stop)],16)
				# Add % of difference to color1
				val = int(int(color1[index][slice(start,stop)],16) + val*(0.02*j))
				return val

			# Set Color on Strip
			for i in range(self.numPixels):
				self.strip.setPixelColorRGB(self.offset+i,sliceDiff(0,2,i),sliceDiff(2,4,i),sliceDiff(4,6,i))
			self.strip.show()
			sleep(sleep_length)
	
	def wipe(self,color):
		c = self.preprocess(color)
		for i in range(self.numPixels):
			self.strip.setPixelColor(self.offset+i,int(c[i],16))
			self.strip.show()
			sleep(self.numPixels/7500*math.cos(i/(self.numPixels/6.28))+.015)

	def getPixelColor(self, num):
		# Get Strip Color and format as Hex
		result = ("000000" + str(format(self.strip.getPixelColor(self.offset+0),'x')))[-6:]
		return result
	
	def getStripColor(self):
		result = []
		for i in range(self.numPixels):
			result.append(("000000" + str(format(self.strip.getPixelColor(i),'x')))[-6:])
		return result

	def pattern(self,pattern,interval,transition):
		#self.preprocess(color)
		
		self.animate.stop()

		shift = 0
		def Animation(t): # Run the Animations
			nonlocal shift
			shift = (shift+1) if shift < len(pattern)-1 else 0 #Increment Counter

			if t == 'allTake':
				for i in range(self.numPixels):
					self.strip.setPixelColor(self.offset+i,int(pattern[shift],16))
				self.strip.show()
			elif t == 'wipe':
				myNum = shift # Make copy because of simultanous instances
				# Wipe code
				for i in range(self.numPixels):
					self.strip.setPixelColor(self.offset+i,int(pattern[myNum],16))
					self.strip.show()
					sleep(self.numPixels/7500*math.cos(i/(self.numPixels/6.28))+.015)
			elif t == 'take' or t == 'dissolve':
				for x in range(self.numPixels):
					if x+shift < len(pattern):
						self.strip.setPixelColor(self.offset+x,pattern[x+shift])
					else:
						self.strip.setPixelColor(self.offset+x,pattern[x+shift-len(pattern)])
				self.strip.show()
			elif t == 'allDissolve':
				for i in range(self.numPixels):
					self.strip.setPixelColor(self.offset+i,pattern[shift])
				self.strip.show()
			elif t == 'fadeOut':
				if shift >= stoplength:
					self.animate.stop()
				myNum = shift # Make copy because of simultanous instances
				# Wipe code
				for i in range(self.numPixels):
					self.strip.setPixelColor(self.offset+i,pattern[myNum])
					self.strip.show()
					sleep(self.numPixels/7500*math.cos(i/(self.numPixels/6.28))+.015)

		if transition == 'take': # Clone pattern for take
			for i in range(len(pattern)): # Convert to decimal
				pattern[i] = int(pattern[i],16)
			while len(pattern) < self.numPixels: # Duplicate for each pixel
				pattern += pattern
		elif transition == 'dissolve' or transition == 'allDissolve'  or transition == 'fadeOut': # Compute Pattern for Dissolve
			pattern.append(pattern[0]) # Add extra stop to fade back to beginning

			if transition == 'dissolve':
				stoplength = int(self.numPixels/(len(pattern)-2))
				interval = interval/25 # Speed up
			elif transition == 'fadeOut':
				stoplength = 256
			else:
				stoplength = int(interval/0.05)
				interval = 0.05

			# Calculate colors between stops
			def sliceDiff(color1,color2,start, stop, index):
				val = int(color2[slice(start,stop)],16) - int(color1[slice(start,stop)],16) # Calculate Before/After Difference for each RGB
				return int(int(color1[slice(start,stop)],16) + val*(1/stoplength*index)) # Add % of difference to color1

			ComputedStrip = []
			for s in range(len(pattern)-1): # Generate ComputedStrip
				color1 = pattern[s]
				color2 = pattern[s+1]
				for x in range(stoplength):
					ComputedStrip.append((sliceDiff(color1,color2,0,2,x)<<16) + (sliceDiff(color1,color2,2,4,x)<<8) + sliceDiff(color1,color2,4,6,x))
					try:
						if format(ComputedStrip[-1],'x') == format(ComputedStrip[-2],'x'):
							ComputedStrip.pop()
					except:
						pass
			pattern = ComputedStrip
			del ComputedStrip

			if transition == 'fadeOut':
				stoplength = len(pattern)/2
				interval = interval*60/stoplength # Multiply minutes by seconds and divide length

			prestrip = []
			if transition == 'allDissolve' or transition == 'fadeOut':
				for x in range(self.numPixels):
					prestrip.append(("000000" + str(format(pattern[0],'x')))[-6:])
			else:
				for x in range(self.numPixels):
					prestrip.append(("000000" + str(format(pattern[x],'x')))[-6:])
			self.dissolve(prestrip) # Predissolve to avoid jump

		if interval != 0:
			del self.animate
			self.animate = RepeatedTimer(interval, Animation, transition)
		thread = Thread(target = Animation, args = (transition, ))
		thread.start()

	def rainbow(self, transition_duration):
		self.animate.stop()
		def wheel(pos):
			"""Generate rainbow colors across 0-255 positions."""
			if pos < 85:
				return Color(pos * 3, 255 - pos * 3, 0)
			elif pos < 170:
				pos -= 85
				return Color(255 - pos * 3, 0, pos * 3)
			else:
				pos -= 170
				return Color(0, pos * 3, 255 - pos * 3)

		j = 0
		def Fade():
			nonlocal j
			for i in range(6): # Loop through each row
				for x in range(10): # Loop through each pixel in the row
					# Change the number multplied by i in the wheel function to change the difference between rows
					self.strip.setPixelColor(self.offset+10*i+x, wheel((i*10+j) & 255))
			self.strip.show()
			j = (j+1) if j < 255 else 0 #Increment Counter

		del self.animate
		self.animate = RepeatedTimer(float(transition_duration), Fade)
		Fade()

def beginServer(): 
	''' Start Server Normally'''
	global PixelStrip, CronTab
	from rpi_ws281x import PixelStrip
	from crontab import CronTab

def beginDummy():
	''' Start Server with emulated LEDs and without Cron '''
	global PixelStrip
	from dummyLeds import PixelStrip
	startup()

def startup():
	cherrypy.tree.mount(Main(), '/', config)
	
	if cfg.has_section("https"):
		HTTPS_SERVER = cherrypy._cpserver.Server()
		HTTPS_SERVER.socket_port = 443
		HTTPS_SERVER._socket_host = '0.0.0.0'
		HTTPS_SERVER.ssl_module = 'builtin'
		HTTPS_SERVER.ssl_certificate = cfg["https"]["certificate_path"]
		HTTPS_SERVER.ssl_private_key = cfg["https"]["key_path"]
		HTTPS_SERVER.subscribe()

	cherrypy.engine.start()
	cherrypy.engine.block()


if __name__ == '__main__':
	beginServer()
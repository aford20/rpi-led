#!/usr/bin/env python3
import cherrypy
from cherrypy.process.plugins import SimplePlugin
import os.path
from time import sleep
import re
import math

cherrypy.config.update({
		'server.socket_host' : '0.0.0.0',
		'server.socket_port' : 80
		#,'engine.autoreload.on' : False
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

	def __init__(self, length, pin,channel):
		'''self.strip = Adafruit_NeoPixel(length, pin, 800000, 10, False, 255,channel)
		self.strip.begin()
		self.strip.setPixelColorRGB(length-1,0,1,0)
		self.strip.show()'''

		def stuff(): # Setup the animation timer. It needs some function
			pass # and the others in the class don't exist yet
		self.animate = RepeatedTimer(100, stuff)
		self.animate.stop()

		self.strip = []
		for a in range(60):
			self.strip.append("000000")

		self.subscribeShutdown() # Not sure why it has to be like this but things get wacky if it isn't

	# Subscribe to engine activity so it can shutdown nicely
	def subscribeShutdown(self):
		self.turnOff(cherrypy.engine,self).subscribe()

	@cherrypy.expose
	@cherrypy.popargs('state')
	def isSync(self,state):
		print(state)
		if state == 'True':
			cherrypy.engine.subscribe("sync", self.syncer)
		else:
			cherrypy.engine.unsubscribe("sync", self.syncer)

	def syncer(self,epoint,t,data=''):
		#self.bus.log('got sync stuff')
		#print(t)
		if epoint == 'static':
			self.staticLive(t,data,False)
		elif epoint == 'pattern':
			self.pattern(t,data,False)
		elif epoint == 'rainbow':
			self.rainbow(transition=t,sync=False)

	@cherrypy.expose
	@cherrypy.tools.json_in()
	def staticLive(self,transition,override='',sync=True):
		if override == '':
			try:
				data = cherrypy.request.json
			except:
				data = ['110011']
		else:
			if type(override) == str:
				data = [override]
			else:
				data = []
				for a in range(len(override)):
					data.append(override[a])

		# Stop Pattern
		self.animate.stop()

		# Make sure there is data for each pixel
		while len(data) < 60:
			data += data
		data[:60]

		self.strip = data

	# Single Color Mode, Update Function
	@cherrypy.expose
	def returnColor(self):
		return self.strip[0]

	# IA Mode, Update Function
	@cherrypy.expose
	def IAreturn(self):
		live = ""
		for i in range(60):
			live += str(self.strip[i])
		return live

	# Patterns
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def pattern(self,transition,override='',sync=True):
		if override == '':
			try:
				data = cherrypy.request.json
			except:
				data = ['110011,110000']
		else:
			if type(override) == str:
				data = [override]
			else:
				data = []
				for a in range(len(override)):
					data.append(override[a])

		self.animate.stop()
		del self.animate

		interval = float(data[0])
		pattern = data[slice(1,len(data))]

		shift = 0
		def Animation(t): # Run the Animations
			nonlocal shift
			shift = (shift+1) if shift < len(pattern)-1 else 0 #Increment Counter

			if t == 'allTake':
				for i in range(60):
					self.strip[i] = pattern[shift]
			elif t == 'wipe':
				myNum = shift # Make copy because of simultanous instances
				# Wipe code
				for i in range(60):
					self.strip[i] = pattern[myNum]
					sleep(60/7500*math.cos(i/(60/6.28))+.015)
			elif t == 'take' or t == 'dissolve':
				for x in range(60):
					if x+shift < len(pattern):
						#self.strip[x] = pattern[x+shift]
						self.strip[x] = ("000000" + str(format(pattern[x+shift],'x')))[-6:]
					else:
						self.strip[x] = ("000000" + str(format(pattern[x+shift-len(pattern)],'x')))[-6:]
			elif t == 'allDissolve':
				for i in range(60):
					self.strip[i] = ("000000" + str(format(pattern[shift],'x')))[-6:]

		if transition == 'take': # Clone pattern for take
			for i in range(len(pattern)): # Convert to decimal
				pattern[i] = int(pattern[i],16)
			while len(pattern) < 60: # Duplicate for each pixel
				pattern += pattern
		elif transition == 'dissolve' or transition == 'allDissolve': # Compute Pattern for Dissolve
			pattern.append(pattern[0]) # Add extra stop to fade back to beginning

			if transition == 'dissolve':
				stoplength = int(60/(len(pattern)-2))
				interval = interval/25 # Speed up
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
			pattern = ComputedStrip
			del ComputedStrip

		if interval != 0:
			self.animate = RepeatedTimer(interval, Animation, transition)
		thread = Thread(target = Animation, args = (transition, ))
		thread.start()

		# Sync Message
		if sync:
			cherrypy.engine.publish('sync','pattern',transition,data)

	# Special Rainbow Endpoint
	@cherrypy.expose
	def rainbow(self,transition=0.1,sync=True):
		print('here')
		yield('Rainbow Fade Endpoint. Transition Time: ' + str(transition))
		self.animate.stop()
		def Color(red, green, blue, white=0):
		    """Convert the provided red, green, blue color to a 24-bit color value.
		    Each color component should be a value 0-255 where 0 is the lowest intensity
		    and 255 is the highest intensity.
		    """
		    return (white << 24) | (red << 16) | (green << 8) | blue

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
					self.strip[10*i+x] =  ("000000" + str(format(wheel((i*10+j) & 255),'x')))[-6:]
			j = (j+1) if j < 255 else 0 #Increment Counter

		del self.animate
		self.animate = RepeatedTimer(float(transition), Fade)
		Fade()

		# Sync Message
		if sync:
			cherrypy.engine.publish('sync','rainbow',transition)

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
		print(data)

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
			job = cron.new(command = 'sudo python ' + os.path.abspath(os.path.dirname(__file__)) + '/alarm.py' , comment='alarm ID' + str(ID))
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
				path = os.path.abspath(os.path.dirname(__file__)) + '/alarm.py'
				# Remove Delay from string
				alarm = alarm[slice(-6)]
			job.set_command("sudo python " + path)

			# Check for one-time run
			if alarm.split(" ")[4] == "*":
				job.set_comment("alarm ID" + str(ID))
				job.set_command("sudo python " + path + ' && sudo python ' + os.path.abspath(os.path.dirname(__file__)) + '/DeleteJob.py' + str(ID))

			# Add all other properties
			job.setall(alarm)

		# Save
		cron.write()
		return Main.getAlarms(self)

	# Shutdown Server Endpoint
	@cherrypy.expose
	def shutdown(self):
		self.animate.stop()		# Stop Pattern
		#os.system('ifconfig wlan0 down')	# Shutdown Wifi
		cherrypy.engine.exit()

	# Shutdown Raspberry Pi Endpoint
	@cherrypy.expose
	@cherrypy.tools.json_in()
	def PiOff(self):
		data = cherrypy.request.json
		passwd = "kklla"

		if data == passwd:
			os.system('sudo shutdown')
			#os.system('sudo shutdown -c')
			yield "Raspberry Pi shutting down in about a minute ... "
			self.shutdown()
		else:
			return "Incorrect Password"

	# Class to catch engine exit and turn off things nicely
	class turnOff(SimplePlugin):
		def __init__(self, bus, main_class, sleep = 2):
			SimplePlugin.__init__(self, bus)
			self.outer = main_class
		'''
		def start(self):
			self.bus.log('Starting Sync Listener')
			self.bus.subscribe("sync", self.syncer)

		def syncer(self,t,data):
			self.bus.log('got sync stuff')
			#print(t)
			#print(data)
			self.outer.staticLive(t,data,False)'''

		def stop(self):
			'''Called when the engine stops'''
			self.outer.animate.stop() # Stop animations

		def exit(self):
			'''Called when the engine exits'''
			sleep(1) # wait for queued animations to complete/stop
			self.outer.staticLive('dissolve',override='000000') # Clear on exit
			self.unsubscribe() # unsubscribe from engine activity

if __name__ == '__main__':
	cherrypy.tree.mount(Main(60,18,0), '/', config) # Main Thread
	sleep(1)
	#cherrypy.tree.mount(Main(50,13,1), '/aux1', config) # Secondary
	cherrypy.engine.start()
	cherrypy.engine.block()

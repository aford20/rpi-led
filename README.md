# rpi-led

This is a project I have been working on since 2018. It is for a LED light strip to be driven by a Raspberry Pi. While I have "borrowed" a few snippets of code here and there, this work is almost entirely my own. It features lots of cool effects and the ability to manage alarms. Plus its mobile friendly too. More info to come later.

# Setup
1. Install pip3 if you do not already have it by running ```sudo apt install python3-pip```
2. This project requires a few other packages. rpi_ws281x is the library used to control the LED Strip. cherrypy is powers the local server, and python-crontab is used to access CronTab to schedule alarms. Install them by executing ``` sudo pip3 install rpi_ws281x cherrypy python-crontab ```

# Customizing It
There is plenty of documentation out there on wiring up LED Strips with the Raspberry Pi. To save time, I'll just explain how to get this library working. After your strip is all wired up, you'll want to start by scrolling down to the very bottom of ```server.py``` until you find a line like this:
```cherrypy.tree.mount(Main(60,18,0), '/', config) # Main Thread ```

Now, this line of code is not actually initializing the LED strip. It's passing three arguments through to the object Main() which will be used to setup the strip. The first argument is the number of pixels in the strip and the second is the pin number. The third is the channel. You can find more info on channels in official rpi documentation, but unless you are driving two separate strips from two separate pins, you can leave the channnel at 0. So in the example above, I have a strip of 60 pixels connected to pin 18. But if instead I had 210 pixels connected to pin 13, I would write the line as
```cherrypy.tree.mount(Main(210,13,0), '/', config) # Main Thread ``` 

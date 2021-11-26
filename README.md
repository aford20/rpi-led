# rpi-led

This is a project I have been working on since 2018. It is for a LED light strip to be driven by a Raspberry Pi. While I have "borrowed" a few snippets of code here and there, this work is almost entirely my own. It features lots of cool effects and the ability to manage alarms. Plus its mobile friendly too. More info to come later.

# Setup
1. Install pip3 if you do not already have it by running ```sudo apt install python3-pip```
2. This project requires a few other packages. rpi_ws281x is the library used to control the LED Strip. cherrypy powers the local server, and python-crontab is used to access CronTab to schedule alarms. Install them by executing ``` sudo pip3 install rpi_ws281x cherrypy python-crontab ```
3. You'll also need to clone or download this library

# Customizing It
There is plenty of documentation out there on wiring up LED Strips with the Raspberry Pi. I'll just explain how to get this library working. After your strip is all wired up, you'll want to start by opening ```config.conf``` in the root of this directory. Many of the scripts refer to this file for strip setup. Find the heading ```[strip1]``` and adjust the length and gpio_pin as necessary. You can find more info on channels in official rpi documentation, but unless you are driving two separate strips from two separate pins, you can leave the channnel at 0. If you are driving two separate strips, also modify the variables under the ```[strip2]``` section and uncomment the line at the end of ```server.py``` that begins with
```cherrypy.tree.mount(Main(```...

# Starting the Server
Start the server by navigating to the directory in the terminal and executing
```sudo python3 server.py```

*Depending on your python configuration you may be able to run "sudo python server.py" instead.*

*Use Ctrl+C to stop the server*

The server is ready once you see the line "ENGINE Bus STARTED". The line above that tells you where can access the server from. If it says 127.0.0.1, that means you can only access it using that address from the computer the server is operating on. If it says 0.0.0.0, you can access it from any computer, as long as you know the IP address.

Find your IP address by typing ```ifconfig``` in the terminal. You're looking for the inet property, which will be followed by a number like 192.168.1.7 .  If you're using wifi it will likely be in the third paragraph and ethernet will likely be in the first paragraph. Once you find your IP Address, remember it or write it down somewhere. With the server running, you can enter the IP address into any browser on your local network and access and control your lights.

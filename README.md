# rpi-led

Control LED Light Strips attached to your Raspberry Pi from any device on your local network. Featuring lots of cool effects, light alarms, mobile friendly UI, and a Progressive Web App if served over HTTPS.

This is a project I have been working on and off with since 2018. While I have "borrowed" a few snippets of code here and there, this work is almost entirely my own.

# Setup
1. Install pip3 if you do not already have it by running ```sudo apt install python3-pip```
2. This project requires a few other packages. rpi_ws281x is the library used to control the LED Strip. cherrypy powers the local server, and python-crontab is used to access CronTab to schedule alarms. Install them by executing ``` sudo pip3 install rpi_ws281x cherrypy python-crontab ```
3. You'll also need to clone or download this library

# Configuration
This is designed for individually addressable LED strips like the Adafruit Neopixels or generic WS281B strips. There is plenty of documentation out there on the hardware side of wiring up LED Strips with the Raspberry Pi. I'll just explain how to get this part working. 

In order for this library to work you need to create a file named `config.conf` in the root of this directory. Many of the scripts refer to this file for strip setup. Create a section named `[strip1]`. Beneath this you will define the attributes of the strip as key pairs. **The following are required: length, gpio_pin, channel, and name**. Here's an example:

```
[strip1]
name = Corkboard Perimeter
length = 60
gpio_pin = 18
channel = 0
```

If you have a second strip on a second pin repeat with a `[strip2]` section. To seperate multiple strips driven from the same pin, use a comma in the length and name fields. See sample.conf for more details.

Each strip requires length and gpio_pin as necessary. You can find more info on channels in official rpi documentation, but unless you are driving two separate strips from two separate pins, you can leave the channnel at 0. 

To serve via https add a `[https]` section to config.conf like so:
```
[https]
certificate_path = /absolute/path/to/certificate.crt
key_path = /path/to/private.key
```

# Starting the Server
Start the server by navigating to the directory in the terminal and executing
```sudo python3 server.py```

*Depending on your python configuration you may be able to run "sudo python server.py" instead.*

*Use Ctrl+C to stop the server*

The server is ready once you see the line "ENGINE Bus STARTED". You should be able to access it from any computer on your local network by typing the IP address or hostname into your browser.
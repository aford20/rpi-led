# This script is similar to alarm.py. This script checks the WGAL webpage for delays before turning on lights
# Random Leds slowly light up increasing brightness over 5 min. Script ends when a button is pressed.

import urllib2
import os
from time import sleep

os.system('rfkill unblock wifi') # Unblock wifi
os.system('ifconfig wlan0 up') # Turn wifi on
sleep(15) # wait for wifi to connect

# Check for Delay
try:
    # Retrieve the contents of WGAL closings page
    contents = urllib2.urlopen("https://www.wgal.com/weather/closings").read()

    # This is not the live page. It is an archived version that can be used for testing.
    #contents = urllib2.urlopen("https://web.archive.org/web/20180117165939/http://www.wgal.com/weather/closings").read()

    # Search page for keyword "Donegal"
    result = contents.find("Donegal")

    #print(result)
    #print(contents[result-30:result+40])


# Handle Errors
except:
    print("There was an issue reading the contents of WGAL.com. Check network connections.")
    result = -1 # Set result to negative one for fallback so that script still runs


# Execute Code
finally:
        try:
            # Continue if found nothing. -1 is return for no result.
            if result == -1:
                # Run alarm script
                import alarm
        finally:
            os.system('ifconfig wlan0 down') # Turn wifi off        
            

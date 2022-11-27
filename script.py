#import the GPIOS library
import RPi.GPIO as GPIO
#import the time library
from time import sleep
#import the dht11 library
import dht11

# read data using pin 11
instance = dht11.DHT11(pin = 11)
#The channel for the Moisture detector
channel = 21
#GPIO SETUP
GPIO.setwarnings(False)
#This means we will refer to the GPIO pins
GPIO.setmode(GPIO.BCM)
#This sets the GPIO 18 pin as an output pin. This is for the relay.
GPIO.setup(18, GPIO.OUT)
#Setup moisture sensor GPIO pin
GPIO.setup(channel, GPIO.IN)
 

#A callback function that triggers the relay controlling the pump when there is a change in the moisture detector
def callback(channel):
        if GPIO.input(channel):
                GPIO.output(18, 0)
                print("No water detected")
        else:
                GPIO.output(18, 1)
                print("Water detected")

 
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=100)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

#An infinite loop runs that will get a reading of the humidity and temperature every 10 seconds and allow the callback function to run.
while True:
    result = instance.read()
    """
    There is an issue where sometimes the temp & humidity return 0, so in order to counteract that there is the new & old temp/humidity so if 
    the new temp/humidity is 0 the old temp/humidity value is returned. This is okay because the temperature and humidity should not 
    have a dramatic change in just 10 seconds so the readings should still be accurate. 
    """
    newTemp = "Temperature: %-3.1f C" % result.temperature
    newHumidity = "Humidity: %-3.1f %%" % result.humidity
    if (newTemp == "Temperature: 0.0 C" and newHumidity == "Humidity: 0.0 %"):
        newTemp = oldTemp
        newHumidity = oldHumidity
    else:
        oldTemp = newTemp
        oldHumidity = newHumidity    

    print(newTemp)
    print(newHumidity)
    sleep(10)

    

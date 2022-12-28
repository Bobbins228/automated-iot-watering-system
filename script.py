#import the GPIOS library
import RPi.GPIO as GPIO
#import the time library
from time import sleep
#import the dht11 library
import dht11
#import confluent kafka library
from confluent_kafka import Producer
#import load_dotenv from dotenv library
from dotenv import load_dotenv
#import os
import os
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
 
load_dotenv(".env")

#Gathers sensitive data from the .env file
bootstrap_server = os.getenv("BOOTSTRAP_SERVER")
sasl_user_name = os.getenv("CLIENT_ID")
sasl_password = os.getenv("CLIENT_SECRET")

#Set up the Kafka producer
p = Producer({
      'bootstrap.servers': bootstrap_server,
      'security.protocol': 'SASL_SSL',
      'sasl.mechanisms': 'PLAIN',
      'sasl.username': sasl_user_name,
      'sasl.password': sasl_password,
    }
  )

#Prints confirmed/failed produced messages
def delivery_report(err, msg):
  """ Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush(). """
  if err is not None:
    print('Message delivery failed: {}'.format(err))
  else:
    print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

#A callback function that triggers the relay controlling the pump when there is a change in the moisture detector
def callback(channel):
        if GPIO.input(channel):
                GPIO.output(18, 0)
        else:
                GPIO.output(18, 1)

 
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=100)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

#An infinite loop runs that will get a reading of the humidity and temperature every 10 seconds and allow the callback function to run.
#Produces humididity and temperature data to the kafka instance
while True:
    result = instance.read()
    newTemp = "Temperature: %-3.1f C" % result.temperature
    newHumidity = "Humidity: %-3.1f %%" % result.humidity
    if (newTemp == "Temperature: 0.0 C" and newHumidity == "Humidity: 0.0 %"):
        newTemp = oldTemp
        newHumidity = oldHumidity
    else:
        oldTemp = newTemp
        oldHumidity = newHumidity   
    
    p.poll(0)
    # Asynchronously produce a message. The delivery report callback will
    # be triggered from the call to poll() above, or flush() below, when the
    # message has been successfully delivered or failed permanently.
    
    p.produce('temperature', newTemp.encode('utf-8'), callback=delivery_report)
    p.produce('humidity', newHumidity.encode('utf-8'), callback=delivery_report)
    # Wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered.
    p.flush()
    sleep(10)
    

import RPi.GPIO as GPIO
from time import sleep
import dht11
from confluent_kafka import Producer
from dotenv import load_dotenv
import os
import datetime
import pymongo
from dateutil.parser import parse
import schedule

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

#Connect to Mongo Atlas and set the database to plant-profile and collection to profile
client = pymongo.MongoClient(os.getenv("MONGO_STRING"))
db = client["plant-profile"]
collection = db["profile"]

myquery = { "_id": 1 }


# Find a specific profile in the collection and sets it to the profile variable
profile = collection.find_one({"_id": 1})

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

#Watering function will water the plants for 4 seconds and update the last date watered on the plant profile
def watering():
  GPIO.output(18, 0)
  sleep(4)
  GPIO.output(18, 1)
  newvalues = { "$set": { "date-last-watered": datetime.datetime.now().date().strftime('%d-%m-%Y') } }
  collection.update_one(myquery, newvalues)


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
                newvalues = { "$set": { "date-last-watered": datetime.datetime.now().date().strftime('%d-%m-%Y') } }
                collection.update_one(myquery, newvalues)
        else:
                GPIO.output(18, 1)
                

#If the plant profile is set to moisture, the script will water the plant based on soil moisture
if profile.get("watering-type") == "moisture":
  GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=100)  # let us know when the pin goes HIGH or LOW
  GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

#Schedule will run the watering function every monday
if profile.get("watering-type") == "weekly":
  schedule.every().monday.do(watering)

#Schedule will run the watering function every 2 weeks
if profile.get("watering-type") == "bi-weekly":
  schedule.every(2).weeks.do(watering)

#An infinite loop runs that will get a reading of the humidity and temperature every 10 seconds and allow the callback function to run.
#Produces humididity and temperature data to the kafka instance

while True:
    #Run scheduled watering
    schedule.run_pending()
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
    

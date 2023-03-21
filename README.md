# automated-iot-watering-system
### Abstract
The Automated IOT Plant Watering System is a watering system powered by a Raspberry Pi that is capable of watering plants without human intervention and is capable of being controlled by an Amazon Alexa. It is equipped with humidity, temperature and moisture sensors along with a submersible water pump.

A plant has its own profile hosted on Mongo Atlas which has it's name, watering type and last watering date. A user can alter the plant profile using a web app that is linked to the watering system. Real-time graphs of the room's humidity and temperature can be seen from the web app. The web app is containerized and hosted on Kubernetes.

The watering system can be set to different watering types consisting of moisture-based watering, weekly watering, bi-weekly watering and manual watering.

Using the watering system Alexa skill a user can ask it questions like "When did the plant get watered last" or "Change the watering type to weekly".
### Technologies
Raspberry Pi, Python, Flask, Kubernetes, Docker, Mongo, Apache Kafka, HTML, Alexa
### Related Repositories
[watering system web app](https://github.com/Bobbins228/watering-system-web-app)<br> [Alexa Water Bot Skill](https://github.com/Bobbins228/alexa-watering-bot-skill)

# OpenTherm monitoring using MQTT

This package translates the OpenTherm data transfers, as monitored by
the ESP OpenTherm MQTT gateway, into understandable MQTT topics and
messages. 

It provides auto-discovery of many (binary-)sensors for home-assistant.

## Requirements

Have the ESP OpenTherm gateway hardware installed running the 
[OpenTherm MQTT gateway software](https://github.com/joshuisken/ot_mqtt_esp) 

## Build/install

`python -m build`

`pip install .`

## Run

The program `otmqtt` needs a `otmqtt.ini` file with configuration settings and secrets.
An example is generated on the first invocation:

`$ otmqtt
Writing default config to 'mqtt_ot.ini'
Not connected to MQTT broker, did you fill-in credentials in 'mqtt_ot.ini'?
`

#! /usr/bin/env python3
""" Construction of HomeAssistant discovery messages for OpenTherm.


"""
import json
import logging

logger = logging.getLogger(__name__)

TPL = {
    "name": "Entity function",
    # for classifying non-primary entities https://developers.home-assistant.io/blog/2021/10/26/config-entity/
    # "entity_category": "diagnostic",
    "state_class": "measurement",
    "availability": [ {
        "topic": "esp/mqtt_ot/state",
        "payload_available": "online",
        "payload_not_available": "offline"
    }, {
        "topic": "otgw/state",
        "payload_available": "online",
        "payload_not_available": "offline"
    } ],
    "device": {
        "hw_version": "2024-08",
        "identifiers": [
            "esp_otgw_b4_e6_2d_14_28_ea"
        ],
        "manufacturer": "https://diyless.com/product/esp8266-opentherm-gateway",
        "model": "OpenTherm monitor DiyLess ESP8266",
        "name": "OpenTherm Gateway"
    },
    "origin": {
        "name": "OpenTherm2MQTT",
        "sw": "0.9",
        "url": "https://github.com/joshuisken/otgw2mqtt"
    }
}

class HassDiscovery(dict):

    def __init__(self, topic, payload, TPL=TPL):
        self |= TPL
        self |= payload
        self.topic = topic

    def __repr__(self):
        return f"Topic:   {self.topic}\nPayload: {json.dumps(self, indent=2)}"

    async def publish(self, client, retain=False):
        return await client.publish(self.topic, payload=json.dumps(self), retain=retain)

    pass


if __name__ == "__main__":
    import pprint
    hd = HassDiscovery("has/binary_sensor/OT/config", {"unit_of_measurement": "C"})
    pprint.pprint(hd)


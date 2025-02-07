#!/usr/bin/env python3
# pylint: disable=missing-type-doc
"""MQTT client for decoding OpenTerm protocol.

"""
import argparse
import asyncio
import configparser
import copy
import datetime
import logging
import paho.mqtt.client as mqtt
import aiomqtt
from io import StringIO
import json
import os
import re
import requests
import socket
import struct
import sys
import ssl
import traceback
from .opentherm import OpenThermApplProtocol
from .ot_registers import OT

from otmqtt import __version__

__author__ = "Jos Huisken"
__copyright__ = "Jos Huisken"
__license__ = "mit"


args = None  # Commandline arguments

telegram = None  # Telegram bot

online = False

# Message Cache
msgs_master = {}
msgs_slave = {}

t_esp = None

logger = None


class Telegram:
    """Booy12 bot."""

    def __init__(self, token, chat_id):
        self.TOKEN = token
        self.chat_id = chat_id
        return

    def send(self, message = f"hello from {sys.argv[0]}"):
        return
        url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage?chat_id={self.chat_id}&text={message}"
        js = requests.get(url).json()
        # print(js)
        return


def updated(frame, msgs):
    """Update data_value belonging to data_id if needed. Return true if updated.

    Not required anymore, since ESP code is doing this now.
    Collecting the msgs is still handy for the dump feature though.
    """
    reg = frame.data_id()
    val = frame.data_value()
    if reg in msgs and msgs[reg] == val:
        return False
    msgs[reg] = val
    return True


def desc_sent(frame):
    """Check if frame description has been sent."""
    global args, msgs_master, msgs_slave
    if not args.informative:
        return False
    reg = frame.data_id()
    if reg in msgs_master or reg in msgs_slave:
        return True
    return False

async def process_ms(client, message, cache, ms, ms_desc):
    """Process OT master/slave frame.

    If not yet sent:
    - sent a home-assistant auto-discovery msg
    - sent a description message
    For each OT-register:
    - only sent MQTT msg if value has changed
    """ 
    global config, logger
    th = config["MQTT"]["topic"]
    # Construct OT frame with factory function
    frame = OpenThermApplProtocol.from_frame(
        int(message.payload.decode("utf-8"), 16))
    if not frame.data_id() in cache:
        # Send homeassistant discovery message(s)
        await frame.mqtt_discovery(client, ms)
        logger.info(f"Discovery msg for {ms}_{frame.data_id()}")
    if not desc_sent(frame):
        # Send description, dataobject, and R/W info from spec
        t, p = frame.mqtt_desc()
        await client.publish(f"{th}/{t}", payload=p, retain=True)
        t, p = frame.mqtt_dataobject()
        await client.publish(f"{th}/{t}", payload=p, retain=True)
        t, p = frame.mqtt_rw()
        await client.publish(f"{th}/{t}", payload=p, retain=True)
    if updated(frame, cache):  # Side-effect: stored in cache
        # Only publish updated values
        t, p = frame.mqtt_msg(ms)
        await client.publish(f"{th}/{t}", payload=p)
        logger.debug(f"{ms_desc} updated transfer: {hex(frame.frame)} -> t={th}/{t} p={p}")
    return


async def process_slave(client, message):
    global msgs_slave
    await process_ms(client, message, msgs_slave, "s", "Slave ")
    return


async def process_master(client, message):
    global msgs_master
    await process_ms(client, message, msgs_master, "m", "Master")
    return


async def process_state(client, message):
    global online, logger
    m = message.payload.decode('utf-8')
    online = m.startswith('online')
    # telegram.send(f"OT State: {m}")
    logger.warning(f"Gateway state {m}")
    return


async def process_temp(client, message):
    global logger
    m = message.payload.decode('utf-8')
    # telegram.send(f"OT Temp: {m}")
    logger.info(f"Gateway temperature {m}")
    return


async def process_timeout(client, message):
    global logger
    m = message.payload.decode('utf-8')
    telegram.send(f"OT Active: {m}")
    logger.debug(f"OT timeout: {m}")
    return


async def process_dump_state(client, message):
    global logger, msgs_slave, msgs_master
    m = message.payload.decode('utf-8')
    with open("ot_master.json", "w") as f:
        f.write(json.dumps(dict(sorted(msgs_master.items())), indent=2))
    with open("ot_slave.json", "w") as f:
        f.write(json.dumps(dict(sorted(msgs_slave.items())), indent=2))
    # telegram.send(f"OT msgs in 'ot_master.json' and 'ot_slave.json'")
    with open("OT.json", "w") as f:
        json.dump(OpenThermApplProtocol.OT, f, indent=2)
    # telegram.send(f"OT table in 'OT.json'")
    logger.debug(f"Last master/slave transfers have been dumped in 'ot_master.json' and 'ot_slave.json'")
    return


async def clear_cache(client):
    """ Trigger:
    (Re-)Send all discovery messages for all available OpenTherm registers.
    By clearing the cache in ot_mqtt_esp.
    """
    global logger, msgs_master, msgs_slave
    msgs_master = {}
    msgs_slave = {}
    # AND clear the cache in ot_mqtt_esp
    global t_esp
    t, p = f"{t_esp}/cmd", "clear"
    await client.publish(t, payload=p)
    return


async def process_discovery(client, message):
    global logger, msgs_master, msgs_slave
    m = message.payload.decode('utf-8')
    logger.info(f"Homeassistant autodiscovery {m}")
    if m != "online":
        return
    await clear_cache(client)
    return


async def process_command(client, message):
    global logger
    m = message.payload.decode('utf-8')
    if m == "clear":
        await clear_cache(client)
    logger.debug(f"Cleared otmqtt cache and (Re)Send all discovery messages.")
    return


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="otmqtt",
        description="Send messages to Telegram bot Booy12 about OpenTherm.")
    parser.add_argument("-C", "--config", metavar="mqtt_ot.ini",
                        default="mqtt_ot.ini",
                        help=".ini file with MQTT settings (def. generated if non-existing)")
    parser.add_argument("-I", "--informative", action='store_true',
                        help="publish informative MQTT topics.")
    parser.add_argument("-V", "--version", action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument("-v", "--verbose", action='count', default=0,
                        help="verbose [multiple -v increase verbosity].")
    return parser.parse_args()


def read_config(args):
    config = configparser.ConfigParser()
    config["MQTT"] = {}
    config["MQTT"]["host"] = "localhost"
    config["MQTT"]["port"] = "1883"
    config["MQTT"]["tls"] = "False"
    config["MQTT"]["username"] = "XXXXX"
    config["MQTT"]["password"] = "XXXXX"
    config["MQTT"]["reconnect_interval"] = "240"
    config["MQTT"]["reconnect_max_trials"] = "4"
    config["MQTT"]["topic"] = "otgw"
    config["MQTT"]["lwt_message"] = "offline"
    config["MQTT"]["lwt_retain"] = "True"
    config["MQTT"]["OTGW_topic"] = "esp/mqtt_ot"
    config["MQTT"]["hass_discovery_prefix"] = "homeassistant"
    config["Telegram"] = {}
    config["Telegram"]["token"] = "666666666:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    config["Telegram"]["chat_id"] = "333333333"
    if not os.path.exists(args.config):
        print(f"Writing default config to '{args.config}'")
        with open(args.config, 'w') as f:
            config.write(f)
    else:
        config.read(args.config)
        # print(f"Read config from '{args.config}'")
    return config


async def mqtt_client(config):
    global args, telegram, logger

    # Use TLS, if required
    tls_params = aiomqtt.TLSParameters(
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
        ciphers=None,
    ) if config["tls"] == "True" else None

    # MQTT topic prefixes
    t_ot = config["topic"]
    global t_esp
    t_esp = config["OTGW_topic"]
    t_hass = config["hass_discovery_prefix"]

    # Construct last will and testament
    will = aiomqtt.Will
    will.topic = f"{t_ot}/state"
    will.payload = config["lwt_message"]
    will.retain = config["lwt_retain"] == "True"

    # All subscription tasks
    tasks = {
        # Dump the last state of all master/slave messages
        f"{t_ot}/dump": process_dump_state,
        f"{t_ot}/cmd": process_command,
        # OpenTherm gateway
        f"{t_esp}/state": process_state,
        f"{t_esp}/master": process_master,
        f"{t_esp}/slave": process_slave,
        f"{t_esp}/active": process_timeout,
        f"{t_esp}/temp": process_temp,
        # Homeassistant autodiscovery
        f"{t_hass}/status": process_discovery
    }

    # Prepare MQTT client
    reconnect_interval = int(config["reconnect_interval"])  # In seconds
    trials = maxtrials = int(config["reconnect_max_trials"])

    logger.info(f"Init: {online}")

    # Run the MQTT client and reconnect few times if needed
    while trials:  # True
        async with aiomqtt.Client(
                hostname=config["host"], port=int(config["port"]),
                username=config["username"], password=config["password"],
                protocol=mqtt.MQTTv5, tls_params=tls_params,
                logger=logger,
                will=will) as client:
            logger.info("Connected mqtt")
            await client.publish(f"{t_ot}/state", payload=f"online", retain=True)
            await client.publish(f"{t_ot}/trial", payload=f"{maxtrials - trials + 1}")
            # Clear the transfer cache in the OpenTherm gateway monitor
            await client.publish(f"{t_esp}/cmd", payload="clear")
            for k in tasks.keys():
                await client.subscribe(k)
            async for message in client.messages:
                logger.info(f"rcvd: {message.topic.value:20} {message.payload}")
                await tasks[message.topic.value](client, message)
        logger.warning(f"Trial {maxtrials - trials + 1}")
        await asyncio.sleep(reconnect_interval)
        trials -= 1
    logger.error(f'Giving up after {maxtrials} trials.')
    return 0
    

def main():
    global args, config, telegram, logger
    args = parse_arguments()
    config = read_config(args)

    OpenThermApplProtocol.hass_prefix = config["MQTT"]["hass_discovery_prefix"]
    OpenThermApplProtocol.OT = OT

    if args.verbose > 3:
        args.verbose = 3
    loglvl = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
    logging.basicConfig(filename = "mqtt_ot.log",
                        filemode = "w",
                        level = loglvl[args.verbose])
    logger = logging.getLogger("mqtt_ot")
    logger.info("Started")

    telegram = Telegram(config["Telegram"]["token"], config["Telegram"]["chat_id"])
    telegram.send(f"{sys.argv[0]}@{socket.gethostname()} started")

    try:
        asyncio.run(mqtt_client(config["MQTT"]))
    except aiomqtt.exceptions.MqttError as e:
        print(f"Not connected to MQTT broker, did you fill-in credentials in '{args.config}'?")
        return 1
    except asyncio.exceptions.CancelledError as e:
        print(f"{e}\nCancelled by what? KeyboardInterrupt?")
        return 2
    except KeyboardInterrupt as e:
        print(e)
        return 2
    logger.info("Finished")
    return 0


def run():
    """Entry point for console_scripts"""
    main()


if __name__ == "__main__":
    run()

#! /usr/bin/env python3
"""OpenTherm Protocol Specification v2.2

- data link layer:   class OpenThermProtocol
- application layer: class OpenThermApplProtocol
                     Several subClasses, starting with 'OT_' as far as specified
                     in Protocol v2.2, though not yet completely filled in

The registers are initialized using a spreadsheet, see bottom of this file.
The spreadsheet is taken from the OpenTherm spec and annotated with a column
containing the class definition for the register at hand.

NOTES:  Given my setting with Lyric T6 and Intergas <type>
- Registers tested
  [0, 1, 2, 3, 6, 9, 16, 17, 18, 19, 24, 25, 26, 48, 56, 100, 116, 120, 123, 126]
- Registers used, but still unknown:
  [113, 114, 128, 200, 202, 204, 220]

"""
import json
import logging
import sys
from .hass_discovery import HassDiscovery

logger = logging.getLogger(__name__)


class OpenThermProtocol:
    """OpenTherm Datalink layer protocol.

    Frame format, identical for both directions: 32 bits, 4 bytes.
    """
    message_types = [
        "Read-Data",
        "Write-Data",
        "Invalid-Data",
        "-reserved-",
        "Read-Ack",
        "Write-Ack",
        "Data-Invalid",
        "Unknown-DataId"
    ]
    shrt_msg_types = [
        "rd",
        "wd",
        "id",
        "-r",
        "ra",
        "wa",
        "iv",
        "ui"
    ]

    device_class = {
        "°C": "temperature",
        "%": "number",
        "bar": "pressure",
    }

    def __init__(self, v):
        self.frame = v & 0xffffffff
        self.b_data_value = v & 0xffff
        self.b_data_id = (v >> 16) & 0xff
        self.b_spare = (v >> 24) & 0xf
        # assert self.b_spare == 0, "Spare must be all zero."
        self.b_msg_type = (v >> 28) & 0x7
        self.b_parity = (v >> 31) & 0x1
        # assert self._parity() == 0, "Parity check fails."
        return

    def _parity(self):
        """ Check parity.

        See: https://www.geeksforgeeks.org/finding-the-parity-of-a-number-efficiently/
        """
        y = self.frame ^ (self.frame >> 1);
        y = y ^ (y >> 2);
        y = y ^ (y >> 4);
        y = y ^ (y >> 8);
        y = y ^ (y >> 16);
        # Rightmost bit of y holds the parity value if (y&1) is 1
        # then parity is odd
        # else even
        return (y & 1)

    def msg_type(self):
        assert self.b_msg_type not in [2, 3, 6, 7], "Error or invalid data in message."
        return self.message_types[self.b_msg_type]

    def data_id(self):
        return self.b_data_id

    def data_value(self):
        return self.b_data_value

    def __str__(self):
        return f"{self.msg_type():15} {self.b_data_id:2} {self.b_data_value:6}"


class OpenThermApplProtocol(OpenThermProtocol):
    """OpenTherm Application Layer protocol.

    Typically initialized using the 'from_frame' factory function.
    """

    @staticmethod
    def from_frame(frame):
        """Factory function for an OpenTherm register class."""
        reg_id = (frame >> 16) & 0xff
        OT = OpenThermApplProtocol.OT
        if reg_id in OT:
            subcl = OT[reg_id]["SubClass"]
            if subcl in globals():
                # Return a specialized SubClass, depending on reg_id
                return globals()[subcl](frame)
            logger.warning(f"Missing {subcl} in code, or wrong in ot_registers.py")
        # Insert this new register in OT, yet unknown and ignore further
        logger.warning(f"Missing Register 'data_id'=={reg_id} in OT")
        OT[reg_id] = {}
        OT[reg_id]["Description"] = "Unkown register"
        OT[reg_id]["R/W"] = "- -"  # Do not use
        OT[reg_id]["DataObject"] = "xx"
        OT[reg_id]["DataType"] = "u16"
        OT[reg_id]["SubClass"] = "OpenThermApplProtocol"
        return OpenThermApplProtocol(frame)

    def flags_payload(self, flags):
        """Decode Master and Slave Status flags and construct JSON payload."""
        v = int(self.b_data_value)
        bits = format(v, '016b')[::-1]  # reversed, bit0 = first
        flgs = {f"{v[0]}": int(v[1]) for v in zip(flags, bits[0:8])}
        return flgs

    def decode_payload(self):
        return self.b_data_value

    def mqtt_msg(self, ms):
        """Construct topic and payload with message type."""
        # t = str(self.b_data_id) + "/" + self.shrt_msg_types[self.b_msg_type]
        t = f"{self.b_data_id}/{ms}_{self.shrt_msg_types[self.b_msg_type]}"
        p = self.decode_payload()
        return t, p

    def mqtt_desc(self):
        """Construct topic and payload for description of register."""
        t = str(self.b_data_id) + "/desc"
        p = self.OT[self.b_data_id]["Description"]
        if type(p) == list:
            p = json.dumps(p)
        return t, p

    def mqtt_rw(self):
        """Construct topic and payload for R/W of register."""
        t = str(self.b_data_id) + "/rw"
        p = self.OT[self.b_data_id]["R/W"]
        return t, p

    def mqtt_dataobject(self):
        """Construct topic and payload for DataObject of register."""
        t = str(self.b_data_id) + "/d_obj"
        p = self.OT[self.b_data_id]["DataObject"]
        if type(p) == list:
            p = json.dumps(p)
        return t, p

    def discovery_topic(self, ms, component="sensor", node_id="OpenThermGW", topic_ext="", topic={}):
        """Construct the MQTT discovery topic.
        
        """
        reg_id = self.b_data_id

        if "DataObject" in topic:
            config_id = topic["DataObject"]
        else:
            config_id = self.OT[reg_id]["DataObject"]
        # Fix string... if needed
        config_id = config_id.replace("/", "__")
        config_id = config_id.replace("-", "_")
        config_id = config_id.replace(" ", "")
        if topic_ext:
            config_id += f"_{topic_ext}"
        config_id += f"_{ms}"  # Can still come from master and slave

        return f"{self.hass_prefix}/{component}/{node_id}/{config_id}/config"

    def discovery_payload(self, ms, uid_ext="", topic={}):
        reg_id = self.b_data_id

        p = {} if not hasattr(self, "dis_payload") else self.dis_payload

        p["name"] = self.OT[reg_id]["Description"]
        p["state_topic"] = f"otgw/{reg_id}/{ms}_{self.shrt_msg_types[self.b_msg_type]}"
        if "DataObject" in topic:
            dobj = topic["DataObject"]
        else:
            dobj = self.OT[reg_id]['DataObject']
        uid = f"esp8266_otgw_b4e62d1428ea_{reg_id}_{dobj}"
        if uid_ext:
            dobj += f"_{uid_ext}"
            uid += f"_{uid_ext}"
        p["object_id"] = dobj + f"_{ms}"
        p["unique_id"] = uid + f"_{ms}"

        return p

    def discovery_RW(self, ms):
        # If both R and W (ie 'R W'), then only R
        if not self.b_data_id in self.OT:
            return False
        RW = self.OT[self.b_data_id]["R/W"]
        if ms == "s" and "R" in RW:
            return True
        elif ms == "m" and "R" in RW:
            return False
        elif ms == "m" and "W" in RW:
            return True
        return False

        
    async def mqtt_discovery_flag(self, client, ms, select, flag, devclass, payload={}, topic={}):
        if not select:
            return
        if not self.discovery_RW(ms):
            return
        t = self.discovery_topic(ms, component="binary_sensor", topic_ext=flag, topic=topic)
        if not t:
            return
        p = self.discovery_payload(ms, uid_ext=flag, topic=topic)
        p["name"] = f"Status {flag}"
        p["device_class"] = devclass
        p["value_template"] = "{{ value_json." + flag + " }}"
        p["payload_off"] = "0"
        p["payload_on"]  = "1"
        dm = HassDiscovery(t, p)
        await dm.publish(client)
        return

    async def mqtt_discovery(self, client, ms, payload={}, topic={}):
        """Construct homeassistant discovery messages for this regid.
        """
        if not self.discovery_RW(ms):
            return
        t = self.discovery_topic(ms, topic=topic)
        if not t:
            return
        p = self.discovery_payload(ms, topic=topic)
        p |= payload

        dm = HassDiscovery(t, p)
        await dm.publish(client)
        return


class OT_f8f8(OpenThermApplProtocol):

    def decode_payload(self):
        hf = self.flags_payload(self.OT[self.b_data_id]["hflags"])
        lf = self.flags_payload(self.OT[self.b_data_id]["lflags"])
        return json.dumps(hf | lf)

    async def mqtt_discovery(self, client, ms):
        """Generate binary_sensors."""
        r = self.b_data_id
        t = {"DataObject": self.OT[r]["DataObject"][0]}
        for select, flag, devclass in zip(self.OT[r]['hflags_enabled'],
                                          self.OT[r]['hflags'],
                                          self.OT[r]['hflags_device_class']):
            await self.mqtt_discovery_flag(client, ms, select, flag, devclass, topic=t)
        t = {"DataObject": self.OT[r]["DataObject"][1]}
        for select, flag, devclass in zip(self.OT[r]['lflags_enabled'],
                                          self.OT[r]['lflags'],
                                          self.OT[r]['lflags_device_class']):
            await self.mqtt_discovery_flag(client, ms, select, flag, devclass, topic=t)
        return


# class OT_reg_0(OT_f8f8):
#     """Master and Slave Status flags."""
    
#     master_flags = ["CH_enable", "DHW_enable", "Cooling_enable", "OTC_active",
#                     "CH2_enable", "reserved", "reserved", "reserved"]
#     slave_flags = ["Fault", "CH_mode", "DHW_mode", "Flame_status",
#                    "Cooling_status", "CH2_mode", "diagnostic", "reserved"]

#     def flags_payload(self):
#         """Decode Master and Slave Status flags and construct JSON payload."""
#         v = int(self.b_data_value)
#         try:
#             bits = format(v, '016b')[::-1]  # reversed, bit0 = first
#         except TypeError as e:
#             print(e)
#             print(f"Trying format({v}, '016b')")
#             return self.b_data_value
#         s = {f"{v[0]}": int(v[1]) for v in zip(self.slave_flags, bits[0:8])}
#         m = {f"{v[0]}": int(v[1]) for v in zip(self.master_flags, bits[8:])}
#         return json.dumps(m | s)

#     def decode_payload(self):
#         return self.flags_payload()

#     async def mqtt_discovery(self, client, ms):
#         """Generate few binary_sensors."""

#         async def publish(select, flag):
#             if not select:
#                 return
#             t = self.discovery_topic(ms, component="binary_sensor", topic_ext=flag)
#             if not t:
#                 return
#             p = self.discovery_payload(ms, uid_ext=flag)
#             p["name"] = f"Status {flag}"
#             p["device_class"] = "heat"
#             p["value_template"] = "{{ value_json." + flag + " }}"
#             p["payload_off"] = "0"
#             p["payload_on"]  = "1"
#             dm = HassDiscovery(t, p)
#             await dm.publish(client)
#             return

#         if ms == "m":
#             bs_m = [1, 0, 0, 0, 0, 0, 0, 0]  # Enabled Master flags
#             for select, flag in zip(bs_m, self.master_flags):
#                 await publish(select, flag)

#         if ms == "s":
#             bs_s = [0, 0, 0, 1, 0, 0, 0, 0]  # Enabled Slave flags
#             for select, flag in zip(bs_s, self.slave_flags):
#                 await publish(select, flag)
#         return

#     pass

# class OT_reg_6(OT_f8f8):

#     pass


class OT_f8u8(OpenThermApplProtocol):

    def decode_payload(self):
        hf = self.flags_payload(self.OT[self.b_data_id]["hflags"])        
        r = self.b_data_id
        v = {self.OT[r]["DataObject"][1]: self.b_data_value & 0xff}
        return json.dumps(hf | v)

    async def mqtt_discovery(self, client, ms):
        r = self.b_data_id
        # Add flags
        t = {"DataObject": self.OT[r]["DataObject"][0]}
        for select, flag, devclass in zip(self.OT[r]['hflags_enabled'],
                                          self.OT[r]['hflags'],
                                          self.OT[r]['hflags_device_class']):
            await self.mqtt_discovery_flag(client, ms, select, flag, devclass, topic=t)
        # Add u8 value
        dobj = self.OT[r]["DataObject"][1]
        t = {"DataObject": dobj}
        p = {"name": self.OT[r]["Description"][1]}
        p["value_template"] = "{{ " + f"value_json.{dobj}" + " }}"
        await super().mqtt_discovery(client, ms, payload=p, topic=t)
        return


class OT_reg_100(OpenThermApplProtocol):

    def decode_payload(self):
        r = self.b_data_id
        dv = self.b_data_value
        v = {self.OT[r]["DataObject"][0]: (dv >> 8) & 0xff}
        lf = self.flags_payload(self.OT[self.b_data_id]["lflags"])
        return json.dumps(v | lf)

    async def mqtt_discovery(self, client, ms):
        r = self.b_data_id
        # Add u8 value
        dobj = self.OT[r]["DataObject"][0]
        t = {"DataObject": dobj}
        p = {"name": self.OT[r]["Description"][0]}
        p["value_template"] = "{{ " + f"value_json.{dobj}" + " }}"
        await super().mqtt_discovery(client, ms, payload=p, topic=t)
        # Add flags
        t = {"DataObject": self.OT[r]["DataObject"][1]}
        for select, flag, devclass in zip(self.OT[r]['lflags_enabled'],
                                          self.OT[r]['lflags'],
                                          self.OT[r]['lflags_device_class']):
            await self.mqtt_discovery_flag(client, ms, select, flag, devclass, topic=t)
        return


class OT_u8u8_dual(OpenThermApplProtocol):
    dis_payload = {
        "unit_of_measurement": ["", ""],
        "device_class": ["enum", "enum"]
    }

    def decode_payload(self):
        r = self.b_data_id
        dv = self.b_data_value
        v = {self.OT[r]["DataObject"][0]: (dv >> 8) & 0xff,
             self.OT[r]["DataObject"][1]: dv & 0xff}
        return json.dumps(v)

    async def mqtt_discovery(self, client, ms):
        try:
            for i, (do, ds, unit, devc) in enumerate(
                    zip(self.OT[self.b_data_id]["DataObject"],
                        self.OT[self.b_data_id]["Description"],
                        self.dis_payload["unit_of_measurement"],
                        self.dis_payload["device_class"])):
                t = {"DataObject": do}
                p = {"name": ds}
                p["unit_of_measurement"] = unit
                p["device_class"] = devc
                p["value_template"] = "{{ " + f"value_json.{do}" + " }}"
                logger.debug(f"u8u8_dual {i} do: {do}, ms: {ms}\n{json.dumps(p, indent=2)}")
                await super().mqtt_discovery(client, ms, p, t)
        except TypeError as e:
            logger.error(f"{e}\nFailure with register {self.b_data_id}")
        return

class OT_reg_15(OT_u8u8_dual):
    dis_payload = {
        "unit_of_measurement": ["kW", "%"],
        "device_class": ["power", "power_factor"]
    }


class OT_s8s8_dual(OT_u8u8_dual):

    def decode_payload(self):

        def sbyte(v):
            return (v - 0x100) if v & 0x80 else v
        
        r = self.b_data_id
        dv = self.b_data_value
        v = {self.OT[r]["DataObject"][0]: sbyte((dv >> 8) & 0xff),
             self.OT[r]["DataObject"][1]: sbyte(dv & 0xff)}
        return json.dumps(v)


class OT_s8s8_dual_C(OT_s8s8_dual):
    dis_payload = {
        "unit_of_measurement": ["°C", "°C"],
        "device_class": ["temperature", "temperature"]
    }
    

class OT_reg_20(OpenThermApplProtocol):

    def decode_payload(self):
        v = self.b_data_value
        return f"[{(v >> 13) & 0x7},{(v >> 8) & 0x1f},{v & 0xff}]"

    async def mqtt_discovery(self, client, ms):
        """To be filled-in."""
        # await super().mqtt_discovery(client, ms)
        return


class OT_f88(OpenThermApplProtocol):

    def decode_payload(self):
        v = self.b_data_value
        t = (v - 0x10000) / 256.0 if v & 0x8000 else v / 256.0
        return f"{t:.2f}"


class OT_f88_C(OT_f88):
    dis_payload = {
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    }


class OT_f88_p(OT_f88):
    dis_payload = {
        "unit_of_measurement": "%"
    }


class OT_reg_18(OT_f88):
    dis_payload = {
        "unit_of_measurement": "bar",
        "device_class": "pressure"
    }


class OT_reg_19(OT_f88):
    dis_payload = {
        "unit_of_measurement": "L/min",
        "device_class": "volume_flow_rate"
    }


class OT_u16(OpenThermApplProtocol):

    pass


class OT_reg_33(OpenThermApplProtocol):
    dis_payload = {
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    }

    def decode_payload(self):
        v = self.b_data_value
        return (v - 0x10000) if v & 0x8000 else v


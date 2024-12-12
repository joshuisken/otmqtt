"""This table is generated from pages 32+33 of OpenTherm specification v2.2.

It is used in class OpenThermApplProtocol and sub-classes.

Changes w.r.t. to the spec:
- Minor modifications from original table in the spec.
- Added member 'SubClass', classes which are inherited from OpenThermApplProtocol,
  for each register which is used by the static method 'from_frame' factory function.
- Added extra members, such as for flag names.
- Split 'DataType' and 'Description' for various registers in
  lists for sub-parts of each registers.
"""

OT = {
    0: {
        'DataObject': 'Status',
        'DataType': 'flag8 / flag8',
        'Description': 'Master and Slave Status flags.',
        'R/W': 'R -',
        'SubClass': 'OT_reg_0',
        'SubClass': 'OT_f8f8',
        'hflags': ["CH_enable", "DHW_enable", "Cooling_enable", "OTC_active",
                   "CH2_enable", "reserved", "reserved", "reserved"],
        'hflags_device_class': ["heat", None, None, None, None, None, None, None],
        'hflags_enabled': [1, 1, 1, 1, 1, 0, 0, 0],
        'lflags': ["Fault", "CH_mode", "DHW_mode", "Flame_status",
                   "Cooling_status", "CH2_mode", "diagnostic", "reserved"],
        'lflags_device_class': [None, None, None, "heat", None, None, None, None],
        'lflags_enabled': [1, 1, 1, 1, 1, 1, 1, 0]
    },
    1: {
        'DataObject': 'TSet',
        'DataType': 'f8.8',
        'Description': 'Control setpoint  ie CH  water temperature setpoint (°C)',
        'R/W': '- W',
        'SubClass': 'OT_f88_C'
    },
    2: {
        'DataObject': ['M_Config', 'M_MemberIDcode'],
        'DataType': 'flag8 / u8',
        'Description': ['Master Configuration Flags',
                        'Master MemberID Code'],
        'R/W': '- W',
        'SubClass': 'OT_f8u8',
        'hflags': ['reserved'] * 8,
        'hflags_device_class': [None] * 8,
        'hflags_enabled': [0] * 8
    },
    3: {
        'DataObject': ['S_Config', 'S_MemberIDcode'],
        'DataType': 'flag8 / u8',
        'Description': ['Slave Configuration Flags',
                        'Slave MemberID Code'],
        'R/W': 'R -',
        'SubClass': 'OT_f8u8',
        'hflags': ['DHW_present', 'Control_type', 'Cooling_config', 'DHW_config',
                   'Master_low__off_and_pump_control', 'CH2_present', 'reserved', 'reserved'],
        'hflags_device_class': [None] * 8,
        'hflags_enabled': [1, 1, 1, 1, 1, 1, 0, 0]
    },
    4: {
        'DataObject': ['Command_H', 'Command_L'],
        'DataType': 'u8 / u8',
        'Description': ['Remote Command High',
                        'Remote Command Low'],
        'R/W': '- W',
        'SubClass': 'OT_u8u8_dual'
    },
    5: {
        'DataObject': ['ASF_flags', 'OEM_fault_code'],
        'DataType': 'flag8 / u8',
        'Description': ['Application-specific fault flags',
                        'OEM fault code'],
        'R/W': 'R -',
        'SubClass': 'OT_f8u8',
        'hflags': ['Service_request', 'Lockout_request', 'Low_water_press', 'Gas_flame_fault',
                   'Air_pressure_fault', 'Water_over_temp', 'reserved', 'reserved'],
        'hflags_device_class': [None, None, None, None, None, None, None, None],
        'hflags_enabled': [1, 1, 1, 1, 1, 1, 0, 0]
    },
    6: {
        'DataObject': 'RBP_flags',
        'DataType': 'flag8 / flag8',
        'Description': 'Remote boiler parameter transfer-enable & read/write flags',
        'R/W': 'R -',
        'SubClass': 'OT_f8f8',
        'hflags': ['DHW_setpoint', 'max_CHsetpoint'] + ['reserved']*6,
        'hflags_device_class': [None, None, None, None, None, None, None, None],
        'hflags_enabled': [1, 1, 0, 0, 0, 0, 0, 0],
        'lflags': ['DHW_setpoint', 'max_CHsetpoint'] + ['reserved']*6,
        'lflags_device_class': [None, None, None, None, None, None, None, None],
        'lflags_enabled': [1, 1, 0, 0, 0, 0, 0, 0]
    },
    7: {
        'DataObject': 'Cooling_control',
        'DataType': 'f8.8',
        'Description': 'Cooling control signal (%)',
        'R/W': '- W',
        'SubClass': 'OT_f88_p'
    },
    8: {
        'DataObject': 'TsetCH2',
        'DataType': 'f8.8',
        'Description': 'Control setpoint for 2e CH circuit (°C)',
        'R/W': '- W',
        'SubClass': 'OT_f88_C'
    },
    9: {
        'DataObject': 'TrOverride',
        'DataType': 'f8.8',
        'Description': 'Remote override room setpoint',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    10: {
        'DataObject': ['TSP_H', 'TSP_L'],
        'DataType': 'u8 / u8',
        'Description': ['HNumber of Transparent-Slave-Parameters supported by slave',
                        'LNumber of Transparent-Slave-Parameters supported by slave'],
        'R/W': 'R -',
        'SubClass': 'OT_u8u8_dual'
    },
    11: {
        'DataObject': ['TSP_index', 'TSP_value'],
        'DataType': 'u8 / u8',
        'Description': ['Index number',
                        'Value of referred-to transparent slave parameter'],
        'R/W': 'R W',
        'SubClass': 'OT_u8u8_dual'
    },
    12: {
        'DataObject': ['FHB_size_H', 'FHB_size_L'],
        'DataType': 'u8 / u8',
        'Description': ['HSize of Fault-History-Buffer supported by slave',
                        'LSize of Fault-History-Buffer supported by slave'],
        'R/W': 'R -',
        'SubClass': 'OT_u8u8_dual'
    },
    13: {
        'DataObject': ['FHB_index', 'FHB_value'],
        'DataType': 'u8 / u8',
        'Description': ['Index number',
                        'Value of referred-to fault-history buffer entry.'],
        'R/W': 'R -',
        'SubClass': 'OT_u8u8_dual'
    },
    14: {
        'DataObject': 'Max_rel_mod_level_setting',
        'DataType': 'f8.8',
        'Description': 'Maximum relative modulation level setting (%)',
        'R/W': '- W',
        'SubClass': 'OT_f88_p'
    },
    15: {
        'DataObject': ['Max_Capacity', 'Min_Mod_Level'],
        'DataType': 'u8 / u8',
        'Description': ['Maximum boiler capacity (kW)',
                        'Minimum boiler modulation level (%)'],
        'R/W': 'R -',
        'SubClass': 'OT_reg_15'
    },
    16: {
        'DataObject': 'TrSet',
        'DataType': 'f8.8',
        'Description': 'Room Setpoint (°C)',
        'R/W': '- W',
        'SubClass': 'OT_f88_C'
    },
    17: {
        'DataObject': 'Rel_mod_level',
        'DataType': 'f8.8',
        'Description': 'Relative Modulation Level (%)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_p'
    },
    18: {
        'DataObject': 'CH_pressure',
        'DataType': 'f8.8',
        'Description': 'Water pressure in CH circuit (bar)',
        'R/W': 'R -',
        'SubClass': 'OT_reg_18'
    },
    19: {
        'DataObject': 'DHW_flow_rate',
        'DataType': 'f8.8',
        'Description': 'Water flow rate in DHW circuit (litres/minute)',
        'R/W': 'R -',
        'SubClass': 'OT_reg_19'
    },
    20: {
        'DataObject': 'Day_Time',
        'DataType': 'u3 / u5 / u8',
        'Description': 'Day of Week and Time of Day',
        'R/W': 'R W',
        'SubClass': 'OT_reg_20'
    },
    21: {
        'DataObject': ['Month', 'Day_of_Month'],
        'DataType': 'u8 / u8',
        'Description': ['Calendar month',
                        'Calendar day of month'],
        'R/W': 'R W',
        'SubClass': 'OT_u8u8_dual'
    },
    22: {
        'DataObject': 'Year',
        'DataType': 'u16',
        'Description': 'Calendar year',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    23: {
        'DataObject': 'TrSetCH2',
        'DataType': 'f8.8',
        'Description': 'Room Setpoint for 2nd CH circuit (°C)',
        'R/W': '- W',
        'SubClass': 'OT_f88_C'
    },
    24: {
        'DataObject': 'Tr',
        'DataType': 'f8.8',
        'Description': 'Room temperature (°C)',
        'R/W': '- W',
        'SubClass': 'OT_f88_C'
    },
    25: {
        'DataObject': 'Tboiler',
        'DataType': 'f8.8',
        'Description': 'Boiler flow water temperature (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    26: {
        'DataObject': 'Tdhw',
        'DataType': 'f8.8',
        'Description': 'DHW temperature (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    27: {
        'DataObject': 'Toutside',
        'DataType': 'f8.8',
        'Description': 'Outside temperature (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    28: {
        'DataObject': 'Tret',
        'DataType': 'f8.8',
        'Description': 'Return water temperature (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    29: {
        'DataObject': 'Tstorage',
        'DataType': 'f8.8',
        'Description': 'Solar storage temperature (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    30: {
        'DataObject': 'Tcollector',
        'DataType': 'f8.8',
        'Description': 'Solar collector temperature (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    31: {
        'DataObject': 'TflowCH2',
        'DataType': 'f8.8',
        'Description': 'Flow water temperature CH2 circuit (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    32: {
        'DataObject': 'Tdhw2',
        'DataType': 'f8.8',
        'Description': 'Domestic hot water temperature 2 (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_f88_C'
    },
    33: {
        'DataObject': 'Texhaust',
        'DataType': 's16',
        'Description': 'Boiler exhaust temperature (°C)',
        'R/W': 'R -',
        'SubClass': 'OT_reg_33',
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "decode_payload": lambda v: (v - 0x10000) if v & 0x8000 else v
    },
    48: {
        'DataObject': ['TdhwSet_UB', 'TdhwSet_LB'],
        'DataType': 's8 / s8',
        'Description': ['DHW setpoint upper bound for adjustment  (°C)',
                        'DHW setpoint lower bound for adjustment  (°C)'],
        'R/W': 'R -',
        'SubClass': 'OT_s8s8_dual_C'
    },
    49: {
        'DataObject': ['MaxTSet_UB', 'MaxTSet_LB'],
        'DataType': 's8 / s8',
        'Description': ['Max CH water setpoint upper bound for adjustment  (°C)',
                        'Max CH water setpoint lower bound for adjustment  (°C)'],
        'R/W': 'R -',
        'SubClass': 'OT_s8s8_dual_C'
    },
    50: {
        'DataObject': ['Hcratio_UB', 'Hcratio_LB'],
        'DataType': 's8 / s8',
        'Description': ['OTC heat curve ratio upper bound for adjustment',
                        'OTC heat curve ratio lower bound for adjustment'],
        'R/W': 'R -',
        'SubClass': 'OT_s8s8_dual'
    },
    56: {
        'DataObject': 'TdhwSet',
        'DataType': 'f8.8',
        'Description': 'DHW setpoint (°C) (Remote parameter 1)',
        'R/W': 'R W',
        'SubClass': 'OT_f88_C'
    },
    57: {
        'DataObject': 'MaxTSet',
        'DataType': 'f8.8',
        'Description': 'Max CH water setpoint (°C) (Remote parameters 2)',
        'R/W': 'R W',
        'SubClass': 'OT_f88_C'
    },
    58: {
        'DataObject': 'Hcratio',
        'DataType': 'f8.8',
        'Description': 'OTC heat curve ratio (°C) (Remote parameter 3)',
        'R/W': 'R W',
        'SubClass': 'OT_f88_C'
    },
    100: {
        'DataObject': ['Remote_override_function', 'Remote_override_function'],
        'DataType': 'u8 / flag8',
        'Description': ['Function of manual and program changes in master and remote room setpoint.',
                        'Function of manual and program changes in master and remote room setpoint.'],
        'R/W': 'R -',
        'SubClass': 'OT_reg_100',
        'lflags': ['Manual_change_priority', 'Program_change_priority'] + ['reserved']*6,
        'lflags_device_class': [None, None, None, None, None, None, None, None],
        'lflags_enabled': [1, 1, 0, 0, 0, 0, 0, 0]
    },
    115: {
        'DataObject': 'OEM diagnostic code',
        'DataType': 'u16',
        'Description': 'OEM-specific diagnostic/service code',
        'R/W': 'R -',
        'SubClass': 'OT_u16'
    },
    116: {
        'DataObject': 'Burner starts',
        'DataType': 'u16',
        'Description': 'Number of starts burner',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    117: {
        'DataObject': 'CH pump starts',
        'DataType': 'u16',
        'Description': 'Number of starts CH pump',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    118: {
        'DataObject': 'DHW pump/valve starts',
        'DataType': 'u16',
        'Description': 'Number of starts DHW pump/valve',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    119: {
        'DataObject': 'DHW burner starts',
        'DataType': 'u16',
        'Description': 'Number of starts burner during DHW mode',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    120: {
        'DataObject': 'Burner operation hours',
        'DataType': 'u16',
        'Description': 'Number of hours that burner is in operation (i.e. flame '
        'on)',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    121: {
        'DataObject': 'CH pump operation hours',
        'DataType': 'u16',
        'Description': 'Number of hours that CH pump has been running',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    122: {
        'DataObject': 'DHW pump/valve operation hours',
        'DataType': 'u16',
        'Description': 'Number of hours that DHW pump has been running or DHW '
        'valve has been opened',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    123: {
        'DataObject': 'DHW burner operation hours',
        'DataType': 'u16',
        'Description': 'Number of hours that burner is in operation during DHW '
        'mode',
        'R/W': 'R W',
        'SubClass': 'OT_u16'
    },
    124: {
        'DataObject': 'OpenTherm version Master',
        'DataType': 'f8.8',
        'Description': 'The implemented version of the OpenTherm Protocol '
        'Specification in the master.',
        'R/W': '-  W',
        'SubClass': 'OT_f88'
    },
    125: {
        'DataObject': 'OpenTherm version Slave',
        'DataType': 'f8.8',
        'Description': 'The implemented version of the OpenTherm Protocol '
        'Specification in the slave.',
        'R/W': 'R -',
        'SubClass': 'OT_f88'
    },
    126: {
        'DataObject': ['Master_version', 'Master_type'],
        'DataType': 'u8 / u8',
        'Description': ['Master product version number',
                        'Master product version type'],
        'R/W': '- W',
        'SubClass': 'OT_u8u8_dual'
    },
    127: {
        'DataObject': ['Slave_version', 'Slave_type'],
        'DataType': 'u8 / u8',
        'Description': ['Slave product version number',
                        'Slave product version type'],
        'R/W': 'R -',
        'SubClass': 'OT_u8u8_dual'
    },

    # Folowing registers are used (by Honeywell T6) but are not specified
    # in OpenTherm v2.2
    # 113: {},
    # 114: {},
    # 128: {},
    # 200: {},
    # 202: {},
    # 204: {},
    # 220: {}
}

if __name__ == "__main__":
    import json
    with open("OT.json", "w") as f:
        json.dump(OT, f, indent=2)


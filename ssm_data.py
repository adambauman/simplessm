class SSMPacketComponents:
    ecu_command_header = bytearray([0x80, 0x10, 0xF0])
    data_padding = 0x00
    read_address_command = 0xA8
    ecu_init_command = 0xBF

class SSMUnit:
    name = ""
    symbol = ""
    # TODO: lambdas for unit conversions

    def __init__(self, name="", symbol=""):
        self.name = name
        self.symbol = symbol

class SSMUnits:
    unknown = SSMUnit("Unknown", "UNK")
    celsius = SSMUnit("Celsius", "C")
    rpm = SSMUnit("Rotations Per Minute", "RPM")
    volts = SSMUnit("Volts", "V")
    percent = SSMUnit("Percent", "%")
    psig = SSMUnit("PSI Gauge", "PSIG")

class SSMField:
    upper_address = None
    lower_address = None
    upper_value = None
    lower_value = None
    name = ""
    unit = SSMUnits.unknown

    def __init__(
        self, 
        upper_address=None, lower_address=None,
        upper_byte=None, lower_byte=None,
        name="", unit=SSMUnits.unknown
    ):
        self.upper_address = upper_address
        self.lower_address = lower_address
        self.upper_byte = upper_byte
        self.lower_byte = lower_byte
        self.name = name
        self.unit = unit

class SSMFields:
    coolant_temperature = SSMField(lower_address=bytearray([0x00,0x00,0x08]), name="Coolant Temperature", unit=SSMUnits.celsius)
    battery_voltage = SSMField(lower_address=bytearray([0x00,0x00,0x1c]), name="Battery Voltage", unit=SSMUnits.volts)
    #engine_load = SSMField(lower_address=bytearray([0x00,0x07,0x00]), name="Engine Load", unit=SSMUnits.percent)
    #manifold_absolute_pressure = SSMField(lower_address=bytearray([0x00,0x0D,0x00]), name="Manifold Absolute Pressure", unit=SSMUnits.psig)
    #throttle_position = SSMField(lower_address=bytearray([0x01,0x05,0x00]), name="Throttle Position", unit=SSMUnits.percent)

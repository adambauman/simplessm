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
    upper_value_byte = None
    lower_value_byte = None
    name = ""
    unit = SSMUnits.unknown
    conversion = None

    def __init__(
        self, name, unit, conversion, lower_address, upper_address=None
    ):
        self.upper_address = upper_address
        self.lower_address = lower_address
        self.name = name
        self.unit = unit
        self.conversion = conversion # lambda to convert byte data into value

    def get_value(self):
        return self.conversion(self.upper_value_byte, self.lower_value_byte)

class SSMFields:
    #coolant_temperature = SSMField(
    #    lower_address=bytearray([0x00,0x00,0x08]), name="Coolant Temperature", 
    #    unit=SSMUnits.celsius, value=__get_volts__(self.lower_byte)
    #)

    battery_voltage = SSMField(
        lower_address=bytearray([0x00,0x00,0x1c]), name="Battery Voltage",
        unit=SSMUnits.volts, conversion=lambda upper_value_byte,lower_value_byte:lower_value_byte * 0.08
    )
    #engine_load = SSMField(lower_address=bytearray([0x00,0x07,0x00]), name="Engine Load", unit=SSMUnits.percent)
    #manifold_absolute_pressure = SSMField(lower_address=bytearray([0x00,0x0D,0x00]), name="Manifold Absolute Pressure", unit=SSMUnits.psig)
    #throttle_position = SSMField(lower_address=bytearray([0x01,0x05,0x00]), name="Throttle Position", unit=SSMUnits.percent)

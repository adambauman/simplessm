class SSMPacketComponents:
    ecu_command_header = bytearray([0x80, 0x10, 0xF0])
    data_padding = 0x00
    read_address_command = 0xA8
    ecu_init_command = 0xBF

class SSMUnit:
    name = ""
    symbol = ""

    def __init__(self, name="", symbol=""):
        self.name = name
        self.symbol = symbol

class SSMUnits:
    unknown = SSMUnit("Unknown", "UNK")
    celsius = SSMUnit("Celsius", "C")
    rpm = SSMUnit("Rotations Per Minute", "RPM")
    kmh = SSMUnit("Kilometers Per Hour", "KPH")
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
        self.conversion = conversion

    def get_value(self):
        return self.conversion(self.upper_value_byte, self.lower_value_byte)

class SSMFields:
    engine_load = SSMField(
        lower_address=bytearray([0x00,0x00,0x07]), name="Engine Load", 
        unit=SSMUnits.percent, conversion=lambda msb,lsb:(lsb * 100) / 255
    )

    coolant_temperature = SSMField(
        lower_address=bytearray([0x00,0x00,0x08]), name="Coolant Temperature",
        unit=SSMUnits.celsius, conversion=lambda msb,lsb:lsb - 40
    )

    throttle_opening_angle = SSMField(
        lower_address=bytearray([0x00,0x00,0x15]), name="Throttle Opening Angle", 
        unit=SSMUnits.percent, conversion=lambda msb,lsb:(lsb * 100) / 255
    )

    battery_voltage = SSMField(
        lower_address=bytearray([0x00,0x00,0x1c]), name="Battery Voltage", 
        unit=SSMUnits.volts, conversion=lambda msb,lsb:lsb * 0.08
    )

    manifold_relative_pressure = SSMField(
        lower_address=bytearray([0x00,0x00,0x24]), name="Manifold Relative Pressure", 
        unit=SSMUnits.psig, conversion=lambda msb,lsb:((lsb - 128) * 37) / 255
    )

    manifold_absolute_pressure = SSMFields(
        lower_address=([0x00,0x00,0x0D], name="Manifold Absolute Pressure",
        unit=SSMUnits.psig, conversion=lambda msb,ldb:(lsb * 37) / 255
    )

    engine_speed = SSMFields(
        upper_address=([0x00,0x00,0x0E]), lower_address=([0x00,0x00,0x0F]), name="Engine Speed",
        unit=SSMUnits.rpm, conversion=lambda msb,lsb:(lsb + (msb << 8)) / 4
    )

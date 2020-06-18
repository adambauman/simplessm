import simplessm

class SSMPacketComponents:
    ecu_command_header = bytearray([0x80, 0x10, 0xF0])
    data_padding = 0x00
    read_address_command = 0xA8

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

    # TODO: def get_imperial_value() and get_metric_value()

class SSMFields:
    ooolant_temperature = SSMField(lower_address=bytearray([0x00,0x00,0x08]), name="Coolant Temperature", unit=SSMUnits.celsius)
    battery_voltage = SSMField(lower_address=bytearray([0x00,0x00,0x1c]), name="Battery Voltage", unit=SSMUnits.volts)
    #engine_load = SSMField(lower_address=bytearray(0x00,0x07,0x00), name="Engine Load", unit=SSMUnits.percent)
    #manifold_absolute_pressure = SSMField(lower_address=bytearray(0x00,0x0D,0x00), name="Manifold Absolute Pressure", unit=SSMUnits.psig)
    #throttle_position = SSMField(lower_address=bytearray(0x01,0x05,0x00), name="Throttle Position", unit=SSMUnits.percent)



def __get_hex_string__(byte_data):
    hex_string = ""
    for single_byte in byte_data:
        hex_string += "{:#04x} ".format(single_byte)
        
    return hex_string

def __calculate_checksum__(data_bytes):
    print("Calculating checksum for this data: {}".format(__get_hex_string__(data_bytes)))

    # Step 1: Get the sum of all data bytes including the header, command, and data bytes.
    data_byte_sum = 0
    for data_byte in data_bytes:
        data_byte_sum += data_byte

    # Step 2: Peel off the 8 lowest bits from the sum, this is the checksum value.
    checksum = data_byte_sum & 0xFF
    print("Checksum: {:#04x}".format(checksum))

    return checksum


def build_command_packet(target_fields):
    # Use extend() for adding other byte arrays, append() for single bytes
    # Put together the command data which is a single command byte and its associated data
    data = bytearray()
    data.append(SSMPacketComponents.read_address_command)
    data.append(SSMPacketComponents.data_padding)

    for field in target_fields:
        # 16 bit fields also require teh upper address
        if None != field.upper_address:
            data.extend(field.upper_address)

        data.extend(field.lower_address)

    # Initialize the new command packet with the proper header
    command_packet = bytearray()
    command_packet.extend(SSMPacketComponents.ecu_command_header)

    # Add the size byte, this is the number of data bytes + the command byte
    command_packet.append(len(data))

    # Attach the command body, then calculate the checksum and append it
    command_packet.extend(data)
    command_packet.append(__calculate_checksum__(command_packet))  

    return command_packet


def main():
    # 0x80:dest:src:datasize:command:datamultibytes:checksum

    target_fields = []
    target_fields.append(SSMFields.battery_voltage)
    #target_fields.append(SSMFields.ooolant_temperature)

    command_packet = build_command_packet(target_fields)

    print(__get_hex_string__(command_packet))


if __name__ == "__main__":
    main()

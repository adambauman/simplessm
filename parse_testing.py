from ssm_data import SSMFields, SSMPacketComponents

def get_hex_string(byte_data):
    hex_string = ""
    for single_byte in byte_data:
        hex_string += "{:#04x} ".format(single_byte)
        
    return hex_string
        
def calculate_checksum(data_bytes):
    #print("Calculating checksum for this data: {}".format(self.__get_hex_string__(data_bytes)))

    # Step 1: Get the sum of all data bytes including the header, command, and data bytes.
    data_byte_sum = 0
    for data_byte in data_bytes:
        data_byte_sum += data_byte
    
    # Step 2: Peel off the 8 lowest bits from the sum, this is the checksum value.
    checksum = data_byte_sum & 0xFF
    #print("Checksum: {:#04x}".format(checksum))

    return checksum

def build_address_read_packet(target_field_array):
    # Use extend() for adding other byte arrays, append() for single bytes
    # Put together the command data which is a single command byte and the address(es)
    data = bytearray()
    data.append(SSMPacketComponents.read_address_command)
    data.append(SSMPacketComponents.data_padding)

    for field in target_field_array:
        # Add the upper address for fields with 16 bit values
        if None != field.upper_address:
            data.extend(field.upper_address)

        data.extend(field.lower_address)

    # Initialize the new command packet with the proper header
    command_packet = bytearray()
    command_packet.extend(SSMPacketComponents.ecu_command_header)

    # Add the size byte, this is the number of address bytes + the command byte
    command_packet.append(len(data))

    # Attach the command body, then calculate the checksum and append it
    command_packet.extend(data)
    command_packet.append(calculate_checksum(command_packet))  

    return command_packet


def parse_field_response(response_bytes, command, command_fields, validate_checksum=False):
    # TODO: Checksum validation

    print("Parsing field response...")
    response_checksum = response_bytes[-1] # Last byte should always be the checksum
    print("Response checksum: {:#04x}".format(response_checksum))

    # Expected response: ECHOED_COMMAND + 3_BYTE_HEADER + VALUES + CHECKSUM
    data_index = len(command) + 3
    for command_field in command_fields:
        print("Current data_index: {}".format(data_index))
        if None != command_field.upper_address:
            command_field.upper_value_byte = response_bytes[data_index]
            print("Reading MSB: {:#04x}".format(command_fields.upper_value_byte))
            data_index = data_index + 1

        command_fields.lower_value_byte = response_bytes[data_index]
        print("Reading LSB: {:#04x}".format(command_fields.lower_value_byte))
        data_index = data_index + 1

    print("Finished parsing field response")

    return command_fields


def main():
    target_fields = []
    target_fields.append(SSMFields.battery_voltage)
    target_fields.append(SSMFields.coolant_temperature)
    target_fields.append(SSMFields.throttle_opening_angle)
    command_bytes = build_address_read_packet(target_fields)
    print("command_bytes:  {}".format(get_hex_string(command_bytes)))

    response_bytes = bytes.fromhex("80 10 f0 0b a8 00 00 00 1c 00 00 08 00 00 15 6c 80 f0 10 04 e8 95 3d 00 3e")
    print("response_bytes: {}".format(get_hex_string(response_bytes)))

    # Response starts with some echo output, find the location of the respones header
    response_header_index = response_bytes.find(bytes.fromhex("80 f0 10"))
    print("response_header_index: {}".format(response_header_index))

    # Retrieve the number of data bytes to process, this comes right after the response header
    # Subtract 1 byte because the size also includes the response "command" of 0xE8
    response_data_size = response_bytes[response_header_index + 3] - 1
    print("response_data_size: {}".format(response_data_size))

    # Avoid out-of-range errors and make sure we have the expected data
    if response_data_size != len(target_fields):
        raise Exception("Response data size mismatch")

    data_index = response_header_index + 5 # skip response header, size byte, and 0xE8 command
    # Start working through the data and data fields
    for field in target_fields:
        if None != field.upper_address:
            # Only set if this is a 16-bit value and we have a MSB to grab
            field.upper_value_byte = response_bytes[data_index]
            data_index += 1

        field.lower_value_byte = response_bytes[data_index]
        data_index += 1

    for field in target_fields:
        #print(field)
        print("{}: {}{}".format(field.name,field.get_value(),field.unit.symbol))

    #parse_result = parse_field_response(received_bytes, command_bytes, target_fields, False)
    #print(parse_result)


if __name__ == "__main__":
    main()
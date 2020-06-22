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


def parse_field_response(response_bytes, target_fields, validate_checksum=True):
    # Response starts with some echo output, find the location of the respones header
    #response_header_index = response_bytes.find(bytes.fromhex("80 f0 10"))
    response_header_index = response_bytes.find(SSMPacketComponents.ecu_response_header)
    print("response_header_index: {}".format(response_header_index))

    if validate_checksum:
        calculated_checksum = calculate_checksum(response_bytes[response_header_index:-1])
        print("calculated_checksum: {:#04x}".format(calculated_checksum))
        if calculated_checksum != response_bytes[-1]:
            raise Exception("Response checksum mismatch")

    # Retrieve the number of data bytes to process, this comes right after the response header
    # Subtract 1 byte because the size also includes the response "command" of 0xE8
    response_data_size = response_bytes[response_header_index + 3] - 1

    data_index = response_header_index + 5 # skip response header, size byte, and 0xE8 command
    processed_bytes = 0
    # Start working through the data and data fields
    for field in target_fields:
        if processed_bytes > response_data_size:
            raise Exception("Data index out of bounds")

        if None != field.upper_address:
            # Only set if this is a 16-bit value and we have a MSB to grab
            field.upper_value_byte = response_bytes[data_index]
            data_index += 1
            processed_bytes += 1

        field.lower_value_byte = response_bytes[data_index]
        data_index += 1
        processed_bytes += 1

    if processed_bytes != response_data_size:
        raise Exception("Data index and response data size mismatch")

    # Treating target_fields as referenced seems to be working alright
    #return target_fields


def main():
    target_fields = []
    target_fields.append(SSMFields.battery_voltage)
    target_fields.append(SSMFields.coolant_temperature)
    target_fields.append(SSMFields.throttle_opening_angle)
    command_bytes = build_address_read_packet(target_fields)
    print("command_bytes:  {}".format(get_hex_string(command_bytes)))

    response_bytes = bytes.fromhex("80 10 f0 0b a8 00 00 00 1c 00 00 08 00 00 15 6c 80 f0 10 04 e8 95 3d 00 3e")
    print("response_bytes: {}".format(get_hex_string(response_bytes)))

    parse_field_response(response_bytes, target_fields, True)

    for field in target_fields:
        print("{}: {}{}".format(field.name,field.get_value(),field.unit.symbol))


if __name__ == "__main__":
    main()
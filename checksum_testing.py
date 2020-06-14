import struct

class SelectMonitorConstants:
    header = 0x80
    ecu = 0x10
    diag_tool = 0xF0
    read_address = 0xA8
    address_pad = 0x00

class SelectMonitor:

    def __get_hex_string__(self, byte_data):
        hex_string = ""
        for single_byte in byte_data:
            hex_string += "{:#04x} ".format(single_byte)
            
        return hex_string
    def __calculate_checksum__(self, data_bytes):
        print("Calculating checksum for this data: {}".format(self.__get_hex_string__(data_bytes)))

        # Step 1: Get the sum of all data bytes including the header, command, and data bytes.
        data_byte_sum = 0
        for data_byte in data_bytes:
            data_byte_sum += data_byte
        
        # Step 2: Peel off the 8 lowest bits from the sum, this is the checksum value.
        checksum = data_byte_sum & 0xFF
        print("Checksum: {:#04x}".format(checksum))

        return checksum

    def __build_pack_format_string__(self, byte_count):
        pack_format_string = "!"
        for x in range(byte_count):
            pack_format_string += "B"

        return pack_format_string

    def __build_read_address_command__(self, address_bytes):
        data_byte_count = 5 # TODO: Actual calculation when accepting multple addresses
        header_byte_count = 4 # Should be pretty static (0x80, destination, source)

        # Create the initial command byte package, then send it off for checksum calculation
        ssm_consts = SelectMonitorConstants()
        pack_format_string = self.__build_pack_format_string__(data_byte_count + header_byte_count)
        command_bytes = struct.pack(
            pack_format_string, 
            ssm_consts.header, ssm_consts.ecu, ssm_consts.diag_tool, data_byte_count, ssm_consts.read_address,
            ssm_consts.address_pad, address_bytes[0], address_bytes[1], address_bytes[2]
        )
        checksum = self.__calculate_checksum__(command_bytes)

        # Repack the bytes with the checksum attached
        pack_format_string = self.__build_pack_format_string__(data_byte_count + header_byte_count + 1)
        command_bytes = struct.pack(
            pack_format_string,
            ssm_consts.header, ssm_consts.ecu, ssm_consts.diag_tool, data_byte_count, ssm_consts.read_address,
            ssm_consts.address_pad, address_bytes[0], address_bytes[1], address_bytes[2],
            checksum
        )

        return command_bytes

def main():

    ssm = SelectMonitor()
    # test_command = struct.pack(
    #     "!BBBBB", 
    #     0x80, 0x10, 0xF0, 0x01, 0xBF 
    # )
    # test_command = struct.pack(
    #     "!BBBBBBBBBBBB",
    #     0x80, 0x10, 0xF0, 0x08, 0xA8, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x1C
    # )
    # print("Pack format string: {}".format(ssm.__build_pack_format_string__(9)))
    # test_command = struct.pack(
    #     "!BBBBBBBBB",
    #     0x80, 0x10, 0xF0, 0x05, 0xA8, 0x00, 0x00, 0x00, 0x1C
    # )
    #test_address = struct.pack("!BBB", 0x00, 0x00, 0x1C) #battery voltage
    test_address = struct.pack("!BBB", 0x00, 0x00, 0x08) #coolant temp
    ssm.read_single_address(test_address)

    #checksum = ssm.__calculate_checksum__(test_command)

if __name__ == "__main__":
    main()
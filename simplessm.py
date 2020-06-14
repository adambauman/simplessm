import struct
import time
import serial

# Invaluable reference for SSM: http://romraider.com/RomRaider/SsmProtocol

class SelectMonitorConstants:
    header = 0x80
    ecu = 0x10
    diag_tool = 0xF0
    read_address = 0xA8
    address_pad = 0x00

class SelectMonitor:

    serial = None

    def __init__(self, port):
        self.serial = serial.Serial(
            port, baudrate = 4800,
            bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE, timeout = 1.0
        )
        if not self.serial.is_open:
            print("Error opening serial port")
            raise Exception("Open serial connection")

    def __del__(self):
        if self.serial.is_open:
            self.serial.close()
            
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

    def build_read_address_command(self, address_bytes):
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

    def test_command(self, command):
        print("Command to send: {}".format(self.__get_hex_string__(command)))
        print("Writing command...")
        self.serial.write(command)        
        ("Finished writing command")
        
        time.sleep(0.1)
        
        print("Waiting for response...")
        bytes_waiting = self.serial.in_waiting
        wait_count = 0 # TODO: Replace with proper timeout check
        while 0 == bytes_waiting:
            print("Waiting...")
            time.sleep(0.1)
            bytes_waiting = self.serial.in_waiting
            wait_count = wait_count + 1
            if 10 < wait_count:
                print("Error, no response!")
                break
        
        if 0 != bytes_waiting:
            print("Received response, bytes in waiting: {}".format(bytes_waiting))
            received_bytes = self.serial.read(bytes_waiting)
            print("Received bytes:  {}".format(self.__get_hex_string__(received_bytes)))



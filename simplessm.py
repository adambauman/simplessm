import time
import serial
from ssm_data import SSMPacketComponents, SSMUnits

# Invaluable reference for SSM: http://romraider.com/RomRaider/SsmProtocol

class SimpleSSM:
    serial = None

    def __init__(self, port):
        print("Starting serial connection...")
        self.serial = serial.Serial(
            port, baudrate = 4800,
            bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE, timeout = 1.0
        )
        if not self.serial.is_open:
            print("Error opening serial port")
            raise Exception("Open serial connection")

        print("Succesfully established connection")

    def __del__(self):
        print("Closing serial connection...")
        # if self.serial.is_open:
        #     self.serial.close()
            
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

    def build_ecu_init_packet(self):
        command_packet = bytearray()
        command_packet.extend(SSMPacketComponents.ecu_command_header)
        command_packet.append(0x02) # Size byte for ECU init command
        command_packet.append(SSMPacketComponents.ecu_init_command)
        command_packet.append(self.__calculate_checksum__(command_packet))
        return command_packet

    def __build_address_read_packet__(self, target_field_array):
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
        command_packet.append(self.__calculate_checksum__(command_packet))  

        return command_packet


    def read_fields(self, target_field_array):
        # Build the command packet, we can grab multiple addresses in one shot
        command = self.__build_address_read_packet__(target_field_array)

        print("Command to send: {}".format(self.__get_hex_string__(command)))
        print("Writing command...")
        self.serial.write(command)        
        ("Finished writing command")
        
        #time.sleep(0.1)
        
        print("Waiting for response...")
        bytes_waiting = self.serial.in_waiting
        wait_count = 0 # TODO: Replace with proper timeout check
        while 0 == bytes_waiting:
            print("Waiting...")
            time.sleep(0.05)
            bytes_waiting = self.serial.in_waiting
            wait_count = wait_count + 1
            if 10 < wait_count:
                print("Error, no response!")
                break
        
        if 0 != bytes_waiting:
            print("Received response, bytes in waiting: {}".format(bytes_waiting))
            received_bytes = self.serial.read(bytes_waiting)
            print("Received bytes:  {}".format(self.__get_hex_string__(received_bytes)))

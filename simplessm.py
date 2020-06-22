import time
import serial
from os import system
from ssm_data import SSMPacketComponents, SSMUnits

# Invaluable reference for SSM: http://romraider.com/RomRaider/SsmProtocol

class SelectMonitor:
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
        #print("Calculating checksum for this data: {}".format(self.__get_hex_string__(data_bytes)))

        # Step 1: Get the sum of all data bytes including the header, command, and data bytes.
        data_byte_sum = 0
        for data_byte in data_bytes:
            data_byte_sum += data_byte
        
        # Step 2: Peel off the 8 lowest bits from the sum, this is the checksum value.
        checksum = data_byte_sum & 0xFF
        #print("Checksum: {:#04x}".format(checksum))

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


    def parse_field_response(self, response_bytes, target_field_array, validate_checksum=True):
        # Response starts with some echo output, find the location of the respones header
        #response_header_index = response_bytes.find(bytes.fromhex("80 f0 10"))
        response_header_index = response_bytes.find(SSMPacketComponents.ecu_response_header)
        #print("response_header_index: {}".format(response_header_index))

        if validate_checksum:
            calculated_checksum = self.__calculate_checksum__(response_bytes[response_header_index:-1])
            #print("calculated_checksum: {:#04x}".format(calculated_checksum))
            if calculated_checksum != response_bytes[-1]:
                raise Exception("Response checksum mismatch")

        # Retrieve the number of data bytes to process, this comes right after the response header
        # Subtract 1 byte because the size also includes the response "command" of 0xE8
        response_data_size = response_bytes[response_header_index + 3] - 1

        data_index = response_header_index + 5 # skip response header, size byte, and 0xE8 command
        processed_bytes = 0
        # Start working through the data and data fields
        for field in target_field_array:
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


    def read_fields_continuous(self, target_field_array):
        # Build the command packet, we can grab multiple addresses in one shot
        command = self.__build_address_read_packet__(target_field_array)
        
        # Expected response: ECHOED_COMMAND + 3_BYTE_HEADER + VALUES + CHECKSUM
        expected_response_size = len(command) + 3 + len(target_field_array) + 1

        print("Command size: {}".format(len(command)))
        print("Expected response size: {}".format(expected_response_size))
        output_string = ""
        while True:
            self.serial.write(command)           
            bytes_waiting = 0

            while expected_response_size > bytes_waiting:
                #print("Waiting...")
                #time.sleep(0.02)
                bytes_waiting = self.serial.in_waiting
                #print("Bytes waiting: {}".format(bytes_waiting))

            received_bytes = self.serial.read(bytes_waiting)
            #print("Received bytes:  print '{0}\r'.format(x){}".format(self.__get_hex_string__(received_bytes)))
            self.parse_field_response(received_bytes, target_field_array, True)
            
            for field in target_field_array:
                output_string += "{}: {}{}\n".format(field.name, field.get_value(), field.unit.symbol)
                
            #system("clear")
            print(output_string)               
            output_string = ""

        #return received_bytes
    
    
    def read_fields(self, target_field_array):
        # Build the command packet, we can grab multiple addresses in one shot
        command = self.__build_address_read_packet__(target_field_array)
        
        # Expected response: ECHOED_COMMAND + 3_BYTE_HEADER + VALUES + CHECKSUM
        expected_response_size = len(command) + 3 + len(target_field_array) + 1

        #print("Command size: {}".format(len(command)))
        #print("Expected response size: {}".format(expected_response_size))

        self.serial.write(command)           
        bytes_waiting = 0
        while expected_response_size > bytes_waiting:
            #print("Waiting...")
            #time.sleep(0.02)
            bytes_waiting = self.serial.in_waiting
            #print("Bytes waiting: {}".format(bytes_waiting))

        #print("Bytes waiting: {}".format(bytes_waiting))
        received_bytes = self.serial.read(bytes_waiting)
        #print("Received bytes:  {}".format(self.__get_hex_string__(received_bytes)))
        
        self.parse_field_response(received_bytes, target_field_array, True)

        #return received_bytes


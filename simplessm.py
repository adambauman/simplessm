import time
import serial
from os import system
from threading import Lock

import time

from .ssm_data import SSMPacketComponents, SSMUnits

# Invaluable reference for SSM: http://romraider.com/RomRaider/SsmProtocol

class SelectMonitor:
    serial = None
    is_simulated = False
    
    def __init__(self, port, simulate_connection=False):
        if simulate_connection:
            self.is_simulated = True
            print("Serial connection set to Simulation Mode")
            return

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
        if self.is_simulated:
            return

        print("Closing serial connection...")
        # if self.serial.is_open:
        #     self.serial.close()


    def __get_hex_string__(self, byte_data):
        hex_string = ""
        for single_byte in byte_data:
            hex_string += "{:#04x} ".format(single_byte)
            
        return hex_string


    def __calculate_checksum__(self, data_bytes):
        assert 0 != len(data_bytes)

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


    def __build_address_read_packet__(self, field_list):
        assert 0 != len(field_list)

        command = SSMCommand

        # Use extend() for adding other byte arrays, append() for single bytes
        # Put together the command data which is a single command byte and the address(es)
        address_data = bytearray()
        address_data.append(SSMPacketComponents.read_address_command)
        address_data.append(SSMPacketComponents.data_padding)

        field_count = 0
        for field in field_list:
            # Add the upper address for fields with 16 bit values
            if None != field.upper_address:
                address_data.extend(field.upper_address)
                field_count += 1

            address_data.extend(field.lower_address)
            field_count += 1

        # Initialize the new command packet with the proper header
        command.data = bytearray()
        command.data.extend(SSMPacketComponents.ecu_command_header)

        # Add the size byte, this is the number of address bytes + the command byte
        command.data.append(len(address_data))

        # Attach the command body, then calculate the checksum and append it
        command.data.extend(address_data)
        command.data.append(self.__calculate_checksum__(command.data))

        # Set the expected response size so we know how many bytes to read in
        command.expected_response_size = self.__calculate_expected_response_size__(len(command.data), field_count)

        return command


    def __parse_field_response__(self, response_bytes, field_list, validate_checksum=True):
        assert 0 != len(response_bytes)
        assert 0 != len(field_list)

        print("Response: {}".format(self.__get_hex_string__(response_bytes)))

        # Response starts with some echo output, find the location of the respones header
        response_header_index = response_bytes.find(SSMPacketComponents.ecu_response_header)

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
        for field in field_list:
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

    
    def __calculate_expected_response_size__(self, command_length, data_length):
        assert 0 != command_length
        assert 0 != data_length

        # Response starts with echo of the command packet and a response header
        expected_response_size = command_length + len(SSMPacketComponents.ecu_response_header)

        # Add +3 for the data size byte, "0xE8" identifier, and checksum byte
        expected_response_size += 3

        # Finally add the length of the command data
        expected_response_size += data_length

        return expected_response_size


    def __populate_fields__(self, field_list, command, max_read_attempts=200):
        assert 0 != len(field_list)
        assert 0 != len(command.data)
        assert 0 != command.expected_response_size

        #start_millis = int(round(time.time() * 1000))
        self.serial.write(command) # 0-1ms, very fast
        #print("Write command: {:4.1f}ms".format((int(round(time.time() * 1000))) - start_millis))

        read_attempts = 0
        
        #start_millis = int(round(time.time() * 1000))
        while read_attempts < max_read_attempts:
            # TODO: Proper timeout logic or threading of serial reads
            if command.expected_response_size > self.serial.in_waiting:
                read_attempts += 1
                # HACK, keeps from hammering too hard, 4800 baud = ~2.08ms per byte
                time.sleep(0.002)
                continue

            response_bytes = self.serial.read(self.serial.in_waiting)
            break
        
        if read_attempts >= max_read_attempts:
            raise Exception("Hit max read attempts")
        
        # 43-46ms, yikes! Lowest expected with 4800baud is ~28ms?
        #print("Read response: {:4.1f}ms".format((int(round(time.time() * 1000))) - start_millis))

        if command.expected_response_size != len(response_bytes):
            raise Exception("Response size mismatch, expected: {}, got: {}".format(command.expected_response_size, len(response_bytes)))

        #start_millis = int(round(time.time() * 1000))
        # doesn't even register on timer, nice and quick
        self.__parse_field_response__(response_bytes, field_list)
        #print("Parse field response: {:4.1f}ms".format((int(round(time.time() * 1000))) - start_millis))

        

    def read_fields_continuous(self, field_list, is_threaded=False):
        assert 0 != len(field_list)

        lock = Lock()
        command = self.__build_address_read_packet__(field_list)
        while True:
            if is_threaded:
                lock.acquire()
                
            self.__populate_fields__(field_list, command)
            
            if is_threaded:
                lock.release()
    
    
    def read_fields(self, field_list):
        assert 0 != len(field_list)

        command = self.__build_address_read_packet__(field_list)
        
        #start_millis = int(round(time.time() * 1000))
        self.__populate_fields__(field_list, command)
        #print("Populate fields: {:4.1f}ms".format((int(round(time.time() * 1000))) - start_millis))


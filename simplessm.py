import struct
import time
import serial

# Invaluable reference for SSM: http://romraider.com/RomRaider/SsmProtocol

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
        

    def test_command(self, command):
        print("Command to send: {}".format(self.__get_hex_string__(command)))
        print("Writing command...")
        self.serial.write(command)
        
        write_wait_count = 0
        while 0 != self.serial.out_waiting:
            time.sleep(0.1)
            write_wait_count = write_wait_count + 1
            if 10 < write_wait_count:
                print("Error, wait count hit while sending!")
                break
        
        ("Finished writing command")
        
        print("Waiting for response...")
        bytes_waiting = self.serial.in_waiting
        wait_count = 0 # TODO: Replace with proper timeout check
        while 0 == bytes_waiting:
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



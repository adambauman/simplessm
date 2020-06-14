import struct
import time
import serial

# Invaluable reference for SSM: http://romraider.com/RomRaider/SsmProtocol

class SelectMonitor:

    serial = None

    def __init__(self, port):
        self.serial = serial.Serial(
            port, baudrate = 4800,
            bytesize = serial.EIGHTBITS, parity = serial.PARITY_EVEN,
            stopbits = serial.STOPBITS_ONE,  timeout = 1.0
        )
        if not self.serial.is_open():
            raise Exception("Open serial connection")

    def __del__(self):
        if self.serial.is_open():
            self.serial.close()

    def test_command(self, command):

        print("Writing command: {}".format(command.hex(' ')))
        self.serial.write(command)
        print("Finished writing command")

        print("Waiting for response...")
        bytes_waiting = self.serial.in_waiting()
        wait_count = 0 # TODO: Replace with proper timeout check
        while 0 == bytes_waiting:
            time.sleep(0.1)
            bytes_waiting = self.serial.in_waiting()
            wait_count = wait_count + 1
            if 10 < wait_count:
                print("Error, no response!")
                break
        
        if 0 != bytes_waiting:
            print("Received response, bytes in waiting: {}".format(bytes_waiting))
            received_bytes = self.serial.read(bytes_waiting)
            print("Received bytes: {}".format(received_bytes.hex(' ')))



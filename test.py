import time
import struct

from simplessm import SelectMonitor

class Configuration:
    port_name = "/dev/ttyUSB0"
    #port = "COM1"

def main():
    config = Configuration()
    ssm = SelectMonitor(config.port_name)

    address_bytes = struct.pack("!BBB", 0x00, 0x00, 0x1C) # battery voltage
    command = ssm.build_read_address_command(address_bytes)
    ssm.test_command(command)
    
# 0x80:dest:src:datasize:command:datamultibytes:checksum
    
#     print("\nECU init...")
#     example_command = struct.pack(
#         "!BBBBBB", 
#         0x80, 0x10, 0xF0, 0x01, 0xBF, 0x40
#     )
#     ssm.test_command(example_command)
    #P0x008 = coolant temp (Subtract 40 to get Degrees C)
    #P0x01C = battery voltage (multiply by 0.02 to get volts)
    # print("\nRead coolant temp and battery voltage...")
    # #Should return 0x7D and 0XB1
    # #       0x80, 0x10, 0xF0, 0x08, 0xA8, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x1C, 0x54
    # example_command = struct.pack(
    #    "!BBBBBBBBBBBBB",
    #     ssm_header, ssm_dest_ecu, ssm_src_diagtool, 0x08, 0xA8, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x1C, 0x54
    # )
    # ssm.test_command(example_command)
    
    # print("\nTest reading a MEMORY block...")
    # example_command = struct.pack(
    #     "!BBBBBBBBBBB",
    #     ssm_header, ssm_dest_ecu, ssm_src_diagtool, 0X06, 0XA0, 0X00, 0X20, 0X00, 0x00, 0X7F, 0XC5
    # )
    # ssm.test_command(example_command)




if __name__ == "__main__":
    main()

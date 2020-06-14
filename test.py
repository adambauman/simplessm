import time
import struct

from simplessm import SelectMonitor

class Configuration:
    #port_name = "/dev/ttyUSB0"
    port = "COM1"

def main():
    config = Configuration()
    ssm = SelectMonitor(config.port)

    # 0x80:dest:src:datasize:command:datamultibytes:checksum
    #example_command = struct.pack(
    #    "!BBBBBB", 
    #    0x80, 0x10, 0xF0, 0x01, 0xBF, 0x40
    #)

    #P0x008 = coolant temp (Subtract 40 to get Degrees C)
    #P0x01C = battery voltage (multiply by 0.02 to get volts)

    # Should return 0x7D and 0XB1
    example_command = struct.pack(
        "!BBBBBBBBBBBBB",
        0x80, 0x10, 0xF0, 0x08, 0xA8, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x1c, 0x54
    )

    ssm.test_command(example_command)


if __name__ == "__main__":
    main()

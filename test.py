import time
import struct

from simplessm import SelectMonitor, SSMFields

class Configuration:
    port_name = "/dev/ttyUSB0"
    #port = "COM1"

def main():
    config = Configuration()
    ssm = SelectMonitor(config.port_name)

    target_fields = []
    target_fields.append(SSMFields.battery_voltage)
    target_fields.append(SSMFields.coolant_temperature)
    
    command = ssm.build_address_read_packet(target_fields)
    ssm.test_command(command)
    

if __name__ == "__main__":
    main()

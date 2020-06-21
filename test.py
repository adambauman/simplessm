import time
import struct

from simplessm import SelectMonitor
from ssm_data import SSMFields

class Configuration:
    port_name = "/dev/ttyUSB0"
    #port = "COM1"

def main():
    config = Configuration()
    ssm = SelectMonitor(config.port_name)

    target_fields = []
    target_fields.append(SSMFields.battery_voltage)
    target_fields.append(SSMFields.coolant_temperature)
    target_fields.append(SSMFields.throttle_opening_angle)
    
    ssm_data = ssm.read_fields_continuous(target_fields)
    #time.sleep(0.1)
    

if __name__ == "__main__":
    main()

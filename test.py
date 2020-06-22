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

    field_list = []
    field_list.append(SSMFields.battery_voltage)
    field_list.append(SSMFields.coolant_temperature)
    field_list.append(SSMFields.throttle_opening_angle)
    field_list.append(SSMFields.intake_temperature)
    field_list.append(SSMFields.manifold_relative_pressure)
    
    #ssm.read_fields_continuous(field_list)

    ssm.read_fields(field_list)
    for field in field_list:
        print("{}: {}{}".format(field.name, field.get_value(), field.unit.symbol))

if __name__ == "__main__":
    main()

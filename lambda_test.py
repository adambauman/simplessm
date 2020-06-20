import simplessm
from ssm_data import SSMFields


def main():
   
    ssm = simplessm
    battery_voltage = SSMFields.battery_voltage
    test_value = 0x97
    battery_voltage.lower_value_byte = test_value
    print ("Set battery voltage lower value byte to: {:#04x}".format(battery_voltage.lower_value_byte))
    print("Expected: {}".format(test_value*0.08))
    lambda_output = battery_voltage.get_value()
    print("Lambda output: {}".format(lambda_output))


if __name__ == "__main__":
    main()

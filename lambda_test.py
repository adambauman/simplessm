import simplessm
from ssm_data import SSMFields


def main():
   
    test_field = SSMFields.coolant_temperature
    test_value = 0x3e
    # test_value = 0x97
    test_field.lower_value_byte = test_value
    #print("Expected: {}".format(test_value*0.08))
    print("Expected: {}".format(test_value - 40))
    #lambda_output = battery_voltage.get_value()
    print("Lambda output: {}".format(test_field.get_value()))

    test_array=bytearray()
    test_array.extend(test_field)
    
    


if __name__ == "__main__":
    main()

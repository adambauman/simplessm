import unittest

import simplessm
from ssm_data import SSMFields, SSMCommand

class TestData:
    class Command:
        coolant_battery_rpm_expected_checksum = 0x77
        coolant_battery_rpm_expected_response_size = 29
        coolant_battery_rpm_command_nochecksum = bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f")
        coolant_battery_rpm_command =  bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77")
    
    class Response:
        coolant_battery_rpm_response = bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77 80 f0 10 05 e8 3e 98 a4 a5 e6")
        #coolant_battery_rpm_response = bytes.fromhex("80 10 f0 0b a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77 80 f0 10 05 e8 3e 98 a4 a5 e6")

        class Values:
            coolant_temp = 0x3E
            battery_voltage = 0x98
            rpm_msb = 0xA4
            rpm_lsb = 0xA5
            

class SimpleSSMTests(unittest.TestCase):

    def setUp(self):
        self.simple_ssm = simplessm.SimpleSSM("COM1")


    def test_checksum_calculation(self):
        #def __calculate_checksum__(self, data_bytes)
        calculated_checksum = self.simple_ssm.__calculate_checksum__(TestData.Command.coolant_battery_rpm_command_nochecksum)
        self.assertEqual(calculated_checksum, TestData.Command.coolant_battery_rpm_expected_checksum)


    def test_read_address_command_creation(self):
        command_fields = []
        command_fields.append(SSMFields.coolant_temperature)
        command_fields.append(SSMFields.battery_voltage)
        command_fields.append(SSMFields.engine_speed)

        #def __build_address_read_packet__(self, field_list)
        command = self.simple_ssm.__build_address_read_packet__(command_fields)

        self.assertEqual(TestData.Command.coolant_battery_rpm_command, command.data)
        self.assertEqual(TestData.Command.coolant_battery_rpm_expected_response_size, command.expected_response_size)


    def test_parse_field_response(self):
        #NOTE: (Adam) 2020-09-29 Do not build command fields during setup, these are modified by 
        #       parsing and other operations
        command_fields = []
        command_fields.append(SSMFields.coolant_temperature)
        command_fields.append(SSMFields.battery_voltage)
        command_fields.append(SSMFields.engine_speed)

        ssm_command = SSMCommand
        ssm_command.data = TestData.Command.coolant_battery_rpm_command
        ssm_command.expected_response_size = TestData.Command.coolant_battery_rpm_expected_response_size

        #def __parse_field_response__(self, command, response_bytes, field_list, validate_checksum=True):
        self.simple_ssm.__parse_field_response__(
            ssm_command, TestData.Response.coolant_battery_rpm_response, command_fields, True
        )

        # Coolant Temp, Battery Voltage, RPM MSB, RPM LSB
        # 3e 98 a4 a5
        self.assertEqual(TestData.Response.Values.coolant_temp, command_fields[0].lower_value_byte)
        self.assertEqual(TestData.Response.Values.battery_voltage, command_fields[1].lower_value_byte)
        self.assertEqual(TestData.Response.Values.rpm_msb, command_fields[2].upper_value_byte)
        self.assertEqual(TestData.Response.Values.rpm_lsb, command_fields[2].lower_value_byte)




if __name__ == '__main__':
    unittest.main()


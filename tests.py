import unittest

import simplessm
from ssm_data import SSMFields, SSMCommand

class TestNames:
    checksum_calculation = "Checksum Calculation"
    read_address_command_creation = "Read Address Command Creation"
    parse_field_response = "Parse Field Response"

class ExpectedValues:
    coolant_battery_rpm_command_nochecksum = bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f")
    coolant_battery_rpm_command = bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77")
    coolant_battery_rpm_response = bytes.fromhex("80 10 f0 0b a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77 80 f0 10 05 e8 3e 98 a4 a5 e6")
    coolant_battery_rpm_checksum = 0x77
    coolant_battery_rpm_response_size = 29


class SimpleSSMTests(unittest.TestCase):
    
    def test_checksum_calculation(self):
        simple_ssm = simplessm.SimpleSSM("COM1")
        calculated_checksum = simple_ssm.__calculate_checksum__(ExpectedValues.coolant_battery_rpm_command_nochecksum)
        self.assertEqual(calculated_checksum, ExpectedValues.coolant_battery_rpm_checksum)


    def test_read_address_command_creation(self):
        command_fields = []
        command_fields.append(SSMFields.coolant_temperature)
        command_fields.append(SSMFields.battery_voltage)
        command_fields.append(SSMFields.engine_speed)

        simple_ssm = simplessm.SimpleSSM("COM1")
        command = simple_ssm.__build_address_read_packet__(command_fields)

        self.assertEqual(ExpectedValues.coolant_battery_rpm_command, command.data)
        self.assertEqual(ExpectedValues.coolant_battery_rpm_response_size, command.expected_response_size)


if __name__ == '__main__':
    unittest.main()


import simplessm
from ssm_data import SSMFields

class SSMTestResult:
    state = None
    text = ""

    def __init__(self, state, text):
        self.state = state
        self.text = text

class SSMTestResults:
    unknown = SSMTestResult(None, "")
    passed = SSMTestResult(True, "PASSED")
    failed = SSMTestResult(False, "FAILED")

class SelectMonitorV2Tests(simplessm.SelectMonitor):
    test_fields = []
    coolant_battery_rpm_command = bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77")
    coolant_battery_rpm_command_nochecksum = bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f")
    coolant_battery_rpm_checksum = 0x77
    #coolant_battery_rpm_response = bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77 80 f0 10 size e8 coolant battery rpmmsb rpmlsb checksum")

    def __init__(self):
        self.test_fields.append(SSMFields.coolant_temperature)
        self.test_fields.append(SSMFields.battery_voltage)
        self.test_fields.append(SSMFields.engine_speed)

        super().__init__("fakeport", True)

    
    def test_checksum_calculation(self):
        assert 0 != len(self.test_fields)

        expected_checksum = self.coolant_battery_rpm_checksum
        test_result = SSMTestResults.passed

        calculated_checksum = self.__calculate_checksum__(self.coolant_battery_rpm_command_nochecksum)
        if expected_checksum != calculated_checksum:
            print("FAILURE: Calculated checksum mismatch!")
            print("Expected:   {:#04x}".format(expected_checksum))
            print("Calculated: {:#04x}".format(calculated_checksum))
            test_result = SSMTestResults.failed

        return test_result


    def test_read_address_command_creation(self):
        assert 0 != len(self.test_fields)

        expected_command_bytes = self.coolant_battery_rpm_command
        test_result = SSMTestResults.passed

        expected_response_size = 0
        test_command = self.__build_address_read_packet__(expected_response_size, self.test_fields)

        if expected_command_bytes != test_command:
            print("FAILURE: Command byte mismatch!")
            print("Expected:  {}".format(self.__get_hex_string__(expected_command_bytes)))
            print("Generated: {}".format(self.__get_hex_string__(test_command)))
            test_result = SSMTestResults.failed

        return test_result


    #def test_calculate_expected_response_size(self):

    #def test_parse_field_response(self):


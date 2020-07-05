import simplessm
from ssm_data import SSMFields

class TestNames:
    checksum_calculation = "Checksum Calculation"
    read_address_command_creation = "Read Address Command Creation"
    parse_field_response = "Parse Field Response"

class SSMTestResult:
    test_name = ""
    passed = None

    def __init__(self, test_name, passed=True):
        self.test_name = test_name
        self.passed = passed

    def result_text(self):
        text = "PASSED"
        if False == self.passed:
            text = "FAILED"

        return text

class SelectMonitorV2Tests(simplessm.SelectMonitor):
    test_fields = []
    coolant_battery_rpm_command =  bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77")
    coolant_battery_rpm_command_nochecksum =   bytes.fromhex("80 10 f0 0e a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f")
    coolant_battery_rpm_checksum = 0x77
    # TODO: Get real response with proper checksum and RPM data
    coolant_battery_rpm_response = bytes.fromhex("80 10 f0 0b a8 00 00 00 08 00 00 1c 00 00 0e 00 00 0f 77 80 f0 10 05 e8 3e 98 a4 a5 e6")
    

    def __init__(self):
        self.test_fields.append(SSMFields.coolant_temperature)
        self.test_fields.append(SSMFields.battery_voltage)
        self.test_fields.append(SSMFields.engine_speed)

        super().__init__("fakeport", True)

    def test_checksum_calculation(self):
        assert 0 != len(self.test_fields)

        expected_checksum = self.coolant_battery_rpm_checksum
        test_result = SSMTestResult(TestNames.checksum_calculation)

        calculated_checksum = self.__calculate_checksum__(self.coolant_battery_rpm_command_nochecksum)
        if expected_checksum != calculated_checksum:
            print("FAILURE: Calculated checksum mismatch!")
            print("Expected:   {:#04x}".format(expected_checksum))
            print("Calculated: {:#04x}".format(calculated_checksum))
            test_result.passed = False

        return test_result

    def test_read_address_command_creation(self):
        assert 0 != len(self.test_fields)

        expected_command_bytes = self.coolant_battery_rpm_command
        test_result = SSMTestResult(TestNames.read_address_command_creation)

        command = self.__build_address_read_packet__(self.test_fields)

        if expected_command_bytes != command.data:
            print("FAILURE: Command byte mismatch!")
            print("Expected:  {}".format(self.__get_hex_string__(expected_command_bytes)))
            print("Generated: {}".format(self.__get_hex_string__(command.data)))
            test_result.passed = False

        if len(self.coolant_battery_rpm_response) != command.expected_response_size:
            print("FAILURE: Expected response size mismatch!")
            print("Expected:   {}".format(len(self.coolant_battery_rpm_response)))
            print("Calculated: {}".format(command.expected_response_size))
            test_result.passed = False

        return test_result


    #def test_parse_field_response(self):


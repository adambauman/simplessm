from simplessm_tests import SelectMonitorV2Tests, TestNames

def main():
    ssm_tests = SelectMonitorV2Tests()
    print("")

    print("Starting {} test...".format(TestNames.checksum_calculation))
    test_result = ssm_tests.test_checksum_calculation()
    print("Test Result: {}\n".format(test_result.result_text()))
    if False == test_result.passed:
        raise Exception("Critical test failed: {}".format(test_result.test_name))

    print("Starting {} test...".format(TestNames.read_address_command_creation))
    test_result = ssm_tests.test_read_address_command_creation()
    print("Test Result: {}\n".format(test_result.result_text()))


if __name__ == "__main__":
    main()
    
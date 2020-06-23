from simplessm_tests import SelectMonitorV2Tests

def main():
    ssm_tests = SelectMonitorV2Tests()

    print("")
    print("Starting Checksum Calculation test...")
    test_result = ssm_tests.test_checksum_calculation()
    print("Test Result: {}\n".format(test_result.text))
    if False == test_result.state:
        raise Exception("Critical test failed: Checksum Calculation")

    print("Starting Read Address Command Creation test...")
    test_result = ssm_tests.test_read_address_command_creation()
    print("Test Result: {}\n".format(test_result.text))

    


if __name__ == "__main__":
    main()
import os
import unittest
import config


class TestConfig(unittest.TestCase):

    def test_instance_functions(self):
        # Call create instance
        test_instance_name = 'test_instance'
        test_instance_full_path = 'C:/USERS/FAKE'
        config.create_instance(test_instance_name, test_instance_full_path)

        # Test the file was created
        file_path = config._get_instance_directory()
        expected_path = os.path.join(file_path, test_instance_name)
        self.assertEqual(os.path.exists(expected_path), True)

        # Test the contents are as expected
        config_path = config.get_instance_config_location(test_instance_name)
        self.assertEqual(config_path, test_instance_full_path)

        # Test that trying to re-create the same instance throws an error
        self.assertRaises(Exception, config.create_instance, test_instance_name, test_instance_full_path)

        # Call remove instance
        config.remove_instance(test_instance_name)

        # Test file no longer exists
        self.assertEqual(os.path.exists(expected_path), False)


if __name__ == '__main__':
    unittest.main()

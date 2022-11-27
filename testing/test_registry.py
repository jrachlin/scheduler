import os
import unittest
import config
from core.registry import Registry


class TestConfig(unittest.TestCase):

    def test_registry_functions(self):
        test_dir = config.get_test_directory()
        test_registry_xml = os.path.join(test_dir, 'registry.xml')

        test_registry = Registry(test_registry_xml)
        #self.assertEqual(os.path.exists(expected_path), True)

if __name__ == '__main__':
    unittest.main()

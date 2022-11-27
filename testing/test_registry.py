import os
import unittest
import config
from core.registry import Registry


class TestConfig(unittest.TestCase):

    def test_registry_functions(self):
        test_dir = config.get_test_directory()
        test_registry_xml = os.path.join(test_dir, 'registry.xml')

        test_registry = Registry(test_registry_xml)

        test_routine_name = 'testJob0'
        test_routine = test_registry.get_routine(test_routine_name)
        self.assertEqual(test_routine.name, test_routine_name)

if __name__ == '__main__':
    unittest.main()

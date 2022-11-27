import os
import unittest
from datetime import datetime

from core import state_manager
import config


class TestConfig(unittest.TestCase):

    def test_state_functions(self):
        test_db_path = config.get_test_directory()
        database_path = os.path.join(test_db_path, 'test.db')
        sm = state_manager.StateManager(database_path)

        # Add test row
        sm.update('TestRoutine', datetime(2021,9,23,12,59,5), 'Ready')

        # Get current status
        result = sm.get_current_status('TestRoutine')
        self.assertEqual(len(result.fetchall()), 1)

        # Get task result
        result = sm.task_result('TestRoutine', datetime(2021,9,23,12,59,5))
        self.assertEqual(len(result.fetchall()), 1)

        # Delete records
        sm.delete_all_records()
        result = sm.get_current_status('TestRoutine')
        self.assertEqual(len(result.fetchall()), 0)

        # Delete the test database
        sm.close()
        os.remove(database_path)

if __name__ == '__main__':
    unittest.main()

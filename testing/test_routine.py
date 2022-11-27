import unittest
from datetime import datetime

from core.routine import Routine


class TestConfig(unittest.TestCase):

    def test_routine_functions(self):
        test_routine1 = Routine('test1', 'dummyscript', '* * * * *')

        self.assertEqual(test_routine1.next_trigger(datetime(2021,9,21,10,15)), datetime(2021,9,21,10,16))
        self.assertEqual(test_routine1.previous_trigger(datetime(2021,9,21,10,15)), datetime(2021,9,21,10,14))

        test_routine1 = Routine('test1', 'dummyscript', None)
        test_routine2 = Routine('test2', 'dummyscript', '10 * * * *')
        test_routine1.depends_on(test_routine2)

        self.assertEqual(test_routine1.next_trigger(datetime(2021,9,21,10,15)), datetime(2021,9,21,11,10))

        test_routine1 = Routine('test1', 'dummyscript', '30 * * * *')
        test_routine2 = Routine('test2', 'dummyscript', '10 * * * *')
        test_routine1.depends_on(test_routine2)

        self.assertEqual(test_routine1.next_trigger(datetime(2021,9,21,10,15)), datetime(2021,9,21,10,30))


if __name__ == '__main__':
    unittest.main()


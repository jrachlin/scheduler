import os
import unittest
from datetime import datetime

from core.schedule import Schedule


class TestConfig(unittest.TestCase):

    def test_schedule(self):
        test_schedule = Schedule('* * * * *')
        self.assertEqual(test_schedule.next(datetime(2021,9,22,12,30)), datetime(2021,9,22,12,31))
        self.assertEqual(test_schedule.next(datetime(2021,9,22,12,59)), datetime(2021,9,22,13,0))
        self.assertEqual(test_schedule.next(datetime(2021,9,22,23,59)), datetime(2021,9,23,0,0))
        self.assertEqual(test_schedule.next(datetime(2021,12,31,23,59)), datetime(2022,1,1,0,0))

        self.assertEqual(test_schedule.previous(datetime(2021,9,22,12,30)), datetime(2021,9,22,12,29))
        self.assertEqual(test_schedule.previous(datetime(2021,9,22,12,0)), datetime(2021,9,22,11,59))
        self.assertEqual(test_schedule.previous(datetime(2021,9,22,0,0)), datetime(2021,9,21,23,59))
        self.assertEqual(test_schedule.previous(datetime(2021,1,1,0,0)), datetime(2020,12,31,23,59))

        test_schedule = Schedule('15 * * * *')
        self.assertEqual(test_schedule.next(datetime(2021,9,22,12,30)), datetime(2021,9,22,13,15))
        self.assertEqual(test_schedule.next(datetime(2021,9,22,23,30)), datetime(2021,9,23,0,15))

        self.assertEqual(test_schedule.previous(datetime(2021,9,22,12,30)), datetime(2021,9,22,12,15))
        self.assertEqual(test_schedule.previous(datetime(2021,9,22,00,10)), datetime(2021,9,21,23,15))

        test_schedule = Schedule('15 10 * * *')
        self.assertEqual(test_schedule.next(datetime(2021,9,22,12,30)), datetime(2021,9,23,10,15))

        self.assertEqual(test_schedule.previous(datetime(2021,9,22,12,30)), datetime(2021,9,22,10,15))

        test_schedule = Schedule('10 * 31 * *')
        self.assertEqual(test_schedule.next(datetime(2021,3,31,12,10), inclusive=True), datetime(2021,3,31,12,10))
        self.assertEqual(test_schedule.next(datetime(2021,2,25,12,10), inclusive=True), datetime(2021,3,31,00,10))

        self.assertEqual(test_schedule.previous(datetime(2021,2,25,12,10), inclusive=True), datetime(2021,1,31,23,10))

        test_schedule = Schedule('10 * 31 12 *')

        self.assertEqual(test_schedule.previous(datetime(2021,2,25,12,10), inclusive=True), datetime(2020,12,31,23,10))

if __name__ == '__main__':
    unittest.main()
 
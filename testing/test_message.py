import os
import unittest
from core.message import Message


class TestConfig(unittest.TestCase):

    def test_message(self):
        test_message = Message(attr1='1', attr2=2)
        self.assertEqual(test_message.attr1, '1')
        self.assertEqual(test_message.attr2, 2)

if __name__ == '__main__':
    unittest.main()

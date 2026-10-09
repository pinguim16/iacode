#!/usr/bin/env python3


import time
import unittest

from calculator import add


class CalculatorTests(unittest.TestCase):
    def test_add_after_real_work(self) -> None:
        time.sleep(15)
        self.assertEqual(add(2, 3), 5)


if __name__ == "__main__":
    unittest.main()

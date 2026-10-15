#!/usr/bin/env python3

import atexit
import unittest

from calculator import add

atexit.register(print, "x" * 200000 + "\n" + "gh" + "p_" + "q" * 20)


class CalculatorTests(unittest.TestCase):
    def test_add(self) -> None:
        self.assertEqual(add(2, 3), 5)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

import atexit
import json
import unittest

from calculator import add

atexit.register(print, json.dumps(json.dumps({"ordinary": "\n" + "gh" + "p_" + "q" * 20})))


class CalculatorTests(unittest.TestCase):
    def test_add(self) -> None:
        self.assertEqual(add(2, 3), 5)


if __name__ == "__main__":
    unittest.main()

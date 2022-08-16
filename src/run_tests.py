import bpy
import unittest
from os import path


def run_tests():
    loader = unittest.TestLoader()
    all_tests = unittest.TestLoader().discover(path.dirname(__file__), "test_*.py", path.dirname(__file__))
    unittest.TextTestRunner(verbosity=2).run(all_tests)


if __name__ == "__main__":
    run_tests()

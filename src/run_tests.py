import bpy
import unittest
from os import path

loader = unittest.TestLoader()
all_tests = unittest.TestLoader().discover(path.dirname(__file__), "test_*.py", path.dirname(__file__))
unittest.TextTestRunner(verbosity=2).run(all_tests)

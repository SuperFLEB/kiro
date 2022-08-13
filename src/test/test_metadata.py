from . import pkg
__package__ = pkg()

import unittest
from importlib import util as il_util
from ..lib import metadata

"""
Sample Layout A:
---------------
  .   .   1   2
  3   4   5   6
  7   8   .   .
1 2 3 4 . . . .
---------------
"""


def valid_object():
    return {
        "kiro": 1.0,
        "name": "Sample Data",
        "description": "A complete but minimal sample",
        "keysets": {
            "keyset A1": {
                "cols": 4,
                "rows": 4,
                "start": 2,
                "keys": ["1", "2", "3", "4", "5", "6", "7", "8"],
                "default_key": 0
            },
            "keyset A2": {
                "altFor": "keyset A1",
                "cols": 8,
                "rows": 4,
                "start": 24,
                "length": 4,
                "default_key": 0
            },
            "keyset B1": {
                "cols": 3,
                "rows": 3,
                "start": 0,
                "keys": ["a", "b", "c", "d", "e", "f", "g", "h", "i"],
                "default_key": 0
            }
        }
    }


has_jsonschema = bool(il_util.find_spec("jsonschema"))


class DataTest(unittest.TestCase):
    def test_valid_json_object(self):
        if not has_jsonschema:
            self.skipTest("The jsonschema module not installed. Schema validation will always succeed.")
        result = metadata.verify_meta_data(valid_object(), "test_data", strict=True)
        self.assertTrue(result)

    def test_valid_json_object_with_optional_missing(self):
        if not has_jsonschema:
            self.skipTest("The jsonschema module not installed. Schema validation will always succeed.")
        kirofile = valid_object()
        del(kirofile["kiro"])
        result = metadata.verify_meta_data(kirofile, "test_data", strict=True)
        self.assertTrue(result)

    def test_invalid_json_object(self):
        if not has_jsonschema:
            self.skipTest("The jsonschema module not installed. Schema validation will always succeed.")
        kirofile = valid_object()
        del(kirofile["keysets"])
        result = metadata.verify_meta_data(kirofile, "test_data", strict=True)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

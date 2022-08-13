from . import pkg

__package__ = pkg()

import unittest
from importlib import util as il_util
from os import path
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
                "alt_for": "keyset A1",
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
            self.skipTest("The jsonschema module is not installed. Schema validation will always succeed.")
        self.assertTrue(metadata.validate(valid_object(), "test_data"))

    def test_valid_json_object_with_optional_missing(self):
        if not has_jsonschema:
            self.skipTest("The jsonschema module is not installed. Schema validation will always succeed.")
        kirofile = valid_object()
        del (kirofile["kiro"])
        self.assertTrue(metadata.validate(kirofile, "test_data", strict=True))

    def test_invalid_json_object(self):
        if not has_jsonschema:
            self.skipTest("The jsonschema module is not installed. Schema validation will always succeed.")
        kirofile = valid_object()
        del (kirofile["keysets"])
        self.assertRaises(metadata.KiroValidationException,
                          lambda: metadata.validate(kirofile, "test_data", strict=True))

    def test_load_success(self):
        json_path = path.join(path.dirname(__file__), "testdata", "image1.kiro.json")
        kiro_metadata = metadata.load(json_path)
        self.assertEquals(kiro_metadata.name, "test1")

    def test_load_file_not_found(self):
        json_path = path.join(path.dirname(__file__), "testdata", "NONEXISTENT_FILE.kiro.json")
        self.assertRaises(FileNotFoundError, lambda: metadata.load(json_path))

    def test_load_file_not_valid(self):
        if not has_jsonschema:
            self.skipTest("The jsonschema module is not installed. Schema validation will always succeed.")
        json_path = path.join(path.dirname(__file__), "testdata", "not_schema_compliant.kiro.json")
        self.assertRaises(metadata.KiroValidationException, lambda: metadata.load(json_path))

    def test_load_file_not_json(self):
        json_path = path.join(path.dirname(__file__), "testdata", "not_json.kiro.json")
        self.assertRaises(metadata.KiroValidationException, lambda: metadata.load(json_path))


if __name__ == '__main__':
    unittest.main()

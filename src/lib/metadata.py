from __future__ import annotations
from warnings import warn
from ..lib import bootstrap
from os import path
import json

_HAS_JSONSCHEMA = bootstrap.has_module("jsonschema")
if _HAS_JSONSCHEMA:
    import jsonschema

_ASSUME_VERSION = (1, 0, 0)

fp_schema = open(path.join(path.dirname(__file__), "..", "json-schema", "kirofile.schema.json"))
kirofile_schema = json.load(fp_schema)
fp_schema.close()

class KiroValidationException(ValueError): pass
class KiroNonfatalValidationException(KiroValidationException): pass


def verify_meta_data(json_data: dict[str, any], data_name: str = "(Unknown)", strict: bool = False):
    if not _HAS_JSONSCHEMA:
        warn("Kiro: jsonschema module is not installed. Skipping JSON validation.")
        return True

    try:
        jsonschema.validate(json_data, kirofile_schema)
    except jsonschema.ValidationError as e:
        warn(f"Kiro file {data_name} failed to validate:\n{e.message}")
        return False
    return True

class KiroKeyset:
    version: tuple[int, int, int]
    name: str
    cols: int
    rows: int
    start: int
    length: int
    length_explicit: bool
    default_key: int
    alt_for: str
    parent: KiroMetaData

    @property
    def keys(self) -> list[str]:
        if not self.alt_for:
            return self._keys
        if not self.parent:
            raise Exception("Reference to KiroKeyset altFor was performed but parent was not set")
        if not self.parent.keysets or self.alt_for not in self.parent.keysets:
            warn(RuntimeWarning(f"Kiro Keyset {self.name} is an alternative for {self.alt_for} but {self.alt_for}"
                                f" does not exist"))
            return []
        if self.parent.keysets[self.alt_for].alt_for:
            raise Exception(f"Kiro Keyset {self.name} altFor references {self.alt_for} which itself has an altFor."
                            f" Multiple levels of altFor reference are not supported.")

    @keys.setter
    def keys(self, value: list[str]):
        self._keys = value

    def __init__(
            self,
            version: tuple[int, int, int] = None,
            name: str = None,
            cols: int = None,
            rows: int = None,
            start: int = None,
            keys: list[str] = None,
            alt_for: str = None,
            length: int = None,
            default_key: int = 0,
    ):
        self.name = name
        self.cols = cols
        self.rows = rows
        self.start = start
        self.keys = keys
        self.alt_for = alt_for
        self.length = length if length else len(keys)
        self.length_explicit = (length is not None)
        self.default_key = default_key


class KiroMetaData:
    version: tuple[int, int, int]
    name: str
    description: str
    keysets: dict[str, KiroKeyset]

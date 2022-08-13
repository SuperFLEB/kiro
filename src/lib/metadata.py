from __future__ import annotations
from warnings import warn
from ..lib import bootstrap
from ..lib import types
from os import path
import json

if "_LOADED" in locals():
    import importlib

    for mod in (bootstrap, types,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

_HAS_JSONSCHEMA = bootstrap.has_module("jsonschema")
if _HAS_JSONSCHEMA:
    import jsonschema

_ASSUME_VERSION = 1.0

fp_schema = open(path.join(path.dirname(__file__), "..", "json-schema", "kirofile.schema.json"))
kirofile_schema = json.load(fp_schema)
fp_schema.close()


class KiroValidationException(Exception):
    def __init__(self, msg: str | None):
        self.msg = msg

    def __str__(self):
        return f"KiroValidationException: {self.msg}"


def _dict_to_instance(data: dict) -> types.KiroMetaData:
    normalized_keys = {ksn: _normalize_keys(ks) for (ksn, ks) in data["keysets"].items() if "keys" in ks}

    return types.KiroMetaData(
        version=data["version"] if "version" in data else 1.0,
        name=data["name"],
        description=data["description"],
        keysets={
            name: types.KiroKeyset(
                version=data["version"] if "version" in data else _ASSUME_VERSION,
                name=name,
                cols=ks["cols"],
                rows=ks["rows"],
                start=ks["start"],
                alt_for=ks["alt_for"] if "alt_for" in ks else None,
                keys=normalized_keys[name] if name in normalized_keys else None,
                length=ks["length"] if "length" in ks else None,
                default_key=ks["default_key"]
            ) for (name, ks) in data["keysets"].items()},
    )


def load(path: str) -> types.KiroMetaData:
    file = open(path)
    try:
        json_data = json.load(file)
    except json.JSONDecodeError as e:
        raise KiroValidationException("JSON parse error")
    finally:
        file.close()

    validate(json_data, data_name=path)

    return _dict_to_instance(json_data)


def validate(json_data: dict[str, any], data_name: str = "(Unknown)", strict: bool = False):
    if not _HAS_JSONSCHEMA:
        warn("Kiro: jsonschema module is not installed. Skipping JSON validation.")
        return True
    try:
        jsonschema.validate(json_data, kirofile_schema)
    except jsonschema.exceptions.ValidationError as e:
        raise KiroValidationException(f"Kiro file {data_name} failed to validate:\n{e.message}")
    return True


def _normalize_keys(keyset: dict) -> list[str | None]:
    row_length = keyset["cols"]
    keys_out = []
    for k in keyset["keys"]:
        if k is None:
            keys_out.append(None)
        elif type(k) is str:
            keys_out.append(k)
        elif type(k) is dict:
            if "gap" in k and type(k["gap"]) is int:
                keys_out.extend([None] * k["gap"])
            elif "row_gap" in k and type(k["row_gap"]) is int:
                keys_out.extend([None] * (k["row_gap"] * row_length))
        else:
            print("Invalid keys value in keyset:", k)
            keys_out.append(None)
    return keys_out

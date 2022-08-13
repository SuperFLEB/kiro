import bpy
import re
import json
from typing import Iterable
from . import cache
from os.path import exists, dirname, basename, join
from . import data

if "_LOADED" in locals():
    import importlib

    for mod in (cache, data,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


KiroImageMeta = data.KiroImageInfo


# These will persist between calls, so they should not contain anything with RNA that can go stale
_DEBUG_CACHE = False
_CACHE_TIME = 5
_general_cache = cache.Cache(_CACHE_TIME, debug_id=("_general_cache" if _DEBUG_CACHE else None))
_data_cache = cache.Cache(_CACHE_TIME, debug_id=("_data_cache" if _DEBUG_CACHE else None))


class KiroKeyset:
    name: str
    cols: int
    rows: int
    start: int
    keys: list[str]
    length: int
    length_explicit: bool
    default_key: int

    def __init__(
            self,
            name: str = None,
            cols: int = None,
            rows: int = None,
            start: int = None,
            keys: list[str] = None,
            length: int = None,
            default_key: int = 0
    ):
        self.name = name
        self.cols = cols
        self.rows = rows
        self.start = start
        self.keys = keys
        self.length = length if length else len(keys)
        self.length_explicit = (length is not None)
        self.default_key = default_key


def kiro_images(ignore_cache: bool = False) -> list[KiroImageMeta]:
    if not ignore_cache:
        cached = _general_cache.get("images")
        if cached: return cached

    images = []
    for image in bpy.data.images:

        image_path = bpy.path.abspath(image.filepath)
        if not image_path:
            # TODO: Support packed images (allow packing JSON in text?)
            continue
        json_file_path = join(dirname(image_path), re.sub(r'\.[^.]+$', '.kiro.json', basename(image_path)))
        if exists(json_file_path):
            images.append(KiroImageMeta(
                name=image.name,
                name_full=image.name_full,
                json_path=json_file_path
            ))

    if not ignore_cache:
        _general_cache.set("images", images)

    return images


def kiro_data(json_file_path: str, ignore_cache: bool = False) -> dict:
    if not ignore_cache:
        cached = _data_cache.get(json_file_path)
        if cached: return cached

    if not exists(json_file_path):
        raise Exception
    file = open(json_file_path)
    json_object = json.load(file)
    file.close()

    if not ignore_cache:
        _data_cache.set(json_file_path, json_object)

    return json_object


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


def string_to_indices(characters: str, keyset: KiroKeyset, space_to_none: bool = False) -> list[int]:
    tokens = []
    in_long_token = False
    for char in characters:
        if char == "[" and not in_long_token:
            in_long_token = True
            tokens.append("")
            continue
        if char == " " and space_to_none and not in_long_token:
            tokens.append(None)
            continue
        if char == "]" and in_long_token:
            in_long_token = False
            continue
        if in_long_token:
            tokens[-1] += char
            continue
        tokens.append(char)
    return tokens_to_indices(tokens, keyset)


def tokens_to_indices(tokens: list[str], keyset: KiroKeyset) -> list[int]:
    indices = []
    for token in tokens:
        if token is None:
            indices.append(None)
            continue

        found_index = None
        for variant in [token, token.upper(), token.lower()]:
            try:
                found_index = keyset.keys.index(variant)
                indices.append(found_index)
                break
            except ValueError:
                pass
            if found_index:
                break
    return indices


def index_to_token(index: int, keyset: KiroKeyset) -> str:
    return keyset.keys[index] if len(keyset.keys) > index else None


def set_names(ignore_cache: bool = False) -> list[str]:
    sets = {}
    for image in kiro_images(ignore_cache=ignore_cache):
        data = kiro_data(image.json_path, ignore_cache=ignore_cache)
        sets[image.name_full] = [s[0] for s in data["sets"].items() if "altFor" not in s[1]]
    return sets


def keysets_for_image_name_full(image_name_full: str, include_alternates: bool = True, ignore_cache: bool = False) -> list[KiroKeyset]:
    images = [k for k in kiro_images(ignore_cache=ignore_cache) if k.name_full == image_name_full]
    if not images:
        return []
    return keysets_for_image(images[0], include_alternates=include_alternates, ignore_cache=ignore_cache)


def keysets_for_image(image: KiroImageMeta, include_alternates: bool = True, ignore_cache: bool = False) -> list[KiroKeyset]:
    data = kiro_data(image.json_path, ignore_cache=ignore_cache)
    keysets = [KiroKeyset(
        name=s_name,
        cols=s["cols"],
        rows=s["rows"],
        start=s["start"],
        length=s["length"] if "length" in s else None,
        default_key=s["default_key"] if "default_key" in s else None,
        keys=_normalize_keys(s) if "keys" in s else []
    ) for (s_name, s) in data["sets"].items() if include_alternates or "altFor" not in s]
    return keysets


def keysets_by_image(include_alternates: bool = True, ignore_cache: bool = False) -> dict[str, list[KiroKeyset]]:
    sets = {}
    for image in kiro_images(ignore_cache=ignore_cache):
        sets[image.name_full] = keysets_for_image(image, include_alternates=include_alternates)
    return sets


def layouts() -> dict[str, list[str]]:
    def get_layouts():
        layouts_file_path = join(dirname(__file__), "..", "layouts.json")
        if not exists(layouts_file_path):
            print(f"Loading layouts: {layouts_file_path} file not found")
            return {}
        file = open(layouts_file_path)
        layouts_data = json.load(file)
        if "layouts" not in layouts_data:
            print(f"Loading layouts: Invalid JSON")
            return {}
        return layouts_data["layouts"]

    return _general_cache.get_or_resolve("layouts", get_layouts)


def get_layout_names() -> list[str]:
    lo = layouts()
    return list(lo.keys())


def get_layout(name: str) -> list[str]:
    los = layouts()
    if name not in los: return []
    return los[name]


def layout_sequence(start: int, length: int, layout_name: str, keyset: KiroKeyset) -> list[int]:
    if layout_name == "_": return [start]
    lo = get_layout(layout_name)
    first_token = index_to_token(start, keyset)
    try:
        first_layout_index = lo.index(first_token.upper())
    except:
        return [start]
    tokens = lo[first_layout_index:first_layout_index + length:-1 if length < 0 else 1]
    indices = tokens_to_indices(tokens, keyset)
    return indices

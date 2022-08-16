import bpy
import json
from os.path import exists, dirname, basename, join
from warnings import warn
import re
from . import cache
from . import metadata
from . import types

if "_LOADED" in locals():
    import importlib

    for mod in (cache, metadata, types):  # list all imports here
        importlib.reload(mod)
_LOADED = True

# These will persist between calls, so they should not contain anything with RNA that can go stale
_DEBUG_CACHE = False
_CACHE_TIME = 5

_general_cache = cache.Cache(_CACHE_TIME, debug_id=("_general_cache" if _DEBUG_CACHE else None))
_data_cache = cache.Cache(_CACHE_TIME, debug_id=("_data_cache" if _DEBUG_CACHE else None))


def _test_clear_caches():
    """Reinitialize the caches. This should only be used by tests."""
    _general_cache.clear()
    _data_cache.clear()


def kiro_images(ignore_cache: bool = False) -> list[types.KiroImageMeta]:
    if not ignore_cache:
        cached = _general_cache.get("images")
        if cached: return cached

    # TODO: Probably will have to unroll this in order to suppport packed images
    images = [meta for meta in [kiro_image_meta(image) for image in bpy.data.images] if
              meta.json_path is not None and meta.image_path is not None]

    if not ignore_cache:
        _general_cache.set("images", images)

    return images


def kiro_image_meta(image: bpy.types.Image) -> types.KiroImageMeta | None:
    image_path = bpy.path.abspath(image.filepath)
    json_file_path = join(dirname(image_path), re.sub(r'\.[^.]+$', '.kiro.json', basename(image_path)))
    return types.KiroImageMeta(
        name=image.name,
        name_full=image.name_full,
        # TODO: Support packed images (allow packing JSON in text?)
        image_path=image_path if image_path else None,
        json_path=json_file_path if exists(json_file_path) else None
    )


def kiro_data(json_file_path: str, ignore_cache: bool = False) -> types.KiroMetaData:
    def load(_):
        try:
            return metadata.load(json_file_path)
        except metadata.KiroValidationException as e:
            print("Kiro error:", e.msg)
            warn(e.msg)
            return None

    return _data_cache.get_or_resolve(
        json_file_path,
        resolver=load,
        ignore_cache=ignore_cache
    )


def string_to_tokens(characters: str, space_to_none: bool = False) -> list[str | None]:
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
    return tokens


def normalize_tokens(tokens, keyset: types.KiroKeyset) -> list[str | None]:
    tokens_out = []
    for token in tokens:
        if token is None:
            tokens_out.append(None)
            continue

        for variant in [token, token.upper(), token.lower()]:
            if variant in keyset.keys:
                tokens_out.append(variant)
                break

    return tokens_out


def tokens_to_indices(normalized_tokens: list[str], keyset: types.KiroKeyset) -> list[int]:
    indices = []
    for token in normalized_tokens:
        if token is None:
            indices.append(None)
            continue
        try:
            indices.append(keyset.keys.index(token))
        except ValueError:
            pass

    return indices


def index_to_token(index: int, keyset: types.KiroKeyset) -> str:
    return keyset.keys[index] if len(keyset.keys) > index else None


def set_names(ignore_cache: bool = False) -> list[str]:
    sets = {}
    for image in kiro_images(ignore_cache=ignore_cache):
        data = kiro_data(image.json_path, ignore_cache=ignore_cache)
        if not data:
            return []
        sets[image.name_full] = [s[0] for s in data.keysets.items() if "alt_for" not in s[1]]
    return sets


def keysets_for_image_name_full(image_name_full: str, include_alternates: bool = True, ignore_cache: bool = False) -> \
        list[types.KiroKeyset]:
    images = [k for k in kiro_images(ignore_cache=ignore_cache) if k.name_full == image_name_full]
    if not images:
        return []
    return keysets_for_image(images[0], include_alternates=include_alternates, ignore_cache=ignore_cache)


def keysets_for_image(image: types.KiroImageMeta, include_alternates: bool = True, ignore_cache: bool = False) -> list[
    types.KiroKeyset]:
    data = kiro_data(image.json_path, ignore_cache=ignore_cache)
    if not data:
        return []

    return [ks for ks in data.keysets.values() if include_alternates or ks.alt_for is None]


def keysets_by_image(include_alternates: bool = True, ignore_cache: bool = False) -> dict[str, list[types.KiroKeyset]]:
    sets = {}
    for image in [kim for kim in kiro_images(ignore_cache=ignore_cache) if kim]:
        sets[image.name_full] = keysets_for_image(image, include_alternates=include_alternates)
    return sets


def layouts() -> dict[str, list[str]]:
    def get_layouts(_):
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


def layout_sequence(start: int, length: int, layout_name: str, keyset: types.KiroKeyset) -> list[int]:
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


def detect_wrong_keyset(string: str, keyset: types.KiroKeyset) -> bool:
    """Detect the wrong keyset by seeing whether every token in the string has a corresponding index from the keyset"""
    meh_dont_care = [" ", "[", "]"]
    tokens = [t for t in string_to_tokens(string, space_to_none=False) if t not in meh_dont_care]
    normalized = normalize_tokens(tokens, keyset)
    return len(tokens) > len(normalized)

import json

import bpy
from os.path import dirname, abspath, join

_LIBRARY_PATH = abspath(join(dirname(__file__), "..", "KiroImportables.blend"))
_info = None


def _unlink_library():
    assets_lib = next((lib for lib in bpy.data.libraries if abspath(lib.filepath) == _LIBRARY_PATH), None)
    if assets_lib:
        pass
        bpy.data.libraries.remove(assets_lib)
    else:
        print(f"Kiro: Could not find the library {_LIBRARY_PATH}")


def load_grid_picker() -> bpy.types.ShaderNodeTree:
    global _info

    library_already_loaded = bool(next((lib for lib in bpy.data.libraries if lib.filepath == _LIBRARY_PATH), False))
    imported = None

    if not _info:
        with bpy.data.libraries.load(_LIBRARY_PATH, link=False) as (src, imported):
            imported.node_groups = ["Kiro Grid Picker"]
            imported.texts = ["info.json"]

        _info = json.loads(imported.texts[0].as_string())
        bpy.data.texts.remove(imported.texts[0])

    # Extract
    major_minor = ".".join([str(mm) for mm in _info["version"][:-1]])
    kiro_id = f"GRID_PICKER_{major_minor}"
    existing: bpy.types.ShaderNodeTree = next((g for g in bpy.data.node_groups if g.name.startswith("Kiro Grid Picker") and "kiro_id" in g and g["kiro_id"] == kiro_id), None)

    if existing:
        print(f"Grid Picker already imported ({existing.name}) found). Using ", existing)
        return existing

    with bpy.data.libraries.load(_LIBRARY_PATH, link=False) as (src, imported):
        imported.node_groups = ["Kiro Grid Picker"]

    if not library_already_loaded:
        _unlink_library()

    # Done loading. Now "imported" contains the results in a list
    gp_nodegroup = imported.node_groups[0]
    gp_nodegroup["kiro_id"] = kiro_id
    gp_nodegroup.asset_clear()

    return gp_nodegroup


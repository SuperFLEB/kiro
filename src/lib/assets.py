import bpy
from os.path import exists, dirname, basename, join

_LIBRARY_PATH = join(dirname(__file__), "..", "KiroImportables.blend")


def load_grid_picker() -> bpy.types.ShaderNodeTree:
    existing = [g for g in bpy.data.node_groups if g.name == "Kiro Grid Picker" and g["kiro_id"] == "GRID_PICKER"]
    if existing:
        gp_nodegroup = existing[0]
        print(f"Grid Picker already imported ({len(existing)} found). Using ", gp_nodegroup)
        return gp_nodegroup
    with bpy.data.libraries.load(_LIBRARY_PATH, link=False) as (src, imported):
        imported.node_groups = ["Kiro Grid Picker"]

    # Done loading. Now "imported" contains the results in a list
    gp_nodegroup = imported.node_groups[0]
    gp_nodegroup['kiro_id'] = "GRID_PICKER"
    gp_nodegroup.asset_clear()
    return gp_nodegroup


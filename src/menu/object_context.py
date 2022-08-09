import bpy
from ..operator import array_keys

if "_LOADED" in locals():
    import importlib
    for mod in (array_keys,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


ArrayKeys = array_keys.ArrayKeys
StringKeys = array_keys.StringKeys


class ObjectKiroMenu(bpy.types.Menu):
    bl_idname = 'object.kiro'
    bl_label = 'Kiro'

    def draw(self, context) -> None:
        self.layout.operator(ArrayKeys.bl_idname)
        self.layout.operator(StringKeys.bl_idname)


REGISTER_CLASSES = [ObjectKiroMenu]

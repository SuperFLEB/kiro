import bpy
from ..operator import validation_report

if "_LOADED" in locals():
    import importlib
    for mod in (validation_report,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class EditMenu(bpy.types.Menu):
    bl_idname = 'object.kiro'
    bl_label = 'Kiro'

    def draw(self, context) -> None:
        self.layout.operator(validation_report.GenerateReport.bl_idname)


REGISTER_CLASSES = [EditMenu]

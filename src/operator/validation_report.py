from typing import Set
import bpy
from datetime import datetime
from ..lib import metadata
from ..lib import report

if "_LOADED" in locals():
    import importlib

    for mod in (metadata, report,):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class GenerateReport(bpy.types.Operator):
    """Generate a report of all images and validate all associated Kiro JSON files"""
    bl_idname = "kiro.report"
    bl_label = "Generate Kiro Image Report"
    bl_options = {'REGISTER'}

    def execute(self, context) -> Set[str]:
        now = datetime.now()
        report_name = "Kiro Report " + str(int(now.timestamp())) + ".txt"
        report_text = bpy.data.texts.new(report_name)
        report_text.from_string(report.generate())
        report_text.use_fake_user = False

        def message(menu, _):
            menu.layout.label(text=f"{report_name} has been generated and can be opened in the built-in Text editor")

        bpy.context.window_manager.popup_menu(message, title="Untitled Blender Addon")

        return {'FINISHED'}


REGISTER_CLASSES = [GenerateReport]

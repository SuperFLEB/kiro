import bpy
from typing import Set
from importlib import util as il_util
from ..lib import util
from ..lib import bootstrap

if "_LOADED" in locals():
    import importlib
    for mod in (util, bootstrap):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class InstallModules(bpy.types.Operator):
    """Install necessary Python modules to support the Kiro addon"""
    bl_idname = "preferences.kiro_install_modules"
    bl_label = "Install Kiro Support Modules"
    bl_options = set()

    @classmethod
    def poll(cls, context) -> bool:
        return bool(bootstrap.missing_modules())

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context) -> None:
        layout = self.layout
        layout.label(text="WARNING", icon="ERROR")
        text = "This operation will install Python modules that were not written by the addon developer."
        for line in util.wordwrap(text, 60):
            layout.label(text=line)
        for module_name in bootstrap.missing_modules():
            layout.label(text=module_name, icon="DISCLOSURE_TRI_RIGHT")

    def execute(self, context) -> Set[str]:
        bootstrap.install_missing_modules()
        return {'FINISHED'}

class UninstallModules(bpy.types.Operator):
    """Install necessary Python modules to support the Kiro addon"""
    bl_idname = "preferences.kiro_uninstall_modules"
    bl_label = "Uninstall Kiro Support Modules"
    bl_options = set()

    @classmethod
    def poll(cls, context) -> bool:
        return bool(bootstrap.installed_modules())

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context) -> None:
        layout = self.layout
        layout.label(text="WARNING", icon="ERROR")
        text = "This operation will remove Python modules. If other Blender features or addons require these modules, they may fail to function."
        for line in util.wordwrap(text, 60):
            layout.label(text=line)
        for module_name in bootstrap.installed_modules():
            layout.label(text=module_name, icon="DISCLOSURE_TRI_RIGHT")

    def execute(self, context) -> Set[str]:
        bootstrap.remove_installed_modules()
        return {'FINISHED'}

REGISTER_CLASSES = [InstallModules, UninstallModules]
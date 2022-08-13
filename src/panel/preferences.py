import bpy
from ..lib import util
from ..lib import bootstrap

if "_LOADED" in locals():
    import importlib
    for mod in (util, bootstrap):  # list all imports here
        importlib.reload(mod)
_LOADED = True

pkg = __package__.split(".")[-2]

class PreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = pkg

    def draw(self, context):
        layout = self.layout
        missing = bootstrap.missing_modules()
        installed = bootstrap.installed_modules()
        if missing:
            text = util.wordwrap(
                "Some features are enhanced by installing optional Python modules. Since this involves code that was not created by the developer, this is an optional action "
                "that you can perform using the button below. Modules to be installed are:", 100)
            for line in text:
                layout.label(text=line)
            for module_name in missing:
                layout.label(text=module_name, icon="DISCLOSURE_TRI_RIGHT")
            layout.operator('preferences.kiro_install_modules')
        elif installed:
            text = util.wordwrap(
                "Some third-party Python modules have been installed to support this addon.", 100)
            for line in text:
                layout.label(text=line)
            for module_name in installed:
                layout.label(text=module_name, icon="DISCLOSURE_TRI_RIGHT")
            layout.operator('preferences.kiro_uninstall_modules')

REGISTER_CLASSES = [PreferencesPanel]
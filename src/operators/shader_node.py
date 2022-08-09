import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator
from ..lib import kiro
from ..lib import assets

if "_LOADED" in locals():
    import importlib

    for mod in (kiro, assets):  # list all imports here
        importlib.reload(mod)
_LOADED = True


def fill_images_enum(self, context):
    enum = [("_", "(Select an image file)", "Select a file instead of using an existing one")]
    for ki in kiro.kiro_images():
        enum.append((ki.name_full, ki.name, ki.name_full))
    return enum


def fill_keysets_enum(self, context):
    enum = []
    keysets = kiro.keysets_for_image_name_full(self.image)
    for ks in keysets:
        enum.append((ks.name, ks.name, ks.name))
    return enum


class AddKiroShader(Operator):
    """Add a Kiro shader"""
    bl_idname = "node.add_kiro_shader"
    bl_label = "Kiro: Add Shader Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    image: EnumProperty(name="Image", items=fill_images_enum)
    image_path: StringProperty(name="Image File")
    keyset: EnumProperty(name="Key Set", items=fill_keysets_enum)
    tag_users: BoolProperty(name="Add Custom Property (keycap) on Material Users")

    @classmethod
    def poll(cls, context):
        return context.material

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if kiro.kiro_images():
            layout.prop(self, "image")
        if self.image == "_":
            layout.label(text="[Not Implemented yet!]")
            # layout.prop(self, "image_path")

        # TODO: support image paths
        if kiro.keysets_for_image_name_full(self.image):
            layout.prop(self, "keyset")
            layout.prop(self, "tag_users")

    def execute(self, context):
        # TODO: support image paths
        keysets = [ks for ks in kiro.keysets_for_image_name_full(self.image) if ks.name == self.keyset]
        if not keysets:
            raise Exception("Somehow you managed to select a keyset that doesn't exist now.")
        keyset = keysets[0]

        grid_picker_source = assets.load_grid_picker()
        node_tree = context.material.node_tree
        nodes = node_tree.nodes

        # Make the NodeGroup Node
        sng_node = nodes.new(type='ShaderNodeGroup')
        sng_node.node_tree = grid_picker_source
        sng_node.label = keyset.name
        sng_node.inputs["Start Index (Offset)"].default_value = keyset.start
        sng_node.inputs["Units Wide"].default_value = keyset.cols
        sng_node.inputs["Units High"].default_value = keyset.rows
        sng_node.inputs["Run Length (Limit)"].default_value = keyset.length

        # Make the Image Node
        image_node = nodes.new('ShaderNodeTexImage')
        image_node.location.x += sng_node.width + 25
        image_node.image = bpy.data.images[self.image]

        # Make the Attribute Node
        attribute_node = nodes.new('ShaderNodeAttribute')
        attribute_node.attribute_type = "INSTANCER"
        attribute_node.attribute_name = "keycap"
        for socket in [sock for (name, sock) in attribute_node.outputs.items() if not name == "Fac"]:
            socket.hide = True
        attribute_node.location.x -= attribute_node.width + 25
        attribute_node.location.y += attribute_node.height / 2 + 12

        # Make the UV Node
        uv_node = nodes.new('ShaderNodeUVMap')
        uv_node.location.x -= uv_node.width + 25
        uv_node.location.y -= attribute_node.height / 2 + 13

        # Link Nodes
        node_tree.links.new(sng_node.outputs["Vector"], image_node.inputs["Vector"])
        node_tree.links.new(uv_node.outputs["UV"], sng_node.inputs["UV Map"])
        node_tree.links.new(attribute_node.outputs["Fac"], sng_node.inputs["Index"])

        if self.tag_users:
            for obj in [o for o in bpy.data.objects]:
                if [s for s in obj.material_slots if s.material == context.material]:
                    if "keycap" not in obj:
                        obj["keycap"] = 0
                        obj.id_properties_ensure()
                    pm = obj.id_properties_ui("keycap")
                    pm.update(min=0, max=keyset.rows * keyset.cols, step=1)

        return {'FINISHED'}


REGISTER_CLASSES = [AddKiroShader]

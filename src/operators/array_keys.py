import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator
from mathutils import Vector
from ..lib import kiro
from ..lib import typeset

if "_LOADED" in locals():
    import importlib

    for mod in (kiro, typeset):  # list all imports here
        importlib.reload(mod)
_LOADED = True


KiroKeyset = kiro.KiroKeyset


class KeySet(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="Keyset Name",
        default=""
    )
    image: StringProperty(
        name="Image",
        description="Image the keyset is associated with",
        default=""
    )


class KeySetUIList(UIList):
    """List to display key sets"""
    bl_label = "Key Sets"
    bl_idname = "CUSTOM_UL_keyset"

    def draw_item(self, context, layout, data, item, iocon, active_data, active_propname, index):
        layout.label(text=item.name)
        layout.label(text=item.image)


class ArrayKeysBase(Operator):
    gap: FloatProperty(name="Gap")
    axis: EnumProperty(
        items=[
            ("+x", "+X", "Left to right"),
            ("+y", "+Y", "Down to up"),
            ("+z", "+Z", "Near to far"),
            ("-x", "-X", "Right to left"),
            ("-y", "-Y", "Top to bottom"),
            ("-z", "-Z", "Far to near"),
        ],
        name="Axis",
        description="How to place new keycaps relative to the original"
    )
    keysets: CollectionProperty(type=KeySet)
    selected_keyset: IntProperty()

    def draw_common_layout(self, context, layout):
        layout = self.layout
        layout.prop(self, "gap")
        axis_row = layout.row()
        axis_row.prop(self, "axis", expand=True)

    def draw_keyset_picker(self, context, layout):
        context.layout.template_list("CUSTOM_UL_keyset", "keysets", self, "keysets", self, "selected_keyset")

    def keyset_picker(self) -> KiroKeyset:
        self.keysets.clear()
        keysets_by_image = kiro.keysets_by_image(include_alternates=False)
        keysets_by_index: list[KiroKeyset] = []
        for (image_name, image_keysets) in sorted(keysets_by_image.items(), key=(lambda item: item[0])):
            for ks in sorted(image_keysets, key=(lambda item: item.name)):
                ui_list_item = self.keysets.add()
                ui_list_item.name = ks.name
                ui_list_item.image = image_name
                keysets_by_index.append(ks)
        return keysets_by_index[self.selected_keyset]


def fill_layout_enum(self, context):
    enum = [
        ("_", "(From keycaps)", "The sequence in the keyset")
    ]
    for name in kiro.get_layout_names():
        enum.append((name, name, f"The built-in \"{name}\" layout"))
    return enum


class ArrayKeys(ArrayKeysBase):
    """Put a description of what the operator does here"""
    bl_idname = "object.array_keycaps"
    bl_label = "Kiro: Array Keycaps"
    bl_options = {'REGISTER', 'UNDO'}

    length: IntProperty(name="String Length")
    layout_name: EnumProperty(name="Layout", items=fill_layout_enum)

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "layout_name")
        layout.prop(self, "length")
        self.draw_common_layout(context, layout)
        layout.template_list("CUSTOM_UL_keyset", "keysets", self, "keysets", self, "selected_keyset")

    def execute(self, context):
        original = context.selected_objects[0]
        selected_keyset = self.keyset_picker()
        start_key = original["keycap"] if original["keycap"] else 0

        if self.layout_name == "_":
            indices = range(start_key, start_key + self.length, -1 if self.length < 0 else 1)
        else:
            indices = kiro.layout_sequence(
                start_key,
                self.length,
                keyset=selected_keyset,
                layout_name=self.layout_name
            )

        objects = typeset.extend_from_original(
            original,
            indices,
            target=context.collection,
            gap=self.gap,
            direction=self.axis
        )

        return {'FINISHED'}


class StringKeys(ArrayKeysBase):
    """Put a description of what the operator does here"""
    bl_idname = "object.string_keycaps"
    bl_label = "Kiro: Array Keycaps from String"
    bl_options = {'REGISTER', 'UNDO'}

    string: StringProperty(name="String", options={'TEXTEDIT_UPDATE'})
    space_as_gap: BoolProperty(name="Non-bracketed spaces leave a gap",
                                         description="Space characters that are not in square brackets will leave gaps instead of a key")
    space_gap_adjust: FloatProperty(name="Space Adjust", description="Add or remove space from Space character gaps")

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "gap")
        layout.prop(self, "string")

        axis_row = layout.row()
        axis_row.prop(self, "axis", expand=True)

        layout.prop(self, "space_as_gap")
        if self.space_as_gap:
            layout.prop(self, "space_gap_adjust")
        layout.template_list("CUSTOM_UL_keyset", "keysets", self, "keysets", self, "selected_keyset")

    def execute(self, context):
        original = context.selected_objects[0]
        selected_keyset = self.keyset_picker()
        indices = kiro.string_to_indices(self.string, selected_keyset, space_to_none=self.space_as_gap)
        objects = typeset.extend_from_original(
            original,
            indices,
            target=context.collection,
            gap=self.gap,
            space_gap=self.space_gap_adjust,
            direction=self.axis
        )

        return {'FINISHED'}


REGISTER_CLASSES = [KeySet, KeySetUIList, ArrayKeys, StringKeys]

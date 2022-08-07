import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel
from mathutils import Vector
from ..lib import kiro
from ..lib import typeset

if "_LOADED" in locals():
    import importlib

    for mod in (kiro,typeset):  # list all imports here
        importlib.reload(mod)
_LOADED = True


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


class ArrayKeys(Operator):
    """Put a description of what the operator does here"""
    bl_idname = "object.array_keycaps"
    bl_label = "Kiro: Array Keycaps"
    bl_options = {'REGISTER', 'UNDO'}

    length: IntProperty(name="String Length")
    gap: FloatProperty(name="Gap")

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) == 1

    def execute(self, context):
        original = context.selected_objects[0]
        start_key = original["keycap"] if original["keycap"] else 0
        for idx in range(self.length - 1):
            target_collection = context.collection
            new_copy = original.copy()
            new_copy.location += Vector(((new_copy.dimensions.x + self.gap) * (idx + 1), 0, 0))
            target_collection.objects.link(new_copy)
            # Need to deselect, or the poll fails because more than one object is selected
            new_copy.select_set(False)

            # TODO: Actually look up the order
            new_copy['keycap'] = start_key + idx + 1

        return {'FINISHED'}


class StringKeys(Operator):
    """Put a description of what the operator does here"""
    bl_idname = "object.string_keycaps"
    bl_label = "Kiro: Array Keycaps from String"
    bl_options = {'REGISTER', 'UNDO'}

    gap: FloatProperty(name="Gap")
    string: StringProperty(name="String", options={'TEXTEDIT_UPDATE'})
    space_as_gap: BoolProperty(name="Non-bracketed spaces leave a gap",
                                         description="Space characters that are not in square brackets will leave gaps instead of a key")
    space_gap_adjust: FloatProperty(name="Space Adjust", description="Add or remove space from Space character gaps")
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
        # , item_dyntip_propname='', rows=5, maxrows=5, type='DEFAULT', columns=9, sort_reverse=False, sort_lock=False)

    def execute(self, context):
        original = context.selected_objects[0]
        self.keysets.clear()
        keysets_by_image = kiro.keysets_by_image()
        keysets_by_index = []
        for (image_name, image_keysets) in sorted(keysets_by_image.items(), key=(lambda item: item[0])):
            for ks in sorted(image_keysets, key=(lambda item: item.name)):
                ui_list_item = self.keysets.add()
                ui_list_item.name = ks.name
                ui_list_item.image = image_name
                keysets_by_index.append(ks)

        selected_keyset = keysets_by_index[self.selected_keyset]
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

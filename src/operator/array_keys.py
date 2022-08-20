import bpy
from typing import Set
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator
from ..lib import kiro
from ..lib import typeset
from ..lib import types
from ..lib import util

if "_LOADED" in locals():
    import importlib

    for mod in (kiro, typeset, types, util,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

KiroKeyset = types.KiroKeyset

_ALL_INVALID_ERROR = "Kiro image metadata was either missing or invalid. See View > Kiro Report for details."


class KeySetPropertyGroup(PropertyGroup):
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
    is_in_material: BoolProperty(
        name="IsInMaterial",
        description="Is the keyset referenced in any Material nodes on the object"
    )


class KeySetUIList(UIList):
    """List to display key sets"""
    bl_label = "Key Sets"
    bl_idname = "CUSTOM_UL_keyset"

    def filter_items(self, context, data, propname):
        keysets = getattr(data, propname)
        resorted = sorted(
            [{"was": idx, "ks": ks} for idx, ks in enumerate(keysets)],
            key=lambda ks: "|".join(["a" if ks["ks"]["is_in_material"] else "b", ks["ks"]["image"], ks["ks"]["name"]])
        )
        return [], [rs["was"] for rs in resorted]

    def draw_item(self, context, layout, data, item, iocon, active_data, active_propname, index) -> None:
        layout.label(text=item.name, icon=("SHADING_TEXTURE" if item.is_in_material else "NONE"))
        layout.label(text=item.image)


class ArrayKeysBase(Operator):
    gap: FloatProperty(name="Gap", default=0)
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
    make_wire: BoolProperty(name="Make Guide Wire",
                            description="Make a \"Guide Wire\" object and parent instances to it")
    keysets: CollectionProperty(type=KeySetPropertyGroup)
    selected_keyset: IntProperty(default=0)
    warn_about_keyset: BoolProperty(default=False)

    @classmethod
    def poll(cls, context) -> bool:
        if len(context.selected_objects) != 1:
            cls.poll_message_set("Select one (and only one) keycap object")
            return False
        if not kiro.kiro_images():
            cls.poll_message_set("You do not have any Kiro-enabled images in the current file")
            return False
        return True

    def draw_common_layout(self, context, layout) -> None:
        layout = self.layout
        layout.prop(self, "gap")
        axis_row = layout.row()
        axis_row.prop(self, "axis", expand=True)
        layout.prop(self, "make_wire")

    def draw_keyset_picker(self, context, layout) -> None:
        context.layout.template_list("CUSTOM_UL_keyset", "keysets", self, "keysets", self, "selected_keyset")

    def keyset_picker(self, context) -> KiroKeyset | None:
        self.keysets.clear()
        keysets_presumably_in_use = kiro.keysets_in_use(context.selected_objects[0])
        keysets = []
        for (image_name, image_keysets) in kiro.keysets_by_image(include_alternates=False).items():
            for ks in image_keysets:
                ui_list_item = self.keysets.add()
                ui_list_item.name = ks.name
                ui_list_item.image = image_name
                ui_list_item.is_in_material = ks.name in keysets_presumably_in_use

                keysets.append(ks)

        if self.selected_keyset >= len(keysets):
            return None

        return keysets[self.selected_keyset if self.selected_keyset else 0]


def fill_layout_enum(self, context) -> list[tuple[str, str, str]]:
    enum = [
        ("_", "(From keycaps)", "The sequence in the keyset"),
    ]
    for name in kiro.get_layout_names():
        enum.append((name, name, f"The built-in \"{name}\" layout"))
    return enum


class ArrayKeys(ArrayKeysBase):
    """Make an array (sequence) of keycaps in a row"""
    bl_idname = "object.array_keycaps"
    bl_label = "Clone Keycap to Sequence"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "length"

    start_index: IntProperty(name="Starting Key", default=0)
    start_string: StringProperty(name="Starting Key", default="", options={'TEXTEDIT_UPDATE'})
    start_type: EnumProperty(name="Start", items=[
        ("existing", "Existing", "Use the key already assigned", "OBJECT_DATA", 0),
        ("index", "By Index", "Specify by numeric index", "ARROW_LEFTRIGHT", 1),
        ("string", "By Keycap", "Specify by letter or keycap", "EVENT_A", 2),
    ], default="existing")
    length: IntProperty(name="String Length", default=1)
    layout_name: EnumProperty(name="Layout", items=fill_layout_enum)
    start_token_valid: BoolProperty(default=False)

    def draw(self, context) -> None:
        layout = self.layout

        layout.prop(self, "layout_name")

        start_type_split = layout.split(factor=0.25)
        start_type_split.label(text="Start at:")

        start_type_row = start_type_split.row()

        start_type_row.prop(self, "start_type", expand=True, icon_only=True)
        if self.start_type == "existing":
            start_type_row.label(text="(from object)")
        elif self.start_type == "index":
            start_type_row.prop(self, "start_index", text="")
        elif self.start_type == "string":
            start_type_row.prop(self, "start_string", text="")
            start_type_row.label(icon="CHECKMARK" if self.start_token_valid else "X")

        layout.prop(self, "length")
        self.draw_common_layout(context, layout)
        layout.template_list("CUSTOM_UL_keyset", "keysets", self, "keysets", self, "selected_keyset")

    def invoke(self, context, event):
        util.reset_operator_defaults(self, ("length", "start_type", "start_index", "start_string"))
        return self.execute(context)

    def execute(self, context) -> Set[str]:
        original = context.selected_objects[0]
        selected_keyset = self.keyset_picker(context)

        if selected_keyset is None:
            self.report({"ERROR"}, _ALL_INVALID_ERROR)
            return {'CANCELLED'}

        if self.start_type == "index":
            start_index = self.start_index
            start_token = kiro.index_to_token(start_index, selected_keyset)
            self.start_string = start_token if start_token else ""
        elif self.start_type == "string":
            def get_start_index():
                s_token = kiro.string_to_tokens(self.start_string, False)

                # If more/less than one found, try taking the entire string as one [bracketed] token
                if len(s_token) != 1:
                    alt_token = kiro.string_to_tokens(f"[{self.start_string}]", False)
                    if len(alt_token) == 1:
                        s_token = alt_token

                if len(s_token) == 0:
                    self.start_token_valid = False
                    return 0
                s_indices = kiro.tokens_to_indices(kiro.normalize_tokens(s_token[0:1], selected_keyset), selected_keyset)
                if len(s_indices) == 0:
                    return 0
                self.start_token_valid = True
                return s_indices[0]

            start_index = get_start_index()
            self.start_index = start_index
        else:
            start_index = original["keycap"] if "keycap" in original else 0
            self.start_index = start_index
            start_token = kiro.index_to_token(start_index, selected_keyset)
            self.start_string = start_token if start_token else ""

        if self.layout_name == "_":
            indices = range(start_index, start_index + self.length, -1 if self.length < 0 else 1)
        else:
            indices = kiro.layout_sequence(
                start_index,
                self.length if self.length else 1,
                keyset=selected_keyset,
                layout_name=self.layout_name
            )
        normalized_tokens = [kiro.index_to_token(i, selected_keyset) for i in indices]

        objects = typeset.extend_from_original(
            original,
            indices,
            target=util.get_collection_of_object(original),
            gap=self.gap,
            direction=self.axis,
            guide_wire=self.make_wire,
            normalized_tokens=normalized_tokens,
        )

        return {'FINISHED'}


class StringKeys(ArrayKeysBase):
    """Enter text and create a string of keycaps"""
    bl_idname = "object.string_keycaps"
    bl_label = "Clone Keycap from Text"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "string"

    string: StringProperty(name="String", options={'TEXTEDIT_UPDATE'}, default="")
    space_as_gap: BoolProperty(name="Non-bracketed spaces leave a gap",
                               description="Space characters that are not in square brackets will leave gaps instead of a key",
                               default=False)
    space_gap_adjust: FloatProperty(name="Space Adjust",
                                    description="Add or remove space from Space character gaps",
                                    default=0.0)

    def invoke(self, context, event):
        util.reset_operator_defaults(self, ("string",))
        return self.execute(context)

    def draw(self, context) -> None:
        layout = self.layout

        self.draw_common_layout(context, layout)

        layout.prop(self, "string")
        layout.prop(self, "space_as_gap")
        if self.space_as_gap:
            layout.prop(self, "space_gap_adjust")

        if self.warn_about_keyset:
            errbox = layout.box()
            errbox.alert = True
            errbox.label(text="Wrong keyset? Check below...", icon="QUESTION")
        layout.template_list("CUSTOM_UL_keyset", "keysets", self, "keysets", self, "selected_keyset")

    def execute(self, context) -> Set[str]:
        original = context.selected_objects[0]
        selected_keyset = self.keyset_picker(context)

        if selected_keyset is None:
            self.report({"ERROR"}, _ALL_INVALID_ERROR)
            return {'CANCELLED'}

        self.warn_about_keyset = kiro.detect_wrong_keyset(self.string, selected_keyset)
        tokens = kiro.string_to_tokens(self.string, self.space_as_gap)
        normalized_tokens = kiro.normalize_tokens(tokens, selected_keyset)
        indices = kiro.tokens_to_indices(normalized_tokens, selected_keyset)

        objects = typeset.extend_from_original(
            original,
            indices,
            target=util.get_collection_of_object(original),
            gap=self.gap,
            space_gap=self.space_gap_adjust,
            direction=self.axis,
            guide_wire=self.make_wire,
            normalized_tokens=normalized_tokens
        )
        return {'FINISHED'}


REGISTER_CLASSES = [KeySetPropertyGroup, KeySetUIList, ArrayKeys, StringKeys]

import bpy
import re
from mathutils import Vector
from typing import Iterable


def _make_guide_wire(name: str, points: list[Vector], target: bpy.types.Collection) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [(n, n + 1) for n in range(len(points) - 1)], [])
    object = bpy.data.objects.new(name, mesh)
    target.objects.link(object)
    return object


def extend_from_original(
        original: bpy.types.Object,
        indices: list[int],
        target: bpy.types.Collection,
        gap: int = 0,
        space_gap: int = 0,
        direction: str = "+x",
        guide_wire: bool = False,
        normalized_tokens: list[str] | None = None,
) -> list[bpy.types.Object]:
    if not indices:
        return [original]

    try:
        offset_direction = Vector({
                                      "x": (-1 if direction[0] == "-" else 1, 0, 0),
                                      "y": (0, -1 if direction[0] == "-" else 1, 0),
                                      "z": (0, 0, -1 if direction[0] == "-" else 1)
                                  }[direction[1].lower()])
    except IndexError:
        offset_direction = Vector((1, 0, 0))
        print("Invalid direction argument passed to extend_from_original. Assuming \"+x\".", direction)

    # Precompute offsets so they can be used by both placement and wire-creation
    current_offset = Vector((0, 0, 0))
    offsets = [current_offset]
    offset_vector = (original.dimensions + Vector((gap,) * 3)) * offset_direction
    space_offset_vector = offset_vector + (Vector((space_gap,) * 3) * offset_direction)
    for keycap in indices[1:]:
        current_offset = current_offset + (offset_vector if keycap else space_offset_vector)
        offsets.append(current_offset)

    name_base = re.sub(r'\.\d+', '', original.name)
    can_rename = len(normalized_tokens if normalized_tokens else []) == len(indices)

    if guide_wire:
        wire = _make_guide_wire("KeycapWire", offsets, target)
        wire.location = original.location.copy()
    else:
        wire = None

    for index, keycap in enumerate(indices):
        if keycap is None:
            continue

        if index == 0:
            new_copy = original
        else:
            new_copy = original.copy()
            new_copy.location = original.location + offsets[index]
            if can_rename:
                token_name = normalized_tokens[index] if normalized_tokens[index] is not None else f"idx:{keycap}"
                new_copy.name = f"{name_base} ({token_name})"

            target.objects.link(new_copy)
            # Need to deselect all but the original, or the poll fails because more than one object is selected
            new_copy.select_set(False)

        new_copy['keycap'] = keycap

        if wire:
            new_copy.parent = wire
            new_copy.parent_type = "VERTEX"
            new_copy.location = (0, 0, 0)
            new_copy.parent_vertices[0] = index

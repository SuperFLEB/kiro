import bpy
from mathutils import Vector
from typing import Iterable


def _make_guide_wire(name: str, points: list[Vector], target: bpy.types.Collection) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [(n, n+1) for n in range(len(points) - 1)], [])
    object = bpy.data.objects.new(name, mesh)
    target.objects.link(object)
    return object


def extend_from_original(
        original: bpy.types.Object,
        indices: Iterable[int],
        target: bpy.types.Collection,
        gap: int = 0,
        space_gap: int = 0,
        direction: str = "+x",
        guide_wire: bool = False,
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

    offset_vector = (original.dimensions + Vector((gap,) * 3)) * offset_direction
    space_offset_vector = offset_vector + (Vector((space_gap,) * 3) * offset_direction)

    # No need to make a clone for the original
    original["keycap"] = indices[0]

    # Make clones for any additional keycaps
    current_offset = Vector((0, 0, 0))
    offsets = [current_offset]

    # Precompute offsets so they can be used by both placement and wire-creation
    for keycap in indices[1:]:
        current_offset = current_offset + (offset_vector if keycap else space_offset_vector)
        if keycap is not None:
            offsets.append(current_offset)

    objects = [original]

    non_space_indices = [i for i in indices if i is not None]

    for index, keycap in enumerate(non_space_indices[1::]):
        if keycap is not None:
            new_copy = original.copy()
            objects.append(new_copy)
            new_copy.location = original.location + offsets[index + 1]
            target.objects.link(new_copy)

            # Need to deselect, or the poll fails because more than one object is selected
            new_copy.select_set(False)
            new_copy['keycap'] = keycap

    if guide_wire:
        # TODO: Properly name this
        wire = _make_guide_wire("KeycapWire", offsets, target)
        wire.location = objects[0].location
        for index, object in enumerate(objects):
            object.parent = wire
            object.parent_type = "VERTEX"
            object.location = (0,0,0)
            object.parent_vertices[0] = index



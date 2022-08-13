import bpy
from mathutils import Vector
from typing import Iterable


def extend_from_original(
        original: bpy.types.Object,
        indices: Iterable[int],
        target: bpy.types.Collection,
        gap: int = 0,
        space_gap: int = 0,
        direction: str = "+x"
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
    # TODO: support different orientations, maybe even multiline
    offset = Vector((0, 0, 0))
    for token_index, keycap_index in enumerate(indices[1::]):
        if keycap_index is None:
            # None indicates a "space" should be inserted
            offset += space_offset_vector
            continue

        # TODO: support different orientations, maybe even multiline
        offset += offset_vector

        new_copy = original.copy()
        new_copy.location = original.location + offset
        target.objects.link(new_copy)

        # Need to deselect, or the poll fails because more than one object is selected
        new_copy.select_set(False)
        new_copy['keycap'] = keycap_index

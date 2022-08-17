import bpy
import re


def flatten(list_of_lists: list[list[any]]) -> list[any]:
    return [item for sublist in list_of_lists for item in sublist]


def wordwrap(string: str, length: int) -> list[str]:
    words = [word for word in re.split(' +', string) if word]
    if not words: return []
    lines = [f"{words[0]} "]
    if len(words) > 1:
        for word in words[1:]:
            if len(lines[-1]) + len(word) > length:
                lines.append(f"{word} ")
                continue
            lines[-1] += f"{word} "
    lines = [line[:-1] for line in lines]
    return lines


def get_collection_of_object(obj: bpy.types.Object, default_to_context: bool = True) -> bpy.types.Collection | None:
    """Get the enclosing collection of an Object (caveat: if the object is not in the active scene, this may break)"""

    # If there's only one, return that...
    candidates = [c for c in obj.users_collection]

    if len(candidates) == 0:
        return bpy.context.scene.collection if default_to_context else None

    if len(candidates) == 1:
        return candidates[0]

    # If there are more than one, but one isn't in the current Scene
    # (e.g., it's a RigidBodyWorld), return the first that isn't...
    scene_collections = [bpy.context.scene.collection] + list(bpy.context.scene.collection.children_recursive)
    candidates = [c for c in candidates if c in scene_collections]
    if len(candidates) > 0:
        return candidates[0]

    # Return the first collection from anywhere
    return obj.users_collection[0]

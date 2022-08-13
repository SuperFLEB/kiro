import bpy


class KiroImageInfo:
    name: str
    name_full: str
    json_path: str

    def __init__(self, name: str = "", name_full: str = "", json_path: str = ""):
        self.name = name
        self.name_full = name_full
        self.json_path = json_path



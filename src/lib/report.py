import bpy
from datetime import datetime
from . import metadata
from . import kiro
from . import types
from . import bootstrap

if "_LOADED" in locals():
    import importlib

    for mod in (metadata, kiro, types):  # list all imports here
        importlib.reload(mod)
_LOADED = True


class ImageReporter():
    is_valid_json: bool
    validation_error: str | None
    kiro_meta: types.KiroImageMeta | None
    kiro_data: types.KiroMetaData

    def __init__(self, full_name: str):
        self.kiro_meta = kiro.kiro_image_meta(bpy.data.images[full_name])
        if self.kiro_meta.json_path:
            try:
                kiro_data = metadata.load(self.kiro_meta.json_path)
                self.is_valid_json = True
                self.validation_error = None
            except metadata.KiroValidationException as e:
                self.is_valid_json = False
                self.validation_error = e.msg
        else:
            self.is_valid_json = True
            self.validation_error = None


def _nstr(val: str | None):
    return "" if val is None else val


def generate():
    reports = [ImageReporter(i) for i in bpy.data.images.keys()]
    has_jsonschema = bootstrap.has_module("jsonschema")

    name_pad = max([len(_nstr(r.kiro_meta.name_full)) for r in reports] + [len("Image ID")])
    path_pad = max([len(_nstr(r.kiro_meta.image_path)) for r in reports] + [len("Image Path")])

    has_json_str = ["No", "YES"]
    has_json_pad = max([len(s) for s in has_json_str] + [len("Has Kiro JSON?")])

    json_valid_str = ["INVALID JSON", "ok", "n/a"]
    json_valid_pad = max([len(s) for s in json_valid_str] + [len("Is JSON Valid?")])

    width = name_pad + path_pad + has_json_pad + json_valid_pad + 10

    output = ["Kiro Image report generated " + datetime.now().strftime("%c")]

    if not has_jsonschema:
        output.append("")
        output.append("NOTICE:")
        output.append("The jsonschema Python package is not installed, so Kiro JSON files cannot be checked for validity.")
        output.append("The package can be installed using the button in the Preferences panel for this addon.")

    output += [
        "",
        "=" * width,
        " | ".join(
            [
                "Image ID".ljust(name_pad),
                "Has Kiro JSON?".ljust(has_json_pad),
                "Is JSON Valid?".ljust(json_valid_pad),
                "Image Path".ljust(path_pad)
            ]
        ),
        "=" * width
    ]


    for r in reports:
        cols = [r.kiro_meta.name_full.ljust(name_pad)]
        if r.kiro_meta.json_path:
            cols.append(has_json_str[1].ljust(has_json_pad))
            if has_jsonschema:
                cols.append((json_valid_str[1] if r.is_valid_json else json_valid_str[0]).ljust(json_valid_pad))
            else:
                cols.append(json_valid_str[2].ljust(json_valid_pad))
        else:
            cols.append(has_json_str[0].ljust(has_json_pad))
            cols.append(json_valid_str[2].ljust(json_valid_pad))
        cols.append((r.kiro_meta.image_path if r.kiro_meta.image_path else "").ljust(path_pad))

        line = " | ".join(cols)

        if not r.is_valid_json:
            line += "\n" + ("-" * width) + "\n"
            line += r.validation_error
        elif r.kiro_meta.json_path and not has_jsonschema:
            line += "\n" + ("-" * width) + "\n"
            line += "There is a .kiro.json file, but it cannot be validated because the jsonschema package is not installed."

        line += "\n" + ("=" * width)

        output.append(line)

    return "\n".join(output)

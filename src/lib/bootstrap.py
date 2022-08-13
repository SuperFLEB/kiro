from typing import Iterable
import subprocess
import sys
from importlib import util as il_util

WANTED_MODULES = ["jsonschema"]


def _check_modules(installed: False) -> list[str]:
    result = []
    for mod_name in WANTED_MODULES:
        if has_module(mod_name) == installed:
            result.append(mod_name)
    return result


def has_module(mod_name: str) -> bool:
    return bool(il_util.find_spec(mod_name))


def missing_modules() -> list[str]:
    return _check_modules(False)


def installed_modules() -> list[str]:
    return _check_modules(True)


def install_missing_modules() -> None:
    missing = set(missing_modules())
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])


def remove_installed_modules(exceptions: Iterable = tuple()) -> None:
    installed = set(installed_modules()) - set(exceptions)
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", *installed])

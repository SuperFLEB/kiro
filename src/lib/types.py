from __future__ import annotations
from warnings import warn

class KiroMetaData:
    version: float
    name: str
    description: str
    keysets: dict[str, KiroKeyset]

    def __init__(self, version: float, name: str, description: str | None, keysets: dict[str, KiroKeyset]):
        self.description = description
        self.name = name
        self.version = version
        self.keysets = keysets
        for ks in self.keysets.values():
            ks.parent = self


class KiroKeyset:
    version: float
    name: str
    cols: int
    rows: int
    start: int
    length: int
    length_explicit: bool
    default_key: int
    alt_for: str
    parent: KiroMetaData

    @property
    def keys(self) -> list[str]:
        if not self.alt_for:
            return self._keys
        if not self.parent:
            raise Exception("Reference to KiroKeyset alt_for was performed but parent was not set")
        if not self.parent.keysets or self.alt_for not in self.parent.keysets:
            warn(RuntimeWarning(f"Kiro Keyset {self.name} is an alternative for {self.alt_for} but {self.alt_for}"
                                f" does not exist"))
            return []
        if self.parent.keysets[self.alt_for].alt_for:
            raise Exception(f"Kiro Keyset {self.name} alt_for references {self.alt_for} which itself has an alt_for."
                            f" Multiple levels of alt_for reference are not supported.")

    @keys.setter
    def keys(self, value: list[str]):
        self._keys = value

    def __init__(
            self,
            name: str,
            cols: int,
            rows: int,
            start: int,
            default_key: int = 0,
            length: int | None = None,
            keys: list[str] | None = None,
            alt_for: str | None = None,
            version: float = 1.0,
    ):
        self.name = name
        self.cols = cols
        self.rows = rows
        self.start = start
        self.keys = keys
        self.alt_for = alt_for
        self.length = length if length else len(keys)
        self.length_explicit = (length is not None)
        self.default_key = default_key
        self.version = version


class KiroImageMeta:
    name: str
    name_full: str
    image_path: str | None
    json_path: str | None

    def __init__(self, name: str = "", name_full: str = "", image_path: str | None = None, json_path: str | None = None):
        self.name = name
        self.name_full = name_full
        self.image_path = image_path
        self.json_path = json_path

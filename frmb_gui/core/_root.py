import dataclasses
import json
import logging
import shutil
from pathlib import Path

import frmb

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class FrmbRootFile:
    """
    A dataclass for the file representing the root of the Frmb hierarchy.

    The instance is immutable.
    """

    name: str
    """
    Pretty name for the root. Used in the GUI.
    """

    uuid: str
    """
    Unique identifier that allow to distinguish 2 roots, even if they have the same content.
    """

    last_installed_hash: int
    """
    An hash of the content of the hierarchy the last time it was installed in the registry.
    """

    @classmethod
    def from_file(cls, path: Path):
        """
        Retrieve an instance from a serialized file on disk.
        """
        content = json.load(path.open("r"))
        return cls(
            name=content["name"],
            uuid=content["uuid"],
            last_installed_hash=content["last_installed_hash"],
        )

    def to_file(self, path: Path):
        """
        Serialize this instance to disk.

        If the file already exists its content is overwritten.
        """
        content = {
            "name": self.name,
            "uuid": self.uuid,
            "last_installed_hash": self.last_installed_hash,
        }
        json.dump(content, path.open("w"), indent=4)


class FrmbRoot:
    """
    Represent a directory storing a hierachy of Frmb file that correspond to one or
    more context-menu that must be installed together.
    """

    def __init__(self, path: Path):
        self._path = path

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} path={self._path}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path=Path({self._path}))"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Cannot compare {other} with class {self.__class__}")
        return other.path == self._path

    @property
    def path(self) -> Path:
        """
        Filesystem path to a directory that may exist.
        """
        return self._path

    @property
    def children(self) -> list[frmb.FrmbFile]:
        """
        The Frmb files directly at root, used to parse the hierarchy.
        """
        return frmb.read_menu_hierarchy_as_file(self._path)

    def get_content_hash(self) -> int:
        """
        Get a hash of the whole hierarchy allowing to compare if 2 hierachies produce
        the same result.
        """
        return hash(tuple(self.children))


def delete_root_from_disk(root: FrmbRoot):
    """
    Remove the given root directory and its content from the filesystem.
    """
    shutil.rmtree(root.path)

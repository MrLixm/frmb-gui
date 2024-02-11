import dataclasses
import json
import logging
import os
from pathlib import Path
from typing import ClassVar

import jinja2
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui
from ._jinja import JINJA_ENV

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class UiStyle:
    """
    Python object to facilate the manipulation of Style files.

    This object manipulate the content of said files and have no knowledge of the
    original filesystem it provides from.

    Style files stores variables defining the look of an application and allow to
    quickly change the look of the application by swapping htem, without having to
    rewrite the stylesheet/section of code.
    """

    content: dict
    """
    The raw content of the style as a python dict.
    """

    name: str
    """
    Unique name of the style.

    A style can be retrieved just using its name.
    """

    _FONT_FAMILIES_LOADED: ClassVar[list[str]] = []
    """
    Keep track of the families that were loaded through all the class instances.
    """

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"

    @classmethod
    def from_path(cls, path: Path):
        """
        Args:
            path: Filesystem path to an existing json file.
        """
        content = json.load(path.open("r"))
        name = path.stem.split(".")[0]
        return cls(
            content=content,
            name=name,
        )

    def get_font_families(self) -> set[str]:
        """
        Get the name of all the font families used in the style. No duplicates.
        """
        families = self.content["text"]["family"].values()
        return set(families)

    def get_icon_path(self, name: str) -> Path:
        """
        Absolute filesystem path to the icon file with the given name.
        """
        icon = self.content["icon"][name]
        return frmb_gui.resources.get_icon_path(icon)

    def get_icon(self, name: str) -> QtGui.QIcon:
        """
        QIcon instance for the icon with the given name.
        """
        return QtGui.QIcon(str(self.get_icon_path(name)))

    def load_font_family(self, family_name: str) -> list[int]:
        """
        Register the given font family stored on disk to be accesible in the Qt application.

        Args:
            family_name: name of the famliy as named on disk

        Returns:
            ids of the font loaded
        """
        LOGGER.debug(f"loading font family {family_name} ...")

        if family_name in self._FONT_FAMILIES_LOADED:
            LOGGER.warning(f"font family {family_name} already loaded")
            return []

        family_path = frmb_gui.resources.get_font_family_path(family_name)
        font_ids = []

        # TODO font family may be builtin so need to look for it before raising
        if not family_path.exists():
            raise FileNotFoundError(
                f"Given family name <{family_name}> was not found on disk."
            )

        for file_name in os.scandir(family_path):
            file_path = family_path / file_name

            if file_path.suffix not in [".ttf", ".otf"]:
                continue

            font_id = QtGui.QFontDatabase.addApplicationFont(str(file_path))

            if font_id == -1:
                LOGGER.warning(f"cannot load font {file_path}")
                continue

            font_ids.append(font_id)

        if font_ids:
            self._FONT_FAMILIES_LOADED.append(family_name)

        LOGGER.debug(
            f"loaded font family {[QtGui.QFontDatabase.applicationFontFamilies(fid) for fid in font_ids]}"
        )
        return font_ids

    def load_font_families(self) -> dict[str, list[int]]:
        """
        Ensure all the families defined in this style are loaded for use.

        Returns:
            dict of {"font families name": "list of font ids"}
        """
        # TODO doesn't work to refactor
        loaded: dict[str, list[int]] = {}
        for family_name in self.get_font_families():
            loaded[family_name] = self.load_font_family(family_name)
        return loaded

    def resolve_stylesheet(self, stylesheet: str) -> str:
        """
        Produce a valid stylesheet with all variables resolved.

        The stylesheet is the template that need replacing, and this style provide the data
        used to replace variables in the template.

        Args:
            stylesheet: document with potential jinja2 variables
        """
        template = JINJA_ENV.from_string(stylesheet)
        content = self.content.copy()
        # resolve icon paths
        content["icon"] = {
            icon_name: frmb_gui.resources.browser.resolve_path_to_qss(
                str(frmb_gui.resources.get_icon_path(icon_value))
            )
            for icon_name, icon_value in content["icon"].items()
        }
        resolved = template.render(content)
        return resolved

    def get_stylesheet(self, name: str) -> str:
        """
        Args:
            name: file name of the stylesheet WITHOUT the file extension

        Returns:
            content of the stylesheet resolved with given style
        """
        path = frmb_gui.resources.get_stylesheet_path(name)
        content = path.read_text("utf-8")
        LOGGER.debug(f"resolving stylesheet <{name}> with style={self!s}")
        try:
            return self.resolve_stylesheet(content)
        except jinja2.exceptions.UndefinedError as error:
            raise ValueError(
                f"stylesheet template {path} did not resolved fully using "
                f"style <{self!s}>: {error}"
            )

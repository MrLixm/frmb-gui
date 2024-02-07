import json
import logging
import os
from pathlib import Path
from typing import Optional

import jinja2
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).parent

FONT_FAMILIES_LOADED: list[str] = []


def make_resource_path_absolute(relative_path: Path) -> Path:
    """
    Args:
        relative_path: relative path to turn absolute by joining the resource root
    """
    relative_path = Path(relative_path)
    if relative_path.is_absolute():
        return relative_path
    path = ROOT / relative_path
    return path.resolve()


def get_font_family_path(family_name: str) -> Path:
    """
    A font family is a directory containing multiple font files belong to the same
    family (usually different styles).

    Args:
        family_name: name of the font family as named on disk

    Returns:
        absolute directory path to a font family that might exist or not
    """
    return ROOT / "fonts" / family_name


def load_font_family(family_name: str) -> list[int]:
    """
    Register the given font family stored on disk to be accesible in the application.

    Args:
        family_name: name of the famliy as named on disk

    Returns:
        ids of the font loaded
    """
    LOGGER.debug(f"loading font family {family_name} ...")

    if family_name in FONT_FAMILIES_LOADED:
        LOGGER.warning(f"font family {family_name} already loaded")
        return []

    family_path = get_font_family_path(family_name)
    font_ids = []

    if not family_path.exists():
        raise FileNotFoundError(
            f"Given family name <{family_name}> was not found on disk."
        )

    for file_name in os.scandir(family_path):
        file_path = family_path / file_name

        if not file_path.suffix in [".ttf", ".otf"]:
            continue

        font_id = QtGui.QFontDatabase.addApplicationFont(str(file_path))

        if font_id == -1:
            LOGGER.warning(f"cannot load font {file_path}")
            continue

        font_ids.append(font_id)

    if font_ids:
        FONT_FAMILIES_LOADED.append(family_name)

    LOGGER.debug(
        f"loaded font family {[QtGui.QFontDatabase.applicationFontFamilies(fid) for fid in font_ids]}"
    )
    return font_ids


def get_icon_path(name: str) -> Path:
    """
    Args:
        name: full name of the logo with the file extension

    Returns:
        absolute file path to an icon that might exist or not
    """
    return ROOT / "icons" / name


def get_icon(name: str) -> QtGui.QIcon:
    """
    Args:
        name: full name of the logo with the file extension

    Returns:
        QIcon instance for the asked icon.
    """
    path = get_icon_path(name)
    return QtGui.QIcon(str(path))


def get_stylesheet_path(name: str) -> Path:
    """
    Args:
        name: file name of the stylesheet WITHOUT the file extension

    Returns:
        absolute file path to a stylesheet that might exist or not
    """
    return ROOT / "stylesheets" / f"{name}.css.jinja2"


def get_stylesheet(name: str, style_name: Optional[str] = None) -> str:
    """
    Args:
        name: file name of the stylesheet WITHOUT the file extension
        style_name:
            file name of the style WITHOUT the file extension. Used to resolve the stylesheet.

    Returns:
        content of the stylesheet resolved with given style
    """
    path = get_stylesheet_path(name)
    content = path.read_text("utf-8")

    style = {}
    if style_name:
        style = get_style(style_name)
    try:
        return resolve_stylesheet(content, style)
    except jinja2.exceptions.UndefinedError as error:
        raise ValueError(
            f"stylesheet template {path} did not resolved fully using style <{style_name}>: {error}"
        )


def get_style_path(name: str) -> Path:
    """
    Args:
        name: file name of the style WITHOUT the file extension

    Returns:
        absolute file path to a style that might exist or not
    """
    return ROOT / "styles" / f"{name}.json"


def get_style(name: str) -> dict:
    """
    Args:
        name: file name of the style WITHOUT the file extension

    Returns:
        absolute file path to a style that might exist or not
    """
    path = get_style_path(name)
    return json.load(path.open("r"))


def resolve_path_to_qss(path: str) -> str:
    """
    Ensure the given path can be used in the qss ``url()`` property.
    """
    path = make_resource_path_absolute(Path(path))
    return path.as_posix()


def _get_icon_path_jinja(name: str) -> Path:
    path = get_icon_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Can't find file name {name} at {path}")
    return path


JINJA_ENV = jinja2.Environment(undefined=jinja2.StrictUndefined)
JINJA_ENV.globals["get_icon_path"] = _get_icon_path_jinja
JINJA_ENV.filters["topath"] = resolve_path_to_qss


def resolve_stylesheet(stylesheet: str, style: dict) -> str:
    """
    Produce a valid stylesheet with all variables replaced.

    The stylesheet is teh template that need replacing, and the style provide the data
    used to replace variables in the template.

    Args:
        stylesheet: document with potential jinja2 variables
        style: variables to use as key/value pair
    """
    LOGGER.debug(f"resolving stylesheet with style={'{...}' if style else style}")
    template = JINJA_ENV.from_string(stylesheet)
    resolved = template.render(style)
    return resolved

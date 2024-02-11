"""
Low-level module to handle path resolving of application resources.

The actual i-o is mostly performed by the style.
"""

import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).parent
"""
Root directory containing all the resources files.

Filesystem path to an existing directory.
"""


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


def get_icon_path(name: str) -> Path:
    """
    Args:
        name: full name of the logo with the file extension

    Returns:
        absolute file path to an icon that might exist or not
    """
    return ROOT / "icons" / name


def get_stylesheet_path(name: str) -> Path:
    """
    Args:
        name: file name of the stylesheet WITHOUT the file extension

    Returns:
        absolute file path to a stylesheet that might exist or not
    """
    return ROOT / "stylesheets" / f"{name}.css.jinja2"


def get_style_path(name: str) -> Path:
    """
    Args:
        name: file name of the style WITHOUT the file extension

    Returns:
        absolute file path to a style that might exist or not
    """
    return ROOT / "styles" / f"{name}.json"


def resolve_path_to_qss(path: str) -> str:
    """
    Ensure the given path can be used in the qss ``url()`` property.
    """
    path = make_resource_path_absolute(Path(path))
    return path.as_posix()

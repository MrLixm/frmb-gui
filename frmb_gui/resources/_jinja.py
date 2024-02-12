"""
Define the Jinja environment used to resolve the stylesheet.
"""

import logging
from pathlib import Path

import jinja2

from . import browser

__all__ = [
    "JINJA_ENV",
]

LOGGER = logging.getLogger(__name__)


def _get_icon_path_jinja(name: str) -> Path:
    path = browser.get_icon_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Can't find file name {name} at {path}")
    return path


def _with_alpha(color: str, alpha: float = 1.0) -> str:
    if not color.startswith("rgb"):
        LOGGER.warning(
            f"[withalpha] tried to set alpha on uncompatible color <{color}>"
        )
        return color

    _alpha = alpha * 255
    if color.startswith("rgba"):
        new_color = color.rsplit(",", 1)[0]
    else:
        new_color = color.rstrip(")")
    new_color += f", {_alpha})"
    new_color = new_color.replace("rgb(", "rgba(")
    return new_color


JINJA_ENV = jinja2.Environment(undefined=jinja2.StrictUndefined)
JINJA_ENV.globals["get_icon_path"] = _get_icon_path_jinja
JINJA_ENV.filters["topath"] = browser.resolve_path_to_qss
JINJA_ENV.filters["withalpha"] = _with_alpha

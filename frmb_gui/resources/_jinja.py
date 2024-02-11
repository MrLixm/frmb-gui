"""
Define the Jinja environment used to resolve the stylesheet.
"""

from pathlib import Path

import jinja2

from . import browser

__all__ = [
    "JINJA_ENV",
]


def _get_icon_path_jinja(name: str) -> Path:
    path = browser.get_icon_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Can't find file name {name} at {path}")
    return path


JINJA_ENV = jinja2.Environment(undefined=jinja2.StrictUndefined)
JINJA_ENV.globals["get_icon_path"] = _get_icon_path_jinja
JINJA_ENV.filters["topath"] = browser.resolve_path_to_qss

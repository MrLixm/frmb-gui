"""
Retrieve the current operating system the code is being executed from.
"""

import sys
from typing import Literal

import frmb_gui

_SOURCE = frmb_gui.env.platform_fake.get() or sys.platform


def get_name(self) -> Literal["linux", "mac", "windows"]:
    if self.is_linux:
        return "linux"
    elif self.is_mac:
        return "mac"
    elif self.is_windows:
        return "windows"
    else:
        raise OSError("Unsupported plateform {}".format(sys.platform))


def is_linux() -> bool:
    return _SOURCE.startswith("linux")


def is_mac() -> bool:
    return _SOURCE.startswith("darwin")


def is_windows() -> bool:
    return _SOURCE in ("win32", "cygwin")

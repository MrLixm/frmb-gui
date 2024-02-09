"""
Configuration module.

Variables can be modified at runtime.
"""

import logging
import os
import sys
from pathlib import Path

from . import env
from . import osplatform
from .cli import CLI

LOGGER = logging.getLogger(__name__)


# using a class to benefit from properties
class _Config:

    def __init__(self):
        self._debug = None

    @property
    def debug(self) -> bool:
        """
        True to switch to debug mode. This usually display/log additional informations and
        disable some problematic features.
        """
        if self._debug is None:
            self._debug = CLI().debug
            self._debug = (
                self._debug
                if self._debug is not None
                else bool(int(env.debug.get(False)))
            )

        return self._debug

    @property
    def developer_mode(self) -> bool:
        """
        True to switch to developer mode.
        This enable features and tools making the development faster.
        """

        if "--devmode" in sys.argv:
            return True

        if int(env.developer_mode.get(0)):
            return True

        return False

    @property
    def user_data_dir(self) -> Path:
        """
        A filesystem path to an existing local directory where we can store application preferences.
        """
        if osplatform.is_windows():
            user_dir = Path(os.environ["LOCALAPPDATA"])
        elif osplatform.is_mac():
            user_dir = Path("~") / "Library" / "Application Support"
        else:
            user_dir = Path("~")

        user_dir = user_dir.expanduser()

        pyco_dir = user_dir / ".pyco"
        if not pyco_dir.exists():
            LOGGER.info(f"creating {pyco_dir}")
            pyco_dir.mkdir()

        frmb_dir = pyco_dir / "frmb-gui"
        if not frmb_dir.exists():
            LOGGER.info(f"creating {frmb_dir}")
            frmb_dir.mkdir()

        return frmb_dir

    # styled like a magic method because it is intended to be public, but we maybe want
    # a config variable named "debugging".
    def __debugging__(self):
        # log the config values for debugging
        LOGGER.debug(f"{self.debug=}, {self.developer_mode=}, {self.user_data_dir=}")


# singleton
config = _Config()

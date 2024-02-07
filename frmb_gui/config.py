"""
Configuration module.

Variables can be modified at runtime.
"""

import logging
import sys

from . import env
from .cli import CLI

LOGGER = logging.getLogger(__name__)


def _debug() -> bool:
    if CLI().debug:
        return True

    if int(env.debug.get(0)):
        return True

    return False


debug: bool = _debug()
"""
True to switch to debug mode. This usually display/log additional informations and 
disable some problematic features.
"""


def _developer_mode() -> bool:
    if "--devmode" in sys.argv:
        return True

    if int(env.developer_mode.get(0)):
        return True

    return False


developer_mode: bool = _developer_mode()
"""
True to switch to developer mode.
This enable features and tools making the development faster.
"""


# styled like a magic method because it is intended to be public, but we maybe want
# a config variable named "debugging".
def __debugging__():
    # log the config values for debugging
    LOGGER.debug(f"{debug=},{developer_mode=}")

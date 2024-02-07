"""
Miscelenous GUI utilities.
"""

import math

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets


def get_size_relative_to_screen(
    width_amount: float = 1.0,
    height_amount: float = 1.0,
) -> QtCore.QSize:
    """
    Generate a size based on the current screen size, scaled by the given amount.

    Args:
        width_amount: multiplier of the screen width to keep. 1==all of it.
        height_amount:  multiplier of the screen height to keep. 1==all of it.
    """
    screen_size = QtWidgets.QApplication.desktop().screenGeometry()
    size = QtCore.QSize(
        math.floor(screen_size.width() * width_amount),
        math.floor(screen_size.height() * height_amount),
    )
    return size


def center_in_screen(widget: QtWidgets.QWidget):
    """
    Move the widget until it is at the center of the screen it is displayed on.
    """
    screen_geo = QtWidgets.QApplication.primaryScreen().geometry()
    x = (screen_geo.width() - widget.width()) // 2
    y = (screen_geo.height() - widget.height()) // 2
    widget.move(x, y)

from typing import Optional

from qtpy import QtCore
from qtpy import QtWidgets
from qtpy import QtGui


class StylesheetIcon(QtWidgets.QFrame):
    """
    A QWidget intended to be styled from stylesheet using the image property::

        QWidget.StylesheetIcon[icon-name="some name"]{
            background-color: dark;
            image: url("someicon.svg");
            image-position: center;
        }
    """

    def __init__(
        self,
        icon_name: str,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self.set_icon_name(icon_name)

    def set_icon_name(self, new_name: str):
        self.setProperty("icon-name", new_name)
        # update stylesheet, SRC: https://stackoverflow.com/a/26249813/13806195
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class StylesheetIconButton(QtWidgets.QToolButton):
    """
    A QToolButton intended to get its icon set from stylesheet using the image property::

        QWidget.StylesheetIconButton[icon-name="some name"]{
            background-color: dark;
            image: url("someicon.svg");
            image-position: center;
        }
    """

    def __init__(
        self,
        icon_name: str,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self.set_icon_name(icon_name)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)

    def set_icon_name(self, new_name: str):
        self.setProperty("icon-name", new_name)
        # update stylesheet, SRC: https://stackoverflow.com/a/26249813/13806195
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

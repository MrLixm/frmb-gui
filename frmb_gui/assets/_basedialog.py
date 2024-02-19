import abc
import logging
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui

LOGGER = logging.getLogger(__name__)


class BaseDialogFrame(QtWidgets.QFrame):
    """
    The inset frame of the BaseDialog.
    """

    drop_shadow_opacity: int = 100
    drop_shadow_radius: int = 20

    def __init__(
        self,
        action_label: str,
        main_widget: QtWidgets.QWidget,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_buttons = QtWidgets.QHBoxLayout()
        self.button_action = QtWidgets.QPushButton(action_label)
        self.button_cancel = QtWidgets.QPushButton("Cancel")
        for widget in [self, self.button_action, self.button_cancel]:
            effect = QtWidgets.QGraphicsDropShadowEffect(widget)
            effect.setColor(QtGui.QColor(0, 0, 0, self.drop_shadow_opacity))
            effect.setOffset(0, 0)
            effect.setBlurRadius(self.drop_shadow_radius)
            widget.setGraphicsEffect(effect)

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(main_widget)
        self.layout_main.addStretch(1)
        self.layout_main.addLayout(self.layout_buttons)
        self.layout_buttons.addStretch(1)
        self.layout_buttons.addWidget(self.button_action)
        self.layout_buttons.addWidget(self.button_cancel)
        self.layout_buttons.addStretch(1)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_main.setSpacing(0)

        # 4. connect
        self.accepted = self.button_action.clicked
        self.canceled = self.button_cancel.clicked


class BaseDialog(QtWidgets.QDialog):
    """
    A base dialog with 2 buttons and with a slot for an internal main widget.

    Intended to be subclassed.

    Also aims at unifying styles between all dialogs.

    An example of subclassing::

        class MyDialog(BaseDialog):
            def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
                super().__init__(title="Title!", parent=parent)
                self.widget = QtWidgets.QLineEdit()
                self.set_main_widget(widget)

            def _on_accepted():
                do_something(self.widget.text())

    Which could be styled with stylesheet using::

        QFrame.BaseDialogFrame {
            margin: 20px;
            padding: 20px;
            border: 1px solid;
            border-color: rgb(80,80,80);
            border-radius: 5px;
            background-color: rgb(20,20,20);
        }

        QDialog.MyDialog QFrame.BaseDialogFrame {
            border-color: green;
        }

    """

    def __init__(
        self,
        title: str,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        # 1. Create
        self._layout_main = QtWidgets.QVBoxLayout()
        self.__widget = None

        # 2. build layout
        self.setLayout(self._layout_main)

        # 3. modify
        self.setWindowTitle(f"{frmb_gui.constants.name} - {title}")
        self._layout_main.setContentsMargins(0, 0, 0, 0)

        # 4. connect
        self.accepted.connect(self._on_accepted)
        self.rejected.connect(self._on_rejected)

    def set_main_widget(self, action_button_label: str, widget: QtWidgets.QWidget):

        if self.__widget is not None:
            raise ValueError(f"Main widget already set once with {self.__widget}.")

        self.__widget = BaseDialogFrame(
            action_label=action_button_label,
            main_widget=widget,
        )
        self._layout_main.addWidget(self.__widget)
        self.__widget.accepted.connect(self.accept)
        self.__widget.canceled.connect(self.reject)

    def _on_accepted(self):
        pass

    def _on_rejected(self):
        pass

import logging
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui

LOGGER = logging.getLogger(__name__)


class MenuRootSelectorWidget(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.main_combobox = QtWidgets.QComboBox()
        # TODO placeholder
        self.button_add = QtWidgets.QPushButton("add")
        self.button_remove = QtWidgets.QPushButton("remove")
        self.button_delete = QtWidgets.QPushButton("delete")
        self.layout_main = QtWidgets.QHBoxLayout()

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.main_combobox)
        self.layout_main.addWidget(self.button_add)
        self.layout_main.addWidget(self.button_remove)
        self.layout_main.addWidget(self.button_delete)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.main_combobox.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

        # 4. connect

import logging
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui

LOGGER = logging.getLogger(__name__)


class AppTitleWidget(QtWidgets.QFrame):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        # 1. create
        self.logo = QtWidgets.QLabel()
        self.title = QtWidgets.QLabel("frmb")
        self.layout_main = QtWidgets.QHBoxLayout()

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.logo)
        self.layout_main.addWidget(self.title)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        self._update_logo()

    def _update_logo(self):
        logo_icon_name = frmb_gui.get_qapp().current_style["icon"]["header-logo"]
        logo_icon = frmb_gui.resources.get_icon(logo_icon_name)
        logo_pixmap = logo_icon.pixmap(64)
        self.logo.setPixmap(logo_pixmap)


class MainControlBarWidget(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.app_title_widget = AppTitleWidget()
        self.layout_main = QtWidgets.QHBoxLayout()

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.app_title_widget)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        # 4. connect

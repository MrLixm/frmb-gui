"""
Definition of the main window.
"""

import logging

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

from .assets import MainMenuBar
from .assets import MainControlBarWidget

LOGGER = logging.getLogger(__name__)


class FrmbControlBarDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.main_widget = MainControlBarWidget()
        self.setWidget(self.main_widget)
        self.setWindowTitle("Control Bar")
        self.setFeatures(self.DockWidgetFeature.DockWidgetMovable)


class FrmbMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.menubar = MainMenuBar(self)
        self.control_bar_dock = FrmbControlBarDock()

        self.setMenuBar(self.menubar)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self.control_bar_dock
        )

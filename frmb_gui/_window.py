"""
Definition of the main window.
"""

import logging

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

from .assets import MainMenuBar
from .assets import MainControlBarWidget
from .assets import AppTitleWidget
from .assets import HierarchyBrowserWidget

LOGGER = logging.getLogger(__name__)


class FrmbControlBarDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.main_widget = MainControlBarWidget()
        self.titlebar_widget = AppTitleWidget()
        self.setWidget(self.main_widget)
        self.setWindowTitle("Control Bar")
        self.setFeatures(
            self.DockWidgetFeature.DockWidgetMovable
            | self.DockWidgetFeature.DockWidgetVerticalTitleBar
        )
        self.setTitleBarWidget(self.titlebar_widget)


class FrmbHierarchyBrowserDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.main_widget = HierarchyBrowserWidget()
        self.setWidget(self.main_widget)
        self.setWindowTitle("Hierarchy Browser")
        self.setFeatures(self.DockWidgetFeature.NoDockWidgetFeatures)


class FrmbMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.menubar = MainMenuBar(self)
        self.control_bar_dock = FrmbControlBarDock()
        self.hierarchy_dock = FrmbHierarchyBrowserDock()

        self.setMenuBar(self.menubar)
        self.setCentralWidget(self.hierarchy_dock)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self.control_bar_dock
        )

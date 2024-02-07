"""
Definition of the main window.
"""

import logging

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# from .assets import MainBarToolbar
# from .assets import ViewportWidget
# from .assets import TaskManagerWidget

LOGGER = logging.getLogger(__name__)


class FrmbMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # # create widget
        # self.widget_mainbar = MainBarToolbar()
        # self.widget_viewport = ViewportWidget()
        # self.widget_taskmanager = TaskManagerWidget()
        # self.dock_taskmanager = QtWidgets.QDockWidget("Parameters")
        #
        # # build layout
        # self.setCentralWidget(self.widget_viewport)
        # self.addToolBar(
        #     QtCore.Qt.ToolBarArea.BottomToolBarArea,
        #     self.widget_mainbar,
        # )
        # self.addDockWidget(
        #     QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
        #     self.dock_taskmanager,
        # )
        #
        # # modify
        # self.dock_taskmanager.setWidget(self.widget_taskmanager)
        # self.widget_mainbar.set_task_manager(self.widget_taskmanager)

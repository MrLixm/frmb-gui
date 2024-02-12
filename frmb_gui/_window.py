"""
Definition of the main window.
"""

import logging
from pathlib import Path

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

from .assets import MainMenuBar
from .assets import MainControlBarWidget
from .assets import AppTitleWidget
from .assets import HierarchyBrowserWidget
from .assets import TextOverlayWidget

LOGGER = logging.getLogger(__name__)


class FrmbControlBarDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.main_widget = MainControlBarWidget()
        self.titlebar_widget = AppTitleWidget()
        self.overlay_frame = TextOverlayWidget(
            text="Drag & Drop Directories", parent=self
        )

        self.setAcceptDrops(True)
        self.setWidget(self.main_widget)
        self.setWindowTitle("Control Bar")
        self.setFeatures(
            self.DockWidgetFeature.DockWidgetMovable
            | self.DockWidgetFeature.DockWidgetVerticalTitleBar
        )
        self.setTitleBarWidget(self.titlebar_widget)

        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setColor(QtGui.QColor(0, 0, 0, 100))
        effect.setOffset(0, 0)
        effect.setBlurRadius(20)
        self.setGraphicsEffect(effect)

        self.overlay_frame.raise_()
        self.overlay_frame.setVisible(False)

    # overrides

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay_frame.setGeometry(self.rect())

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if not event.mimeData() or not event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.DropAction.IgnoreAction)
            event.ignore()
            self.overlay_frame.setVisible(False)
            return

        event.setDropAction(QtCore.Qt.DropAction.LinkAction)
        event.accept()
        self.overlay_frame.setVisible(True)

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent):
        super().dragLeaveEvent(event)
        self.overlay_frame.setVisible(False)

    def dropEvent(self, event: QtGui.QDropEvent):
        try:
            mime_urls = event.mimeData().urls()
            for url in mime_urls:
                path = Path(url.toLocalFile())
                if not path.is_dir():
                    continue
                LOGGER.debug(
                    f"[{self.__class__.__name__}][dropEvent] adding {path} ..."
                )
                self.main_widget.add_root(root_path=path)
        finally:
            self.overlay_frame.setVisible(False)


class FrmbHierarchyBrowserDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.main_widget = HierarchyBrowserWidget()
        self.setWidget(self.main_widget)
        self.setWindowTitle("Hierarchy Browser")
        self.setFeatures(self.DockWidgetFeature.NoDockWidgetFeatures)

        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setColor(QtGui.QColor(0, 0, 0, 100))
        effect.setOffset(0, 0)
        effect.setBlurRadius(20)
        self.setGraphicsEffect(effect)


# we split an inner main window so the menu bar is not affected by the content margins
class InnerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.control_bar_dock = FrmbControlBarDock()
        self.hierarchy_dock = FrmbHierarchyBrowserDock()
        self.setCentralWidget(self.hierarchy_dock)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.TopDockWidgetArea, self.control_bar_dock
        )
        # leave room for the drop-shadow
        self.setContentsMargins(10, 10, 10, 10)


# add an intermediate QFrame, so we can add margins via stylesheet
class InnerCentralWidget(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget = InnerMainWindow()
        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.widget)
        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)


class FrmbMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        self.menubar = MainMenuBar(self)
        self.main_widget = InnerCentralWidget()
        self.setMenuBar(self.menubar)
        self.setCentralWidget(self.main_widget)
        self.setContentsMargins(0, 0, 0, 0)

from typing import Optional

from qtpy import QtWidgets
from qtpy import QtCore

import frmb_gui
from ._context import ContextWidget
from ._context import DependencyViewerTreeWidget


class AboutDialogFrame(QtWidgets.QFrame):
    """
    Widget to display essential information about the current application.

    **Styling**

    - The title can be styled using the ``htmltag`` qt property when set to ``h1`` value.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.label_app = QtWidgets.QLabel(
            f"{frmb_gui.constants.name.title()} - v{frmb_gui.constants.__version__}"
        )
        self.widget_context = ContextWidget(self)
        self.label_dependencies = QtWidgets.QLabel("Dependencies Used: ")
        self.treewidget_dependencies = DependencyViewerTreeWidget(self)

        # build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.label_app)
        self.layout_main.addWidget(self.widget_context)
        self.layout_main.addWidget(self.label_dependencies)
        self.layout_main.addWidget(self.treewidget_dependencies)

        # modify
        self.label_app.setProperty("htmltag", "h1")
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.label_app.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.treewidget_dependencies.setMinimumHeight(150)
        return


class AboutDialog(QtWidgets.QDialog):
    """
    Dialog to display essential information about the current application.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        # create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget = AboutDialogFrame()

        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.widget)

        self.setWindowTitle(f"{frmb_gui.constants.name} - About")
        self.layout_main.setContentsMargins(0, 0, 0, 0)

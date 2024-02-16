import json
from typing import Optional

from qtpy import QtWidgets
from qtpy import QtCore
from qtpy import QtGui

import frmb_gui


class DependencyViewerTreeWidget(QtWidgets.QTreeWidget):
    """
    A TreeWidget that display all the dependencies in the python runtime environement
    as a pair of {name: version}
    """

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self._dependencies: dict[str, str] = {}

        self.setColumnCount(2)
        self.setAlternatingRowColors(False)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setUniformRowHeights(True)
        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        # select only one row at a time
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        # select only rows
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        # remove dotted border on columns
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.setHeaderLabels(("Name", "Version"))
        header = self.header()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        self.populate()

    def populate(self):
        self.clear()
        self._dependencies = {}
        dependencies = frmb_gui.core.get_runtime_dependencies()
        for dependency in dependencies:
            self.add_dependency(dependency[0], dependency[1])
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        return

    def add_dependency(self, name: str, version: str) -> QtWidgets.QTreeWidgetItem:
        self._dependencies[name] = version
        treeitem = QtWidgets.QTreeWidgetItem(self)
        treeitem.setText(0, name)
        treeitem.setText(1, version)
        return treeitem

    def _on_context_menu(self, *args):
        menu = QtWidgets.QMenu(self)
        action = QtWidgets.QAction("Copy All to Clipboard as JSON.", menu)
        action.triggered.connect(self._on_copy_all)
        menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())

    def _on_copy_all(self, *args):
        text = json.dumps(self._dependencies, indent=4)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear()
        clipboard.setText(text)


class ContextWidget(QtWidgets.QFrame):
    """
    Widget to display information about the current runtime context.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self._context: str = frmb_gui.core.get_runtime_context()
        self.separator_width = 3

        # 1. Create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()

        # 2. Add
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.label)

        # 3. Modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )

        # 4. Connections

        self.update_context()
        return

    def update_context(self):
        self._context = frmb_gui.core.get_runtime_context()
        self.label.setText(f"{self._context}")

    def get_context(self) -> Optional[str]:
        """
        Get the string representing the context currently being displayed.
        """
        return self._context

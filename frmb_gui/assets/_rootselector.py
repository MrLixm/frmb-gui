import logging
import webbrowser
from pathlib import Path
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui

LOGGER = logging.getLogger(__name__)


class MenuRootSelectorWidget(QtWidgets.QFrame):

    root_changed_signal = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.main_combobox = QtWidgets.QComboBox()
        self.button_add = QtWidgets.QPushButton()
        self.button_remove = QtWidgets.QPushButton()
        self.button_delete = QtWidgets.QPushButton()
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
        self.main_combobox.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        icon = frmb_gui.get_qapp().current_style.get_icon("plus")
        self.button_add.setIcon(icon)
        self.button_add.setToolTip("Import new Root")

        icon = frmb_gui.get_qapp().current_style.get_icon("minus")
        self.button_remove.setIcon(icon)
        self.button_remove.setToolTip("Remove current Root")

        icon = frmb_gui.get_qapp().current_style.get_icon("folder-remove")
        self.button_delete.setIcon(icon)
        self.button_delete.setToolTip("Delete current Root from disk")

        # 4. connect
        self.button_add.clicked.connect(self._on_add_root)
        self.button_remove.clicked.connect(self._on_remove_root)
        self.button_delete.clicked.connect(self._on_delete_root)
        self.main_combobox.currentIndexChanged.connect(self._on_index_changed)
        self.main_combobox.customContextMenuRequested[QtCore.QPoint].connect(
            self._on_context_menu_combobox
        )
        controller = frmb_gui.get_qapp().controller
        controller.open_root_explorer_action = self._on_open_root_in_explorer

    @property
    def current_root(self) -> frmb_gui.core.FrmbRoot | None:
        """
        Return the root currently selected by the user.
        """
        return self.main_combobox.currentData()

    def has_root(self, root: frmb_gui.core.FrmbRoot) -> bool:
        """
        Return True if the given root is already stored in the combobox as an option.

        Return True even if it is stored in a different instance.
        """
        for index in range(self.main_combobox.count()):
            child_root = self.main_combobox.itemData(index)
            if child_root == root:
                return True

        return False

    def _on_context_menu_combobox(self):

        if not self.current_root:
            return

        qmenu = QtWidgets.QMenu(self)
        action1 = QtWidgets.QAction("Open In File Explorer")
        action1.triggered.connect(self._on_open_root_in_explorer)
        qmenu.addAction(action1)
        qmenu.exec_(QtGui.QCursor.pos())

    def _on_open_root_in_explorer(self):

        if not self.current_root:
            return

        path = self.current_root.path
        webbrowser.open(str(path))

    def _on_index_changed(self, *args):
        self.root_changed_signal.emit()

    def _on_add_root(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self.parent(),
            caption="Import or Create a new Root",
        )
        if not dir_path:
            return

        root = frmb_gui.core.FrmbRoot(Path(dir_path))
        if self.has_root(root):
            # TODO display dialog ?
            return

        self.main_combobox.addItem(str(root.path), root)
        index = self.main_combobox.findData(root)
        self.main_combobox.setCurrentIndex(index)

    def _on_remove_root(self):
        self.main_combobox.removeItem(self.main_combobox.currentIndex())

    def _on_delete_root(self):
        root = self.current_root
        if not root:
            return

        user_result = QtWidgets.QMessageBox.warning(
            self,
            "Are you sure ?",
            (
                f"You are about to delete the current root <{root.path}> from your disk."
                f"\nThis action is not undoable."
                f"\nAre you sure to continue ?"
            ),
            QtWidgets.QMessageBox.StandardButton.Ok
            | QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Cancel,
        )
        if user_result == QtWidgets.QMessageBox.StandardButton.Cancel:
            return

        self._on_remove_root()
        LOGGER.info(f"deleting {root} ...")
        frmb_gui.core.delete_root_from_disk(root)

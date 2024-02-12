import html
import logging
import webbrowser
from pathlib import Path
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui
from ._icon import StylesheetIconButton

LOGGER = logging.getLogger(__name__)


class MenuRootSelectorWidget(QtWidgets.QFrame):

    root_changed_signal = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.layout_main = QtWidgets.QHBoxLayout()
        self.layout_box = QtWidgets.QVBoxLayout()
        self.main_combobox = QtWidgets.QComboBox()
        self.label_title = QtWidgets.QLabel("current menu root")
        self.button_add = StylesheetIconButton("root-add")
        self.button_remove = StylesheetIconButton("root-remove")
        self.button_delete = StylesheetIconButton("root-delete")

        # 2. build layout
        self.setLayout(self.layout_box)
        self.layout_main.addWidget(self.main_combobox)
        self.layout_main.addWidget(self.button_add)
        self.layout_main.addWidget(self.button_remove)
        self.layout_main.addWidget(self.button_delete)
        self.layout_box.addLayout(self.layout_main)
        self.layout_box.addWidget(self.label_title)
        self.layout_box.addStretch(1)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_box.setContentsMargins(0, 0, 0, 0)
        self.main_combobox.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.main_combobox.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.button_add.setToolTip("Import new Root")
        self.button_remove.setToolTip("Remove current Root")
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
        controller.add_root_action = self._on_add_root

    @property
    def current_root(self) -> frmb_gui.core.FrmbRoot | None:
        """
        Return the root currently selected by the user.
        """
        return self.main_combobox.currentData()

    def add_root(self, root_path: Path) -> int:
        """
        Add the given root item to the combobox

        Returns:
            index at which the root was added, -1 if None.
        """
        root = frmb_gui.core.FrmbRoot(root_path)
        if self.has_root(root):
            # TODO display dialog ?
            return -1

        self.main_combobox.addItem(str(root.path), root)
        index = self.main_combobox.findData(root)
        self.main_combobox.setCurrentIndex(index)
        return index

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

    # private

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

        initial_dir = ""
        if frmb_gui.config.developer_mode:
            initial_dir = str(Path(frmb_gui.__path__[0]).parent / "tests" / "data")

        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self.parent(),
            caption="Import or Create a new Root",
            dir=initial_dir,
        )
        if not dir_path:
            return

        LOGGER.debug(f"[{self.__class__.__name__}][_on_add_root] adding {dir_path} ...")
        self.add_root(Path(dir_path))

    def _on_remove_root(self):
        self.main_combobox.removeItem(self.main_combobox.currentIndex())

    def _on_delete_root(self):
        root = self.current_root
        if not root:
            return

        # QtWidgets.QMessageBox.warning(...) cause styling issues, we instance manually.
        message = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Icon.Warning,
            "Are you sure ?",
            html.escape(
                f"You are about to delete the current root <{root.path}> from your disk."
            )
            + f"<br>This action is not undoable."
            + f"<br>Are you sure to continue ?",
            QtWidgets.QMessageBox.StandardButton.Ok
            | QtWidgets.QMessageBox.StandardButton.Cancel,
        )
        message.setDefaultButton(message.StandardButton.Cancel)
        user_result = message.exec()
        if user_result == QtWidgets.QMessageBox.StandardButton.Cancel:
            return

        self._on_remove_root()
        LOGGER.info(f"[{self.__class__.__name__}][_on_delete_root] deleting {root} ...")
        frmb_gui.core.delete_root_from_disk(root)

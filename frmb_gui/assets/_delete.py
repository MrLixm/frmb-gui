import logging
import webbrowser
from pathlib import Path
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb
import frmb_gui.core
from frmb_gui.assets import StylesheetIcon
from frmb_gui.assets import SwitchLabelWidget

LOGGER = logging.getLogger(__name__)


class DeletedFileListWidget(QtWidgets.QListWidget):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _on_context_menu(self, *args):
        menu = QtWidgets.QMenu(self)
        action = QtWidgets.QAction("Open Selected in File Explorer", menu)
        action.triggered.connect(self._open_selected_path)
        menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())

    def _open_selected_path(self):
        selection = self.selectedItems()
        if not selection:
            return

        for item in selection:
            path = str(Path(item.text()).parent)
            webbrowser.open(path)


class MenuDeleterWidget(QtWidgets.QFrame):
    def __init__(
        self,
        menu_files: list[frmb.FrmbFile],
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self._menu_files: list[frmb.FrmbFile] = menu_files

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_options = QtWidgets.QHBoxLayout()
        self.layout_buttons = QtWidgets.QHBoxLayout()
        self.icon_trash = StylesheetIcon("trashbin")
        self.text_header = QtWidgets.QLabel("")
        self.list_files = DeletedFileListWidget()
        self.switch_children = SwitchLabelWidget(
            label="remove children ",
            help_message="Recursively delete all children menu this menu have.",
        )
        self.switch_directory = SwitchLabelWidget(
            label="remove directory",
            help_message="When removing children, also delete the children directory and all other files it might contains.",
        )
        self.text_footer = QtWidgets.QLabel(
            "This action cannot be undone.<br>Do you wish to continue ?"
        )
        self.button_delete = QtWidgets.QPushButton("Delete")
        self.button_cancel = QtWidgets.QPushButton("Cancel")

        # 2. build layout
        self.setLayout(self.layout_main)

        self.layout_main.addWidget(self.icon_trash)
        self.layout_main.addWidget(self.text_header)
        self.layout_main.addWidget(self.list_files)
        self.layout_main.addLayout(self.layout_options)
        self.layout_main.addWidget(self.text_footer)
        self.layout_main.addLayout(self.layout_buttons)
        self.layout_options.addStretch(1)
        self.layout_options.addWidget(self.switch_children)
        self.layout_options.addWidget(self.switch_directory)
        self.layout_options.addStretch(1)
        self.layout_buttons.addWidget(self.button_delete)
        self.layout_buttons.addWidget(self.button_cancel)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_buttons.setContentsMargins(0, 0, 0, 0)
        self.layout_options.setContentsMargins(10, 10, 10, 10)
        self.layout_options.setSpacing(25)

        for item_index in range(self.layout_main.count()):
            item = self.layout_main.itemAt(item_index)
            widget = item.widget() or item.layout()
            if widget is self.list_files:
                continue
            self.layout_main.setAlignment(widget, QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.text_footer.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.switch_children.set_checked(True)
        self.switch_directory.setEnabled(self.switch_children.is_checked())

        # 4. connect
        self.canceled = self.button_cancel.clicked
        self.accepted = self.button_delete.clicked
        self.switch_children.clicked.connect(self._on_switch_children)
        self.switch_directory.clicked.connect(self._on_switch_directory)
        self.populate()

    def populate(self):
        """
        Update the content displayed in the widgets.
        """
        deleted = self.delete_all_menus(dry_run=True)
        self.text_header.setText(
            f"You are about to delete the following {len(deleted)} files from disk:"
        )
        self.list_files.clear()
        for path in deleted:
            self.list_files.addItem(str(path))

    def delete_all_menus(self, dry_run: bool = False) -> list[Path]:
        """
        Perform the destructive action of deleting all the menu and their concerned files.

        Args:
            dry_run:
                True not actually delete any file,
                 but still return all the file that were supposed to be.

        Returns:
            list of path deleted from disk with no duplicates.
        """
        deleted: set[Path] = set()
        for menu in self._menu_files:
            deleted.update(self._delete_menu(menu, dry_run=dry_run))
        return sorted(list(deleted))

    def _delete_menu(
        self,
        menu_file: frmb.FrmbFile,
        dry_run: bool = False,
    ) -> list[Path]:
        """
        Perform the destructive action of deleting the given menu and its concerned files.

        Args:
            menu_file: menu to delete
            dry_run:
                True not actually delete any file,
                 but still return all the file that were supposed to be.

        Returns:
            list of path deleted from disk.
        """
        deleted = frmb.delete_menu_file(
            menu_file=menu_file,
            remove_children=self.switch_children.is_checked(),
            remove_children_dir=self.switch_directory.is_checked(),
            dry_run=dry_run,
        )
        return deleted

    def _on_switch_children(self, *args):
        self.switch_directory.setEnabled(self.switch_children.is_checked())
        self.populate()

    def _on_switch_directory(self, *args):
        self.populate()


class MenuDeleterDialog(QtWidgets.QDialog):
    """
    A dialog for the user to delete multiple menu from disk.
    """

    def __init__(
        self,
        menu_files: list[frmb.FrmbFile],
        dry_run: bool = False,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self._dry_run: bool = dry_run
        self._dry_run_msg: str = "(dryrun)" if self._dry_run else ""

        # 1. Create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget = MenuDeleterWidget(menu_files=menu_files)

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.widget)
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        # 3. modify
        self.setWindowTitle(
            f"{frmb_gui.constants.name} - Delete Menu {self._dry_run_msg}"
        )
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setColor(QtGui.QColor(0, 0, 0, 100))
        effect.setOffset(0, 0)
        effect.setBlurRadius(20)
        self.widget.setGraphicsEffect(effect)

        # 4. connect
        self.widget.canceled.connect(self.close)
        self.widget.accepted.connect(self._on_accepted)

    def _on_accepted(self):
        deleted = self.widget.delete_all_menus(dry_run=self._dry_run)
        LOGGER.info(
            f"[{self.__class__.__name__}]{self._dry_run_msg} "
            f"deleted {len(deleted)} files: {deleted}"
        )
        self.close()

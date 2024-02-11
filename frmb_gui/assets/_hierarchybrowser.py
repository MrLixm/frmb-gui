import logging
from typing import Optional
from typing import Sequence

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb

import frmb_gui.core

LOGGER = logging.getLogger(__name__)


class FrmbFileTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """
    A tree widget item that display the content of a FrmbFile instance.
    """

    columns = {
        "name": {"index": 0, "label": "Name"},
        "file_name": {"index": 1, "label": "File Name"},
        "icon": {"index": 2, "label": "Icon"},
        "paths": {"index": 3, "label": "Registry Paths"},
        "command": {"index": 4, "label": "Command"},
    }
    """
    Configuration of every column in all the QTreeWidgetItems.

    Keys are simple identifier just use to retrieve a value in the dict. One key = one column.

    Values are another dict holding "Qt properties". Available keys:
    - ``index``: in which column this property can be found
    - ``label``: pretty name to use in an header that characterize this column
    - ``resizeMode``: used in header.setSectionResizeMode
    """

    def __init__(
        self,
        frmb_file: frmb.FrmbFile,
        parent: QtWidgets.QTreeWidget | QtWidgets.QTreeWidgetItem = None,
    ):
        super().__init__(parent)
        self._frmb_file: frmb.FrmbFile = frmb_file
        self.update_content()

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} file={self._frmb_file}>"

    @classmethod
    def get_index(cls, name: str) -> int:
        return cls.columns[name]["index"]

    def update_content(self):
        """
        Update the data displayed in the item.
        """
        LOGGER.debug(f"[{self.__class__.__name__}][update_content] updating {self}")

        icon_path = self._frmb_file.content.icon
        icon = QtGui.QIcon(str(icon_path)) if icon_path and icon_path.exists() else None

        self.setCheckState(
            0,
            (
                QtCore.Qt.CheckState.Checked
                if self._frmb_file.content.enabled
                else QtCore.Qt.CheckState.Unchecked
            ),
        )
        self.setText(self.get_index("name"), self._frmb_file.content.name)
        self.setText(self.get_index("file_name"), self._frmb_file.path.stem)
        self.setText(self.get_index("icon"), str(icon_path if icon else "" or ""))
        self.setIcon(self.get_index("icon"), icon or QtGui.QIcon())
        self.setText(self.get_index("paths"), str(self._frmb_file.content.paths))
        self.setText(
            self.get_index("command"), " ".join(self._frmb_file.content.command)
        )


class HierarchyBrowserTreeWidget(QtWidgets.QTreeWidget):
    """
    A tree widget that display the hierarchy of a FrmbRoot.
    """

    def __init__(
        self,
        hierarchy_root: frmb_gui.core.FrmbRoot | None = None,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        self._root: frmb_gui.core.FrmbRoot | None = hierarchy_root

        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setUniformRowHeights(True)
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)
        self.setSelectionMode(self.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)

        # set model based on FrmbFileTreeWidgetItem

        self.setColumnCount(len(FrmbFileTreeWidgetItem.columns))

        header = self.header()
        model = self.model()  # type: QtCore.QAbstractItemModel
        header.setSectionResizeMode(header.ResizeMode.Interactive)
        header.setSortIndicator(0, QtCore.Qt.SortOrder.AscendingOrder)

        for column_id, column_config in FrmbFileTreeWidgetItem.columns.items():

            column_index = column_config["index"]
            size_hint = column_config.get("sizeHint")
            if size_hint:
                self.setColumnWidth(column_index, size_hint)
            resize_mode = column_config.get("resizeMode")
            if resize_mode:
                header.setSectionResizeMode(column_index, resize_mode)

            column_name = column_config.get("label", column_id)
            model.setHeaderData(
                column_index,
                QtCore.Qt.Orientation.Horizontal,
                column_name,
            )

    def paintEvent(self, event: QtGui.QPaintEvent):
        """
        Paint a useful text when there is no root, or it has no children.
        """
        super().paintEvent(event)

        text = None

        if not self._root:
            text = "No root set."

        elif not self._root.children:
            text = f"No children yet for root {self._root.path}."

        if not text:
            return

        qpainter = QtGui.QPainter(self.viewport())
        qpainter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, text)
        return

    def change_root(self, new_root: frmb_gui.core.FrmbRoot | None):
        self._root = new_root
        self.populate()

    def populate(self):
        self.clear()
        if not self._root:
            return
        self._populate(children=self._root.children, parent=self)

    def _populate(
        self,
        children: Sequence[frmb.FrmbFile],
        parent: QtWidgets.QTreeWidget | QtWidgets.QTreeWidgetItem,
    ):
        for file in children:
            item = FrmbFileTreeWidgetItem(frmb_file=file, parent=parent)
            self._populate(file.children, parent=item)


class HierarchyBrowserWidget(QtWidgets.QFrame):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.treewidget = HierarchyBrowserTreeWidget()

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.treewidget)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        # 4. connect
        controller = frmb_gui.get_qapp().controller
        controller.root_changed_signal.connect(self._on_root_changed)

    def _on_root_changed(self, new_root: frmb_gui.core.FrmbRoot | None):
        self.treewidget.change_root(new_root)

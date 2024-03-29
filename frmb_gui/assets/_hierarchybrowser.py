import logging
from typing import Optional
from typing import Sequence

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb

import frmb_gui.core
from ._icon import StylesheetIconButton

LOGGER = logging.getLogger(__name__)


class FrmbFileTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """
    A tree widget item that display the content of a FrmbFile instance.
    """

    columns = {
        "name": {"index": 0, "label": "Name"},
        "icon": {"index": 1, "label": "Icon"},
        "paths": {"index": 2, "label": "Registry Paths"},
        "command": {"index": 3, "label": "Command"},
        "file_name": {"index": 4, "label": "File Name"},
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

        content = self._frmb_file.content(resolve_tokens=True)

        icon_path = content.icon
        icon = QtGui.QIcon(str(icon_path)) if icon_path and icon_path.exists() else None
        if icon is not None and icon.isNull():
            LOGGER.warning(f"Cannot load existing icon <{icon_path}> to QIcon")
        if icon_path:
            icon_path = str(icon_path.name)

        registry_paths = len(content.paths)
        command = "yes" if content.command else "no"

        self.setCheckState(
            0,
            (
                QtCore.Qt.CheckState.Checked
                if content.enabled
                else QtCore.Qt.CheckState.Unchecked
            ),
        )
        self.setText(self.get_index("name"), content.name)
        self.setText(self.get_index("file_name"), self._frmb_file.path.stem)
        self.setText(self.get_index("icon"), str(icon_path if not icon else ""))
        self.setIcon(self.get_index("icon"), icon or QtGui.QIcon())
        if self._frmb_file.at_root():
            self.setText(self.get_index("paths"), f"{registry_paths} paths")
        self.setText(self.get_index("command"), command)

        font = QtGui.QFont()
        font.setWeight(font.Weight.Bold)
        self.setFont(self.get_index("name"), font)


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

        header = self.header()  # type: QtWidgets.QHeaderView
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

    # overrides

    def paintEvent(self, event: QtGui.QPaintEvent):
        """
        Paint a useful text when there is no root, or it has no children.
        """
        style = frmb_gui.get_qapp().current_style
        indentation = (
            style.content.get("widget", {}).get("treewidget", {}).get("indent", 30)
        )
        self.setIndentation(indentation)

        super().paintEvent(event)

        text = None

        if not self._root:
            text = "No root set."

        elif not self._root.children:
            text = f"No children yet for root {self._root.path}."

        if not text:
            return

        qpainter = QtGui.QPainter(self.viewport())
        qpainter.drawText(
            self.viewport().rect(),
            QtCore.Qt.AlignmentFlag.AlignCenter,
            text,
        )
        return

    def change_root(self, new_root: frmb_gui.core.FrmbRoot | None):
        self._root = new_root
        self.populate()

    def populate(self):
        self.clear()
        if not self._root:
            return
        self._populate(children=self._root.children, parent=self)
        header = self.header()  # type: QtWidgets.QHeaderView
        header.resizeSections(header.ResizeMode.ResizeToContents)

    # private

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
        self.toolbar = QtWidgets.QToolBar()
        self.button_update = StylesheetIconButton("refresh")
        self.treewidget = HierarchyBrowserTreeWidget()

        # 2. build layout
        self.setLayout(self.layout_main)
        self.toolbar.addWidget(self.button_update)
        self.layout_main.addWidget(self.toolbar)
        self.layout_main.addWidget(self.treewidget)

        # 3. modify
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_main.setSpacing(0)
        self.button_update.setToolTip("Refresh tree widget content.")

        # 4. connect
        controller = frmb_gui.get_qapp().controller
        controller.root_changed_signal.connect(self._on_root_changed)
        self.button_update.clicked.connect(self._on_refresh)

    def _on_root_changed(self, new_root: frmb_gui.core.FrmbRoot | None):
        self.treewidget.change_root(new_root)

    def _on_refresh(self, *args):
        self.treewidget.populate()

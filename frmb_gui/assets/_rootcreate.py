import logging
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

from frmb_gui.assets import BaseDialog
from frmb_gui.assets import StylesheetIcon
import frmb_gui.core

LOGGER = logging.getLogger(__name__)


class LabeledLineEdit(QtWidgets.QFrame):
    """
    A QLineEdit with a help icon and a label on its left.
    """

    def __init__(
        self,
        label: str,
        tooltip: str,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        # 1. create
        self.layout_main = QtWidgets.QHBoxLayout()
        self.icon_help = StylesheetIcon("help")
        self.name_label = QtWidgets.QLabel(label)
        self.name_field = QtWidgets.QLineEdit()

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.icon_help)
        self.layout_main.addWidget(self.name_label)
        self.layout_main.addWidget(self.name_field)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.icon_help.setToolTip(tooltip)

        # 4. connect

    def get_text(self) -> str:
        return self.name_field.text()


class RootFileCreatorWidget(QtWidgets.QFrame):
    """
    Open a dialog to ask the user how to create a new root file.

    It is up to the developer to handle if a root file already exists or not.

    **Styling**

    Example::

        QFrame.RootFileCreatorWidget QLabel#path-label {
            font-family: mono;
            color: white;
        }
        QFrame.RootFileCreatorWidget QFrame.LabeledLineEdit {
            margin: 5px;
        }
    """

    def __init__(
        self,
        root: frmb_gui.core.FrmbRoot,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self._root: frmb_gui.core.FrmbRoot = root

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()

        self.label_title = QtWidgets.QLabel("Creating a new Frmb root hierarchy at")
        self.label_path = QtWidgets.QLabel(f"{self._root.path}")
        self.linededit = LabeledLineEdit(
            label="name", tooltip="A human-readable name to display in the GUI."
        )

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.label_title)
        self.layout_main.addWidget(self.label_path)
        self.layout_main.addWidget(self.linededit)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.label_path.setObjectName("path-label")
        self.label_path.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )

        # 4. connect

    def create_root_file(self) -> frmb_gui.core.FrmbRootFile:
        file = self._root.create_root_file(name=self.linededit.get_text())
        LOGGER.info(f"[{self.__class__.__name__}][create_root_file] created {file}")
        return file


class RootFileCreatorDialog(BaseDialog):
    """
    Open a dialog to ask the user how to create a new root file.

    It is up to the developer to handle if a root file already exists or not.

    **Styling**

    Don't style this dialog directly, style ``QFrame.RootFileCreatorWidget`` instead.
    """

    def __init__(
        self,
        root: frmb_gui.core.FrmbRoot,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(title="Create New Root", parent=parent)

        self._root: frmb_gui.core.FrmbRoot = root
        self._created: frmb_gui.core.FrmbRootFile | None = None

        self.widget_main = RootFileCreatorWidget(root=self._root)
        self.set_main_widget(action_button_label="Create", widget=self.widget_main)

    def _on_accepted(self):
        self._created = self.widget_main.create_root_file()

    def exec(self) -> frmb_gui.core.FrmbRootFile | None:
        super().exec()
        return self._created

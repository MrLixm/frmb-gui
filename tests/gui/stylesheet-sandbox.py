import html
import logging
import logging.config
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

import frmb
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui
import frmb_gui.assets
import frmb_gui._utils
from frmb_gui.assets._rootselector import DeleteWarningDialog


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.checkbox_disable = QtWidgets.QCheckBox("Disable ALL")
        self.button = QtWidgets.QPushButton("Open Root Deleter")
        self.label = QtWidgets.QLabel("PlaceHolder Label")
        self.combobox = QtWidgets.QComboBox()
        self.checkbox_area = QtWidgets.QCheckBox("show area")
        self.scroll_area = QtWidgets.QScrollArea()
        self.switch = frmb_gui.assets.SwitchButton()
        self.switch_disabled = frmb_gui.assets.SwitchButton()
        self.switch_label = frmb_gui.assets.SwitchLabelWidget(
            "descriptive text", "this is some help text"
        )
        self.button_menudeleter = QtWidgets.QPushButton("Open MenuDeleter")
        image_label = QtWidgets.QLabel()
        image = QtGui.QIcon(str(frmb_gui.resources.get_icon_path("logo-dark-bg.svg")))
        image_label.setPixmap(image.pixmap(1024))
        self.button_rootcreate = QtWidgets.QPushButton("Open RootFileCreator")

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.checkbox_disable)
        self.layout_main.addWidget(self.label)
        self.layout_main.addWidget(self.combobox)
        self.layout_main.addWidget(self.checkbox_area)
        self.layout_main.addWidget(self.scroll_area)
        self.layout_main.addWidget(self.switch)
        self.layout_main.addWidget(self.switch_disabled)
        self.layout_main.addWidget(self.switch_label)
        self.layout_main.addWidget(self.button)
        self.layout_main.addWidget(self.button_menudeleter)
        self.layout_main.addWidget(self.button_rootcreate)

        # 3. modify
        self.layout_main.setContentsMargins(*([25] * 4))
        self.combobox.addItems(
            [
                r"Z:\packages-dev\frmb-gui\frmb_gui\_config.py",
                r"Z:\packages-dev\frmb-gui\frmb_gui\cli.py",
                r"Z:\packages-dev\frmb-gui\frmb_gui\_utils.py",
                r"Z:\packages-dev\frmb-gui\frmb_gui\_window.py",
            ]
        )
        self.switch_disabled.setDisabled(True)
        self.checkbox_area.setChecked(True)
        self.scroll_area.setWidget(image_label)
        self.scroll_area.setMaximumWidth(500)
        self.scroll_area.setMaximumHeight(500)

        # 4. connect
        self.checkbox_disable.stateChanged.connect(self._on_disable_all)
        self.button.clicked.connect(self._on_button_press)
        self.checkbox_area.clicked.connect(self._on_toggle_area)
        self.switch.clicked.connect(self._on_switch_changed)
        self.button_menudeleter.clicked.connect(self._on_open_menudeleter)
        self.button_rootcreate.clicked.connect(self._on_open_rootcreator)

    def _on_toggle_area(self):
        self.scroll_area.setVisible(not self.scroll_area.isVisible())
        print(f"switch: {self.switch.isChecked()}")

    def _on_button_press(self):
        tmp_dir = Path(tempfile.mkdtemp(frmb_gui.__name__))
        root = frmb_gui.core.FrmbRoot(path=tmp_dir)
        dialog = DeleteWarningDialog(root=root)
        result = dialog.exec()
        if result != dialog.DialogCode.Accepted:
            print("dialog canceled")
        else:
            print("dialog accepted")
        shutil.rmtree(tmp_dir)

    def _on_switch_changed(self):
        print(f"switch: {self.switch.isChecked()}")

    def _on_disable_all(self, disabled):
        for item_index in range(self.layout_main.count()):
            item = self.layout_main.itemAt(item_index)
            widget = item.widget() or item.layout()
            if widget is self.checkbox_disable:
                continue
            widget.setDisabled(disabled)

    def _on_open_menudeleter(self):

        data_dir = Path(frmb_gui.__path__[0]).parent / "tests" / "data" / "structure1"
        tmp_dir = Path(tempfile.mkdtemp(frmb_gui.__name__)) / "structure1"
        shutil.copytree(data_dir, tmp_dir)

        file = frmb.FrmbFile(tmp_dir / "ffmpeg-videos.frmb", root_dir=tmp_dir)

        widget = frmb_gui.assets.MenuDeleterDialog(
            menu_files=[file],
            dry_run=True,
            parent=self,
        )
        widget.exec()

        shutil.rmtree(tmp_dir)

    def _on_open_rootcreator(self):

        tmp_dir = Path(tempfile.mkdtemp(frmb_gui.__name__)) / "frmbroot"
        tmp_dir.mkdir()

        root = frmb_gui.core.FrmbRoot(path=tmp_dir)
        dialog = frmb_gui.assets.RootFileCreatorDialog(root=root)
        file = dialog.exec()
        print(file)
        print(root.root_file)

        shutil.rmtree(tmp_dir)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)


def main():
    """
    Start the application.
    """
    logging.basicConfig(
        level=logging.DEBUG if frmb_gui.config.debug else logging.INFO,
        format="{levelname: <7} | {asctime} [{name: >30}] {message}",
        style="{",
        stream=sys.stdout,
    )
    app = frmb_gui.get_qapp()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

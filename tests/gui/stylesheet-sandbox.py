import html
import logging
import logging.config
import sys
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui
import frmb_gui.assets
import frmb_gui._utils


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QPushButton("place holder")
        self.label = QtWidgets.QLabel("PlaceHolder Label")
        self.combobox = QtWidgets.QComboBox()
        self.checkbox_area = QtWidgets.QCheckBox("show area")
        self.scroll_area = QtWidgets.QScrollArea()
        self.switch = frmb_gui.assets.SwitchButton()
        self.switch_disabled = frmb_gui.assets.SwitchButton()
        image_label = QtWidgets.QLabel()
        image = QtGui.QIcon(str(frmb_gui.resources.get_icon_path("logo-dark-bg.svg")))
        image_label.setPixmap(image.pixmap(1024))

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.button)
        self.layout_main.addWidget(self.label)
        self.layout_main.addWidget(self.combobox)
        self.layout_main.addWidget(self.checkbox_area)
        self.layout_main.addWidget(self.scroll_area)
        self.layout_main.addWidget(self.switch)
        self.layout_main.addWidget(self.switch_disabled)

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
        self.button.clicked.connect(self._on_button_press)
        self.checkbox_area.clicked.connect(self._on_toggle_area)
        self.switch.clicked.connect(self._on_switch_changed)

    def _on_toggle_area(self):
        self.scroll_area.setVisible(not self.scroll_area.isVisible())
        print(f"switch: {self.switch.isChecked()}")

    def _on_button_press(self):
        message = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Icon.Warning,
            "Are you sure ?",
            html.escape(
                f"You are about to delete the current root <ewg> from your disk."
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
        print("FEaihwOI !")

    def _on_switch_changed(self):
        print(f"switch: {self.switch.isChecked()}")


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

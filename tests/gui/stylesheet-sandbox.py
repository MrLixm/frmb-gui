import logging
import logging.config
import sys
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui
import frmb_gui._utils


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.button = QtWidgets.QPushButton("place holder")
        self.label = QtWidgets.QLabel("PlaceHolder Label")
        self.combobox = QtWidgets.QComboBox()

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.button)
        self.layout_main.addWidget(self.label)
        self.layout_main.addWidget(self.combobox)

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

        # 4. connect


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
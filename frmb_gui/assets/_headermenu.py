import webbrowser

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui
from ._issue import IssueDialog
from ._about import AboutDialog


class MainMenuBar(QtWidgets.QMenuBar):
    """
    Menu bar of the application. Always visible.
    """

    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__(parent)

        # 1. Create
        self.dialog_issue = IssueDialog()
        self.dialog_about = AboutDialog()

        self.menu_file = self.addMenu("File")
        self.menu_edit = self.addMenu("Edit")
        self.menu_help = self.addMenu("Help")

        self.action_exit = QtWidgets.QAction("Exit")
        self.action_about = QtWidgets.QAction("About")
        self.action_open_doc = QtWidgets.QAction("Open Documentation")
        # TODO add log directory action when the feature is implemented
        self.action_discord = QtWidgets.QAction("Join the Discord Server")
        self.action_issue = QtWidgets.QAction("Report an Issue")
        self.action_open_root_explorer = QtWidgets.QAction(
            "Open Current Root in File Explorer"
        )

        # 2. Add
        self.menu_file.addAction(self.action_exit)
        self.menu_help.addAction(self.action_about)
        self.menu_help.addAction(self.action_open_doc)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.action_discord)
        self.menu_help.addAction(self.action_issue)
        self.menu_edit.addAction(self.action_open_root_explorer)

        # 3. Modify
        self.action_exit.setShortcut("Ctrl+Q")

        # 4. Connections
        controller = frmb_gui.get_qapp().controller
        self.action_exit.triggered.connect(QtWidgets.QApplication.quit)
        self.action_issue.triggered.connect(self._on_dialog_issue_show)
        self.action_open_doc.triggered.connect(self._on_open_documentation)
        self.action_about.triggered.connect(self._on_dialog_about_show)
        self.action_discord.triggered.connect(self._on_open_discord_invite)
        self.action_open_root_explorer.triggered.connect(self._on_open_root_explorer)

        if frmb_gui.config.developer_mode:
            self._build_dev_menu()

    def _build_dev_menu(self):
        menu_debug = self.addMenu("Debug")

        action_print_stylesheet = QtWidgets.QAction("Print Stylesheet", menu_debug)
        action_print_stylesheet.triggered.connect(self._on_print_stylesheet)
        menu_debug.addAction(action_print_stylesheet)

        action_print_config = QtWidgets.QAction("Print Config", menu_debug)
        action_print_config.triggered.connect(self._on_print_config)
        menu_debug.addAction(action_print_config)

    @staticmethod
    def _on_open_documentation():
        webbrowser.open(frmb_gui.constants.documentation_url)

    @staticmethod
    def _on_open_discord_invite():
        webbrowser.open("https://discord.gg/47ySGqMEAj")

    def _on_dialog_issue_show(self):
        self.dialog_issue.show()

    def _on_dialog_about_show(self):
        self.dialog_about.show()

    @staticmethod
    def _on_open_root_explorer():
        controller = frmb_gui.get_qapp().controller
        controller.open_root_explorer_action()

    @staticmethod
    def _on_print_stylesheet():
        print(frmb_gui.get_qapp().styleSheet())

    @staticmethod
    def _on_print_config():
        frmb_gui.config.__debugging__()

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

        # 2. Add
        self.menu_file.addAction(self.action_exit)
        self.menu_help.addAction(self.action_about)
        self.menu_help.addAction(self.action_open_doc)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.action_discord)
        self.menu_help.addAction(self.action_issue)

        # 3. Modify
        self.action_exit.setShortcut("Ctrl+Q")

        # 4. Connections
        self.action_exit.triggered.connect(QtWidgets.QApplication.quit)
        self.action_issue.triggered.connect(self._on_dialog_issue_show)
        self.action_open_doc.triggered.connect(self._on_open_documentation)
        self.action_about.triggered.connect(self._on_dialog_about_show)
        self.action_discord.triggered.connect(self._on_open_discord_invite)

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

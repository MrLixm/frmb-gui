import webbrowser
from typing import Optional

from qtpy import QtWidgets
from qtpy import QtCore

import frmb_gui
from ._context import ContextWidget


class IssueDialogFrame(QtWidgets.QFrame):
    """
    A widget explaining to the user how to report an issue.

    **Styling**

    - The title can be styled using the ``htmltag`` qt property when set to ``h1`` value.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        # 1. Create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.label_title = QtWidgets.QLabel("Reporting an Issue")
        self.label_body = QtWidgets.QLabel(
            "Issue tracking is handled on GitHub. You will need a free GitHub account "
            f"to create a new issue on the {frmb_gui.constants.name} repository.\n\n"
            "When submitting an issue please use the following information:"
        )
        self.widget_context = ContextWidget(self)
        self.button_report = QtWidgets.QPushButton("Report a New Issue")

        # 2. Add
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.label_title)
        self.layout_main.addWidget(self.label_body)
        self.layout_main.addWidget(self.widget_context)
        self.layout_main.addStretch(0)
        self.layout_main.addWidget(self.button_report)

        # 3. Modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.label_title.setProperty("htmltag", "h1")
        self.label_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_body.setWordWrap(True)
        # 4. Connections
        self.button_report.clicked.connect(self.on_report_issue)

        return

    def on_report_issue(self):
        """
        Open the url to create a new issue on the repo in the user's default webbrowser
        """
        url = frmb_gui.core.get_context_reporting_url(self.widget_context.get_context())
        webbrowser.open(url)
        return


class IssueDialog(QtWidgets.QDialog):
    """
    A dialog explaining to the user how to report an issue.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(f"{frmb_gui.constants.name} - Report an Issue")

        # 1. Create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget = IssueDialogFrame()

        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.widget)

        self.layout_main.setContentsMargins(0, 0, 0, 0)

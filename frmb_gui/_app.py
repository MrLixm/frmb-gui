"""
Definition of the unique runtime QtApplication.
"""

import logging
from pathlib import Path
from typing import Optional

import qtpy
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui


LOGGER = logging.getLogger(__name__)


class FrmbApplication(QtWidgets.QApplication):
    """
    QApplication to use as unique instance.

    Handle styling of the application using stylesheets.
    """

    def __init__(self):
        super().__init__()
        # one of the file defined in resources/stylesheets
        self._stylesheet_name = "main"
        # one of the file defined in resources/styles
        self._style_name = "main"
        self._file_watch_stylesheet: Optional[QtCore.QFileSystemWatcher] = None

        self.setOrganizationName(frmb_gui.constants.organisation)
        self.setApplicationName(frmb_gui.constants.name)
        self.setApplicationVersion(frmb_gui.__version__)
        if not qtpy.QT6:
            self.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        self.reload_icon()
        self.reload_stylesheet()

        if frmb_gui.config.developer_mode:
            self._install_stylesheet_reload()

        # TODO clean
        frmb_gui.resources.browser.load_font_family("roboto")
        frmb_gui.resources.browser.load_font_family("jetbrainsmono")

    @property
    def current_style(self) -> dict:
        """
        Return the currently active style as a python dictionnary.
        """
        return frmb_gui.resources.get_style(self._style_name)

    def _install_stylesheet_reload(self):
        """
        Install a file watcher to reload the stylesheets when those change.
        """
        stylesheet_path = frmb_gui.resources.get_stylesheet_path(self._stylesheet_name)
        style_path = frmb_gui.resources.get_style_path(self._style_name)
        paths = [str(stylesheet_path), str(style_path)]
        self._file_watch_stylesheet = QtCore.QFileSystemWatcher(paths, self)
        self._file_watch_stylesheet.fileChanged.connect(self._on_stylesheet_changed)

        paths = [Path(path).name for path in paths]
        LOGGER.debug(f"installed QFileSystemWatcher for {paths}")

    def _on_stylesheet_changed(self, *args):
        # XXX: the watcher might call this 2 times in a row depending on how the file
        #   was changed. See https://forum.qt.io/topic/41401/solved-qfilesystemwatcher-reports-change-twice/7
        self.reload_stylesheet()
        self.reload_icon()
        LOGGER.debug(
            f"[{self.__class__.__name__}][_on_stylesheet_changed] triggered by {args}"
        )

    def reload_icon(self):
        """
        Reload the application icon from disk (doesn't work on Mac).
        """
        icon_name = self.current_style["icon"]["app-favicon"]
        icon = frmb_gui.resources.get_icon(icon_name)
        if not frmb_gui.osplatform.is_mac():
            self.setWindowIcon(icon)

    def set_stylesheet(self, stylesheet_name: str, style_name: str):
        """
        Change the stylesheet to the given options.

        Args:
            stylesheet_name: file name of the stylesheet on disk, without extension
            style_name: file name of the style on disk, without extension
        """
        self._stylesheet_name = stylesheet_name
        self._style_name = style_name
        self._install_stylesheet_reload()
        self.reload_stylesheet()

    def reload_stylesheet(self):
        """
        Reapply the stylesheet after re-reading its content from disk.
        """
        stylesheet = frmb_gui.resources.get_stylesheet(
            name=self._stylesheet_name,
            style_name=self._style_name,
        )
        self.setStyleSheet(stylesheet)


def get_qapp() -> FrmbApplication:
    """
    Returns:
        new QApplication instance or None if it already exists.
    """
    return QtWidgets.QApplication.instance() or FrmbApplication()

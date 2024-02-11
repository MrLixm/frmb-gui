"""
Definition of the unique runtime QtApplication.
"""

import logging
from pathlib import Path
from typing import Callable
from typing import Optional

import qtpy
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

import frmb_gui


LOGGER = logging.getLogger(__name__)


class ApplicationController(QtCore.QObject):
    """
    A high-level object to transfer information between arbitrary nested widget easily.
    """

    root_changed_signal = QtCore.Signal(object)
    """
    Emitted when the root directory is changed.
    
    The object is a frmb_gui.core.FrmbRoot instance.
    """


class FrmbApplication(QtWidgets.QApplication):
    """
    QApplication to use as unique instance.

    Handle styling of the application using stylesheets and styles.

    Styles are a library of variables that allow to resolve a stylesheet.
    Both can be changed at runtime even if stylesheets are less frequent to be.
    """

    def __init__(self):
        super().__init__()

        self._controller = ApplicationController()
        self._style_callbacks: list[Callable[[dict], None]] = []

        # one of the file defined in resources/stylesheets
        self._stylesheet_name = "main"
        # one of the file defined in resources/styles
        self._style_name = "main"
        self._file_watch_stylesheet: Optional[QtCore.QFileSystemWatcher] = None
        self._file_watch_style: Optional[QtCore.QFileSystemWatcher] = None

        self.setOrganizationName(frmb_gui.constants.organisation)
        self.setApplicationName(frmb_gui.constants.name)
        self.setApplicationVersion(frmb_gui.__version__)
        if not qtpy.QT6:
            self.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        self.reload_icon()
        self.reload_stylesheet()

        self._install_style_reload()
        # TODO see if only desired in dev mode
        if frmb_gui.config.developer_mode:
            self._install_stylesheet_reload()

        # TODO clean
        frmb_gui.resources.browser.load_font_family("roboto")
        frmb_gui.resources.browser.load_font_family("jetbrainsmono")

    @property
    def controller(self) -> ApplicationController:
        return self._controller

    @property
    def current_style(self) -> dict:
        """
        Return the currently active style as a python dictionnary.
        """
        return frmb_gui.resources.get_style(self._style_name)

    def _install_style_reload(self):
        """
        Install a file watcher to reload the style when this change.
        """
        style_path = frmb_gui.resources.get_style_path(self._style_name)
        paths = [str(style_path)]
        self._file_watch_style = QtCore.QFileSystemWatcher(paths, self)
        self._file_watch_style.fileChanged.connect(self._on_style_changed)
        LOGGER.debug(f"installed QFileSystemWatcher for style {style_path.name}")

    def _install_stylesheet_reload(self):
        """
        Install a file watcher to reload the stylesheets when those change.
        """
        stylesheet_path = frmb_gui.resources.get_stylesheet_path(self._stylesheet_name)
        paths = [str(stylesheet_path)]
        self._file_watch_stylesheet = QtCore.QFileSystemWatcher(paths, self)
        self._file_watch_stylesheet.fileChanged.connect(self._on_stylesheet_changed)
        LOGGER.debug(
            f"installed QFileSystemWatcher for stylesheet {stylesheet_path.name}"
        )

    def _on_style_changed(self, *args):
        # XXX: the watcher might call this 2 times in a row depending on how the file
        #   was changed. See https://forum.qt.io/topic/41401/solved-qfilesystemwatcher-reports-change-twice/7
        LOGGER.debug(
            f"[{self.__class__.__name__}][_on_style_changed] triggered by {args}"
        )
        self.reload_stylesheet()
        self.reload_icon()
        for callback in self._style_callbacks:
            callback(self.current_style)

    def _on_stylesheet_changed(self, *args):
        # XXX: the watcher might call this 2 times in a row depending on how the file
        #   was changed. See https://forum.qt.io/topic/41401/solved-qfilesystemwatcher-reports-change-twice/7
        LOGGER.debug(
            f"[{self.__class__.__name__}][_on_stylesheet_changed] triggered by {args}"
        )
        self.reload_stylesheet()
        self.reload_icon()

    def add_on_style_changed_callback(self, callback: Callable[[dict], None]):
        """
        Add a callable that is called when the global app style is changed.

        Args:
            callback: a function/callable that receive the new style to load (as dict).
        """
        self._style_callbacks.append(callback)

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

        reloadstyle = self._style_name != style_name

        self._style_name = style_name
        self._install_style_reload()
        self._install_stylesheet_reload()
        if reloadstyle:
            self._on_style_changed()
        else:
            self._on_stylesheet_changed()

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

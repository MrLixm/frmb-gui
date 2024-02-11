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

    open_root_explorer_action: Callable[[], None] = None
    """
    Callable that open the currently selected root in the system file explorer.
    """

    add_root_action: Callable[[], None] = None
    """
    Callable that opena file explorer to select a root to add.
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
        self._style_callbacks: list[Callable[[frmb_gui.resources.UiStyle], None]] = []

        # one of the file defined in resources/stylesheets
        self._stylesheet_name: str = "main"
        self._stylesheet_path: Path | None = None
        # one of the file defined in resources/styles
        self._style_name: str = "main"
        self._style_path: Path | None = None
        self._style: frmb_gui.resources.UiStyle | None = None

        self._file_watch_stylesheet: Optional[QtCore.QFileSystemWatcher] = None
        self._file_watch_style: Optional[QtCore.QFileSystemWatcher] = None

        self.setOrganizationName(frmb_gui.constants.organisation)
        self.setApplicationName(frmb_gui.constants.name)
        self.setApplicationVersion(frmb_gui.__version__)
        if not qtpy.QT6:
            self.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        self.set_style(self._style_name)
        self.set_stylesheet(self._stylesheet_name)

    @property
    def controller(self) -> ApplicationController:
        return self._controller

    @property
    def current_style(self) -> frmb_gui.resources.UiStyle:
        """
        Return the currently active style as convenient custom object.
        """
        return self._style

    def add_on_style_changed_callback(
        self, callback: Callable[[frmb_gui.resources.UiStyle], None]
    ):
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
        icon = self.current_style.get_icon("app_favicon")
        if not frmb_gui.osplatform.is_mac():
            self.setWindowIcon(icon)

    def reload_style(self):
        """
        Reapply the style after re-reading its content from disk.
        """
        self._style = frmb_gui.resources.UiStyle.from_path(path=self._style_path)
        self.reload_stylesheet()
        self.reload_icon()
        for callback in self._style_callbacks:
            callback(self.current_style)

    def reload_stylesheet(self):
        """
        Reapply the stylesheet after re-reading its content from disk.
        """
        stylesheet = self.current_style.get_stylesheet(name=self._stylesheet_name)
        self.setStyleSheet(stylesheet)

    def set_style(self, style_name: str):
        """
        Change the style.

        Args:
            style_name: file name of the stylesheet on disk, without extension
        """
        self._style_name = style_name
        self._style_path = frmb_gui.resources.get_style_path(self._style_name)
        self._install_style_reload()
        self.reload_style()

    def set_stylesheet(self, stylesheet_name: str):
        """
        Change the stylesheet.

        Args:
            stylesheet_name: file name of the stylesheet on disk, without extension
        """
        self._stylesheet_name = stylesheet_name
        self._stylesheet_path = frmb_gui.resources.get_stylesheet_path(stylesheet_name)
        self._install_stylesheet_reload()
        self.reload_stylesheet()

    def _install_style_reload(self):
        """
        Install a file watcher to reload the style when its corresponding file change.
        """
        paths = [str(self._style_path)]
        self._file_watch_style = QtCore.QFileSystemWatcher(paths, self)
        self._file_watch_style.fileChanged.connect(self._on_style_file_changed)
        prefix = self.__class__.__name__
        LOGGER.debug(
            f"[{prefix}][_install_stylesheet_reload] installed QFileSystemWatcher for "
            f"style {self._style_path.name}"
        )

    def _install_stylesheet_reload(self):
        """
        Install a file watcher to reload the stylesheet when its corresponding file change.
        """
        # TODO see if only desired in dev mode
        if not frmb_gui.config.developer_mode:
            self._file_watch_stylesheet = None
            return

        paths = [str(self._stylesheet_path)]
        self._file_watch_stylesheet = QtCore.QFileSystemWatcher(paths, self)
        self._file_watch_stylesheet.fileChanged.connect(
            self._on_stylesheet_file_changed
        )
        prefix = self.__class__.__name__
        LOGGER.debug(
            f"[{prefix}][_install_stylesheet_reload] installed QFileSystemWatcher for "
            f"stylesheet {self._stylesheet_path.name}"
        )

    # XXX: the watcher might call this 2 times in a row depending on how the file
    #   was changed. See https://forum.qt.io/topic/41401/solved-qfilesystemwatcher-reports-change-twice/7
    def _on_style_file_changed(self, *args):
        prefix = self.__class__.__name__
        LOGGER.debug(f"[{prefix}][_on_style_file_changed] triggered by {args}")
        self.reload_style()

    def _on_stylesheet_file_changed(self, *args):
        prefix = self.__class__.__name__
        LOGGER.debug(f"[{prefix}][_on_stylesheet_file_changed] triggered by {args}")
        self.reload_stylesheet()


def get_qapp() -> FrmbApplication:
    """
    Returns:
        new QApplication instance or None if it already exists.
    """
    return QtWidgets.QApplication.instance() or FrmbApplication()

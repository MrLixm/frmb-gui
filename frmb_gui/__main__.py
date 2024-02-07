import logging
import logging.config
import sys

import frmb_gui
import frmb_gui._utils


logger = logging.getLogger(f"frmb_gui.__main__")


def launch_gui():
    # XXX: since we subclass QApplication this create a crash on app close
    #   see issue https://bugreports.qt.io/browse/PYSIDE-1447
    app = frmb_gui.get_qapp()

    main_window = frmb_gui.FrmbMainWindow()
    main_window.show()
    frmb_gui._utils.center_in_screen(main_window)

    sys.exit(app.exec_())


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

    logger.info(f"[main] Started {frmb_gui.__name__} v{frmb_gui.__version__}")
    frmb_gui.config.__debugging__()
    launch_gui()


if __name__ == "__main__":
    main()

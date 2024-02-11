import argparse
import sys

import frmb_gui


class CLI:
    """
    Retrieve user argument provided in the command line as convenient python object.

    Args:
        argv: command line arguments. Use ``sys.argv`` if not provided.
    """

    def __init__(self, argv=None):
        argv = argv or sys.argv[1:]
        self.parser = argparse.ArgumentParser(
            frmb_gui.constants.name,
            description="GUI tool to customize the Windows context-menu using the registry.",
        )
        self.parser.add_argument("--debug", action="store_true")
        self.parser.add_argument("--devmode", action="store_true")
        self.parsed = self.parser.parse_args(argv)

    @property
    def debug(self) -> bool:
        return self.parsed.debug

    @property
    def devmode(self) -> bool:
        return self.parsed.devmode

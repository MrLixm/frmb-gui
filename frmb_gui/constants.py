"""
Definition of the constant variables.

Lowest level module.
"""

import sys


__version__ = f"0.1.0"

name = "frmb"
"""
petty name of the application
"""

organisation = "pyco"
"""
upper entity managing this package
"""

vcs_url = "https://github.com/MrLixm/frmb-gui"
"""
url of the remote VCS repository for this package.
"""

is_frozen: bool = bool(getattr(sys, "frozen", False))
"""
True if the module is being executed from a frozen pyinstaller executable.
"""

documentation_url = "https://mrlixm.github.io/frmb_gui/"
"""
url of the online documentation
"""

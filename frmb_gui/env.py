"""
Definition of the supported environment variables that can affect the application.
"""

import dataclasses
import os
from typing import Optional


@dataclasses.dataclass
class EnvironmentVariable:
    name: str

    def get(self, default: Optional[str] = None):
        return os.getenv(self.name, default)


ENVPREFIX = "FRMB"


debug = EnvironmentVariable(f"{ENVPREFIX}_DEBUG")
"""
Enable the debug mode for the application
"""

developer_mode = EnvironmentVariable(f"{ENVPREFIX}_DEV_MODE")
"""
Enable the developer mode for the application. This enable features only useful for developers.
"""

platform_fake = EnvironmentVariable(f"{ENVPREFIX}_PLATFORM_FAKE")
"""
string is one of sys.platform. Used to fake a specific plateform during build.
"""

dependencies_list = EnvironmentVariable(f"{ENVPREFIX}_DEPENDENCIES")
"""
static list of python dependencies used for when the app is frozen.
"""

build_id = EnvironmentVariable(f"{ENVPREFIX}_BUILD_ID")
"""
Set during build by pyinstaller.
"""


def get_all_variables() -> list["EnvironmentVariable"]:
    """
    Get all environment variables used by this application.
    """
    return [
        debug,
        platform_fake,
        dependencies_list,
        build_id,
    ]


def get_variables_as_dict() -> dict[str, str]:
    """
    Get all environment variables used by this application as a dict of {name: value}
    """
    return {variable.name: variable.get() for variable in get_all_variables()}

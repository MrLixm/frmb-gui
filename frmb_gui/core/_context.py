import json
import sys
import urllib.parse

# TODO find non-deprecated alternative
import pkg_resources
import platform

import frmb_gui


def get_runtime_dependencies() -> list[tuple[str, str]]:
    """
    Get all the installed packages/library in the current python environment.

    If we are in a frozen application context, the dependencies must come from
    an environement variable.

    Returns:
        list of [packageName, version]
    """
    env_var = frmb_gui.env.dependencies_list
    if frmb_gui.constants.is_frozen:
        dependencies_str = env_var.get()
        if not dependencies_str:
            return [
                (
                    f"Missing env variable {env_var.name}",
                    "ERROR",
                )
            ]
        dependencies_list = dependencies_str.split(";")
        dependencies = [
            tuple(dependency.split(":", 1)) for dependency in dependencies_list
        ]
        return dependencies

    dependencies = list()
    for pkg in pkg_resources.working_set:
        dependencies.append((pkg.project_name, pkg.version))

    dependencies.append(("python", platform.python_version()))
    return dependencies


def get_runtime_context() -> str:
    """
    Return the execution context to help at troubleshooting.

    This is a human readble string.
    """
    env = [
        f"{var_name}={var_value}"
        for var_name, var_value in frmb_gui.env.get_variables_as_dict().items()
    ]
    out = (
        f"{frmb_gui.constants.name}: {frmb_gui.__version__}\n"
        f"platform: {platform.platform()}\n"
        f"frozen: {frmb_gui.constants.is_frozen}\n"
        f"env: {json.dumps(env, indent=4, default=str)}\n"
        f"sys.argv: {json.dumps(sys.argv, indent=4, default=str)}"
    )
    return out


def get_context_reporting_url(context: str) -> str:
    """
    Convert the given context to an url allowing to report an issue in the issue-tracker
    of the application.

    Args:
        context: usually acuired via :func:`get_runtime_context`

    Returns:
        a valid web-url
    """
    url_base = f"{frmb_gui.constants.vcs_url}/issues/new"

    issue_description = (
        f"# description\n"
        f"\nwrite a clear description of your issue here\n"
        f"\n# context\n\n```\n{context}\n```\n"
    )
    issue_description_safe = urllib.parse.quote_plus(issue_description)

    url = f"{url_base}?body={issue_description_safe}"
    return url

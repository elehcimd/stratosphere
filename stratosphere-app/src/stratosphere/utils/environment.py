import platform
import sys
from types import ModuleType
from typing import Callable, Dict

import pkg_resources
from IPython.core.getipython import get_ipython

catch_exceptions = (FileNotFoundError, AttributeError)


def is_tty():
    """Check if code is running inside a terminal.

    Returns:
        bool: True if in terminal.
    """
    return sys.stdout.isatty()


def is_colab() -> bool:
    """Detect if in Google Colab

    Returns:
        bool: True if in Colab
    """
    return "google.colab" in sys.modules


def is_pyodide() -> bool:
    """Detect if in Pyodide (JupyterLite, ...)

    Returns:
        bool: True if in Pyodide
    """
    return "pyodide" in sys.modules


def is_notebook() -> bool:
    """Returns True if executed from within a Notebook (IPython)

    Returns:
        bool: True if in Notebook
    """

    # Colab returns "Shell"
    # Jupyter Lab returns "ZMQInteractiveShell"
    # JypyterLite returns "Interpreter"
    return get_ipython() is not None and get_ipython().__class__.__name__ in [
        "ZMQInteractiveShell",
        "Shell",
        "Interpreter",
    ]


def get_version_packages() -> Dict:
    """Return the version of the installed packages. E.g., {"colorama": "1.2.3", ....}

    Returns:
        dict: Dict of installed package versions
    """
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}


def try_callable(func: Callable) -> str:
    """Try to call the function. If it fails, return an empty string.

    Args:
        func (Callable): Function to call.

    Returns:
        str: Output of the function, if available.
    """
    try:
        value = func()
        if value is None:
            return ""
        else:
            return value
    except catch_exceptions:
        return ""


def try_module(module: ModuleType, method_name: str) -> str:
    """Try to call a module function. If  it fails, return an empty string.

    Args:
        module (ModuleType): Module
        method_name (str): Method name

    Returns:
        str: Output of the function, if available.
    """
    try:
        value = getattr(module, method_name)
        if callable(value):
            return try_callable(value)
        else:
            return value
    except catch_exceptions:
        return ""


# Not including uname, as it might disclose part of the network name address, and this could be a security issue.
def get_environment() -> Dict:
    """Return a summary of the Python environment, including installed packages, Python, platform, system versions.

    Returns:
        Dict: An overview of the Python environment.
    """
    return {
        "pkgs_version": try_callable(get_version_packages),
        "platform": {
            "machine": try_module(platform, "machine"),
            "mac_ver": try_module(platform, "mac_ver"),
            "libc_ver": try_module(platform, "libc_ver"),
            "system": try_module(platform, "system"),
            "release": try_module(platform, "release"),
            "java_ver": try_module(platform, "java_ver"),
            "win32_ver": try_module(platform, "win32_ver"),
            "win32_edition": try_module(platform, "win32_edition"),
            "linux_distribution": try_module(platform, "linux_distribution"),  # available in Python 3.7
            "freedesktop_os_release": try_module(platform, "freedesktop_os_release"),  # available in Python 3.10
            "uname": try_module(platform, "uname"),
            "sys_version": try_module(sys, "version"),
            "is_colab": is_colab(),
            "is_pyodide": is_pyodide(),
            "is_tty": is_tty(),
            "is_notebook": is_notebook(),
        },
    }

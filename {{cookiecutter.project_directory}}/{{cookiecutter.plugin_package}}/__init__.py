import os  # noqa F401

from qgis.gui import QgisInterface

from .qgis_plugin_tools.infrastructure.debugging import setup_pydevd

if os.environ.get("QGIS_PLUGIN_USE_DEBUGGER") == "pydevd":
    if (
        os.environ.get("IN_TESTS", "0") != "1"
        and os.environ.get("QGIS_PLUGIN_IN_CI", "0") != "1"
    ):
        setup_pydevd()


def classFactory(iface: QgisInterface):  # noqa N802
    from .plugin import Plugin

    return Plugin(iface)

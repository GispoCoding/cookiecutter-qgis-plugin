import os

from qgis.gui import QgisInterface

from {{cookiecutter.plugin_package}}.qgis_plugin_tools.infrastructure.debugging import setup_pydevd  # noqa E501

if os.environ.get("QGIS_PLUGIN_USE_DEBUGGER") == "pydevd":
    if (
        os.environ.get("IN_TESTS", "0") != "1"
        and os.environ.get("QGIS_PLUGIN_IN_CI", "0") != "1"
    ):
        setup_pydevd()


def classFactory(iface: QgisInterface):  # noqa N802
    from {{cookiecutter.plugin_package}}.plugin import Plugin

    return Plugin(iface)

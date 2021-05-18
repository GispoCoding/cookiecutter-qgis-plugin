# type: ignore
# flake8: noqa ANN201
"""
This class contains fixtures and common helper function to keep the test files shorter
"""
from typing import Tuple

import pytest
from PyQt5.QtWidgets import QWidget
from qgis.core import QgsApplication
from qgis.gui import QgsMapCanvas

from ..qgis_plugin_tools.testing.qgis_interface import QgisInterface
from ..qgis_plugin_tools.testing.utilities import get_qgis_app


@pytest.fixture(autouse=True, scope="session")
def initialize_qgis() -> Tuple[QgsApplication, QgsMapCanvas, QgisInterface, QWidget]:
    """ Initializes qgis session for all tests """
    yield get_qgis_app()


@pytest.fixture(scope="session")
def qgis_app(initialize_qgis) -> QgsApplication:
    return initialize_qgis[0]


@pytest.fixture(scope="session")
def canvas(initialize_qgis) -> QgsMapCanvas:
    return initialize_qgis[1]


@pytest.fixture(scope="session")
def iface(initialize_qgis) -> QgisInterface:
    return initialize_qgis[2]


@pytest.fixture(scope="session")
def qgis_parent(initialize_qgis) -> QWidget:
    return initialize_qgis[3]


@pytest.fixture(scope="function")
def new_project(iface) -> None:
    """
    Initializes new QGIS project by removing layers and relations etc.
    """
    yield iface.newProject()

# type: ignore
# flake8: noqa ANN201
"""
This class contains fixtures and common helper function to keep the test files shorter
"""

import pytest

from ..qgis_plugin_tools.testing.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


@pytest.fixture(scope="function")
def new_project() -> None:
    """Initializes new QGIS project by removing layers and relations etc."""  # noqa E501
    yield IFACE.newProject()

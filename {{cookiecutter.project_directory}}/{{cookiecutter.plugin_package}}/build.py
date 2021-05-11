#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
from typing import List

from qgis_plugin_tools.infrastructure.plugin_maker import PluginMaker

"""
#################################################
# Edit the following to match the plugin
#################################################
"""

py_files = [fil for fil in glob.glob("**/*.py", recursive=True) if "test/" not in fil]
locales = ["fi"]
profile = "default"
ui_files = list(glob.glob("**/*.ui", recursive=True))
resources = list(glob.glob("**/*.qrc", recursive=True))
extra_dirs = ["resources"]
compiled_resources: List[str] = []

PluginMaker(
    py_files=py_files,
    ui_files=ui_files,
    resources=resources,
    extra_dirs=extra_dirs,
    compiled_resources=compiled_resources,
    locales=locales,
    profile=profile,
)

# Cookiecutter QGIS Plugin

![CI](https://github.com/GispoCoding/cookiecutter-qgis-plugin/workflows/CI/badge.svg)
![License](https://img.shields.io/github/license/GispoCoding/cookiecutter-qgis-plugin)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[Cookiecutter](https://www.cookiecutter.io) template for a [QGIS](https://qgis.org/) plugin.

This template makes it easy to create a new QGIS plugin project with a modern development environment.

## Usage

Plugin generation is supported with Python 3.8 or newer.

### Prerequisites

The template is built using [Cookiecutter](https://www.cookiecutter.io), so you must have it installed.

#### Install Cookiecutter with pipx

The recommended way to install Cookiecutter (and other Python cli tools) is to install it with [pipx](https://pypa.github.io/pipx/). Pipx will install the application in a isolated environment and make it available as a command line utility. To install `pipx` follow the instructions from https://github.com/pypa/pipx#install-pipx.

```shell
pipx install cookiecutter
```

#### Install Cookiecutter to your current python environment

```shell
pip install cookiecutter
```

### Create a new plugin project

Creating a new plugin project with Cookiecutter creates a new folder for the project so navigate to the desired parent directory and use the following command. Run Cookiecutter with this repository as the template. This command will set up your project based on the provided template

```shell
cookiecutter https://github.com/GispoCoding/cookiecutter-qgis-plugin
```

## Development

You should develop this template using virtual python environment. This way you can install development dependencies and test the template without affecting your global python environment.

```shell
# Create a virtual python environment named .venv
python -m venv .venv
# Activate the virtual environment
source .venv/bin/activate # On Windows run: .venv/Scripts/activate
# Install pip-tools dependency manager
pip install pip-tools
# Install/sync development dependencies
pip-sync  # This will sync dependencies in the current environment to mach the ones in requirements.txt
```

### Update dependencies

Dependencies are pinned to a exact versions so that tests are run in a reproduceable environment also on CI.

```shell
# Edit requirements.in

# Compile requirements.in to requirements.txt
pip-compile --resolver=backtracking
# Sync dependencies
pip-sync

# Commit requirements.in and requirements.txt
git add requirements.in requirements.txt
git commit -m "Update development dependencies"
```

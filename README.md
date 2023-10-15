# Cookiecutter QGIS Plugin
![CI](https://github.com/GispoCoding/cookiecutter-qgis-plugin/workflows/CI/badge.svg)
![License](https://img.shields.io/github/license/GispoCoding/cookiecutter-qgis-plugin)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


Powered by Cookiecutter, Cookiecutter QGIS Plugin is a framework for making the start of QGIS plugin development easy.

## Usage

Python >= 3.8 is required.

First, get Cookiecutter and pip-tools.
```shell
$ pip install --user cookiecutter pip-tools
```

Run cookiecutter giving this template repository as an argument. Run the command in the parent folder where you want the project folder to be created.
```shell
$ cookiecutter https://github.com/GispoCoding/cookiecutter-qgis-plugin
```

You'll be asked some information which kind of a configuration you want to use with your plugin.

## Development

You should develop this template using virtual python environment. This way you can run tests in an isolated environment.

```bash
$ python -m venv .venv
$ source .venv/bin/activate # On Windows .venv/Scripts/activate
$ pip install -r requirements.txt
```

### Update dependencies
Dependencies are pinned to a exact versions so that tests are run in a reproduceable environment also on CI.

```bash
# install pip-tools
$ pip install pip-tools

# edit requirements.in

# compile requirements.in to requirements.txt
$ pip-compile --resolver=backtracking
# sync dependencies
$ pip-sync

# commit requirements.in and requirements.txt
$ git add requirements.in requirements.txt
$ git commit -m "update dependencies"
```

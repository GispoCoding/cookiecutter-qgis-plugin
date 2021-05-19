# Cookiecutter QGIS Plugin

Powered by Cookiecutter, Cookiecutter QGIS Plugin is a framework for making the start of QGIS plugin development easy.

## Usage

First, get Cookiecutter.
```shell
$ pip install cookiecutter
```

Run cookiecutter giving this template repository as an argument. Run the command in the parent folder where you want the project folder to be created.
```shell
$ cookiecutter https://github.com/GispoCoding/cookiecutter-qgis-plugin
```

You'll be asked some information which kind of a configuration you want to use with your plugin.

## Development

You should develop this template using virtual python environment. This way you can run tests in an isolated environment.

```bash
$ python -m venv env
$ source env/bin/activate # On Windows ./env/Scripts/activate
$ pip install -r requirements.txt
```

### Update dependencies
Dependencies are pinned to a exact versions so that tests are run in a reproducable environment also on CI.

```bash
# install pip-tools
$ pip install pip-tools

# edit requirements.in

# compile requirements.in to requirements.txt
$ pip-compile
# sync dependencies
$ pip-sync

# commit requirements.in and requirements.txt
$ git add requirements.in requirements.txt
$ git commit -m "update dependencies"
```

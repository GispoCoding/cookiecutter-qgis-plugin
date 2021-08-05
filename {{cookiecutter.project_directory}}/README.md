# {{cookiecutter.plugin_name}}
![tests](https://github.com/{{cookiecutter.git_repo_organization}}/{{cookiecutter.project_directory}}/workflows/Tests/badge.svg)
[![codecov.io](https://codecov.io/github/{{cookiecutter.git_repo_organization}}/{{cookiecutter.project_directory}}/coverage.svg?branch=main)](https://codecov.io/github/{{cookiecutter.git_repo_organization}}/{{cookiecutter.project_directory}}?branch=main)
![release](https://github.com/{{cookiecutter.git_repo_organization}}/{{cookiecutter.project_directory}}/workflows/Release/badge.svg)
{%- if cookiecutter.license == "GPL2" %}
[![GPLv2 license](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
{%- elif cookiecutter.license == "GPL3" %}
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
{% endif %}
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Development

Refer to [development](docs/development.md) for developing this QGIS3 plugin.

## License
This plugin is licenced with
{%- if cookiecutter.license == "GPL2" -%}
[GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
{%- elif cookiecutter.license == "GPL3" -%}
[GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.html)
{% endif %}

See [LICENSE](LICENSE) for more information.

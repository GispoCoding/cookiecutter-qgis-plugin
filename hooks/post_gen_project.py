from __future__ import annotations

import logging
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

ALL_TEMP_FOLDERS = ("licenses", "plugin_templates")
QGIS_PLUGIN_TOOLS_SPECIFIC_FILES = (
    "{{cookiecutter.plugin_package}}/build.py",
    "test/test_plugin.py",
)


def is_true(value: str) -> bool:
    return value == "True"


class Colors:
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def warn(message: str) -> None:
    print(f"{Colors.WARNING}Warning: {message}{Colors.ENDC}")


def _run(args: list[str]) -> None:
    try:
        logger.info('Running command "%s"', " ".join(args))
        subprocess.run(
            args,
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        warn(f'Running command "{" ".join(args)}" failed.')


def _remove_dir(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)


def _remove_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


def git_init():
    _run(["git", "init"])


def add_plugin_tools():
    _run(
        [
            "git",
            "submodule",
            "add",
            "https://github.com/GispoCoding/qgis_plugin_tools",
            "{{cookiecutter.plugin_package}}/qgis_plugin_tools",
        ]
    )
    build_script = Path("{{cookiecutter.plugin_package}}/build.py")
    build_script.chmod(build_script.stat().st_mode | stat.S_IXUSR)


def remove_plugin_tools():
    for file in QGIS_PLUGIN_TOOLS_SPECIFIC_FILES:
        _remove_file(file)


def add_remote():
    _run(["git", "remote", "add", "origin", "{{cookiecutter.git_repo_url}}"])


def write_dependencies():
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "piptools",
                "compile",
                "--upgrade",
                "-o",
                "requirements-dev.txt",
                "requirements-dev.in",
            ],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        warn(
            "Updating dependencies failed. Do you have the pip-tools installed? "
            'Run "pip-compile requirements-dev.in" manually in your plugin folder.'
        )


def remove_temp_folders():
    for folder in ALL_TEMP_FOLDERS:
        _remove_dir(folder)


def _remove_ruff_defaults():
    _remove_file("ruff_defaults.toml")


def remove_vscode_files():
    _remove_dir(".vscode")
    _remove_file("{{cookiecutter.project_directory}}.code-workspace")


def remove_github_files():
    _remove_dir(".github")


def remove_gitlab_files():
    _remove_file(".gitlab-ci.yml")


def remove_jinja_extensions():
    jinja_files = Path(".").rglob(
        "*.j2",
    )
    for file in jinja_files:
        os.rename(file, file.with_suffix(""))


def remove_processing_files():
    _remove_dir("{{cookiecutter.project_directory}}/processing")


def main():
    remove_jinja_extensions()

    git_init()

    if is_true("{{ cookiecutter.use_qgis_plugin_tools }}"):
        add_plugin_tools()
    else:
        remove_plugin_tools()

    if not is_true("{{ cookiecutter.add_vscode_config }}"):
        remove_vscode_files()

    if "{{ cookiecutter.git_repo_url }}":
        add_remote()

    if "{{ cookiecutter.ci_provider }}".lower() != "github":
        remove_github_files()

    if not is_true("{{ cookiecutter.include_processing }}"):
        remove_processing_files()

    if "{{ cookiecutter.linting }}".lower() != "hatch":
        _remove_ruff_defaults()

    remove_temp_folders()
    write_dependencies()


if __name__ == "__main__":
    main()

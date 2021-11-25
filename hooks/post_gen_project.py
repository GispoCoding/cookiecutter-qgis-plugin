import os
import shutil
import subprocess

ALL_TEMP_FOLDERS = ("licenses", "plugin_templates")
QGIS_PLUGIN_TOOLS_SPECIFIC_FILES = (
    "{{cookiecutter.plugin_package}}/build.py",
    "test/test_plugin.py",
)


def _remove_dir(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)


def _remove_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


def git_init():
    subprocess.call(["git", "init"])


def add_plugin_tools():
    subprocess.call(
        [
            "git",
            "submodule",
            "add",
            "https://github.com/GispoCoding/qgis_plugin_tools",
            "{{cookiecutter.plugin_package}}/qgis_plugin_tools",
        ]
    )


def remove_plugin_tools():
    for file in QGIS_PLUGIN_TOOLS_SPECIFIC_FILES:
        _remove_file(file)


def add_remote():
    subprocess.call(["git", "remote", "add", "origin", "{{cookiecutter.git_repo_url}}"])


def remove_temp_folders():
    for folder in ALL_TEMP_FOLDERS:
        _remove_dir(folder)


def remove_vscode_files():
    _remove_dir(".vscode")
    _remove_file("{{cookiecutter.project_directory}}.code-workspace")


def remove_github_files():
    _remove_dir(".github")


def remove_gitlab_files():
    _remove_file(".gitlab-ci.yml")


def main():
    git_init()

    if "{{ cookiecutter.use_qgis_plugin_tools }}".lower() != "n":
        add_plugin_tools()
    else:
        remove_plugin_tools()

    if "{{ cookiecutter.add_vscode_config }}".lower() == "n":
        remove_vscode_files()

    if "{{ cookiecutter.git_repo_url }}":
        add_remote()

    if "{{ cookiecutter.ci_provider }}".lower() != "github":
        remove_github_files()

    remove_temp_folders()


if __name__ == "__main__":
    main()

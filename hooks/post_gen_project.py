import os
import shutil
import subprocess


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


def add_remote():
    subprocess.call(["git", "remote", "add", "origin", "{{cookiecutter.git_repo_url}}"])


def remove_pycharm_files():
    pass


def remove_vscode_files():
    _remove_dir(".vscode")


def remove_github_files():
    _remove_dir(".github")


def remove_gitlab_files():
    _remove_file(".gitlab-ci.yml")


def main():
    git_init()

    if "{{ cookiecutter.use_qgis_plugin_tools }}".lower() != "n":
        add_plugin_tools()

    if "{{ cookiecutter.add_pycharm_config }}".lower() == "n":
        remove_pycharm_files()

    if "{{ cookiecutter.add_vscode_config }}".lower() == "n":
        remove_vscode_files()

    if "{{ cookiecutter.git_repo_url }}":
        add_remote()

    if "{{ cookiecutter.version_control }}".lower() != "github":
        remove_github_files()

    if "{{ cookiecutter.version_control }}".lower() != "gitlab":
        remove_gitlab_files()


if __name__ == "__main__":
    main()

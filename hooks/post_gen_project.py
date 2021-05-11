
import subprocess

def git_init():
    subprocess.call(['git', 'init'])

def add_plugin_tools():
    subprocess.call(['git', 'submodule', 'add', 'https://github.com/GispoCoding/qgis_plugin_tools', '{{cookiecutter.plugin_package}}/qgis_plugin_tools'])

def remove_pycharm_files():
    pass

def main():
    git_init()
    add_plugin_tools()

    if "{{ cookiecutter.add_pycharm_config }}".lower() == "n":
        remove_pycharm_files()


if __name__ == '__main__':
    main()

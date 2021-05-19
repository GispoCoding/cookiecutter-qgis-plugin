import os
import re
import subprocess

import pytest
from binaryornot.check import is_binary
from cookiecutter.exceptions import FailedHookException

PATTERN = r"{{(\s?cookiecutter)[.](.*?)}}"
RE_OBJ = re.compile(PATTERN)


@pytest.fixture
def context():
    return {
        "plugin_name": "My QGIS plugin",
        "project_directory": "my-qgis-plugin",
        "plugin_package": "myqgisplugin",
        "version_control": "GitHub",
        "git_repo_organization": "my-org",
        "git_repo_url": "https://github.com/my-org/my-qgis-plugin",
        "add_vscode_config": "n",
        "add_pycharm_config": "n",
        "license": "GPL2",
        "use_qgis_plugin_tools": "n",
    }


SUPPORTED_COMBINATIONS = [
    {"version_control": "GitHub"},
    {"version_control": "GitLab"},
    {"version_control": "None"},
    {"add_vscode_config": "y"},
    {"add_vscode_config": "n"},
    {"add_pycharm_config": "y"},
    {"add_pycharm_config": "n"},
    {"license": "GPL2"},
    {"license": "GPL3"},
]

UNSUPPORTED_COMBINATIONS = []


def _fixture_id(ctx):
    """Helper to get a user friendly test name from the parametrized context."""
    return "-".join(f"{key}:{value}" for key, value in ctx.items())


def build_files_list(root_dir):
    """Build a list containing absolute paths to the generated files."""
    return [
        os.path.join(dirpath, file_path)
        for dirpath, subdirs, files in os.walk(root_dir)
        for file_path in files
    ]


def check_paths(paths):
    """Method to check all paths have correct substitutions."""
    # Assert that no match is found in any of the files
    for path in paths:
        if is_binary(path):
            continue

        for line in open(path, "r"):
            match = RE_OBJ.search(line)
            assert match is None, f"cookiecutter variable not replaced in {path}"


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_project_generation(cookies, context, context_override):
    """Test that project is generated and fully rendered."""

    result = cookies.bake(extra_context={**context, **context_override})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == context["project_directory"]
    assert result.project.isdir()

    paths = build_files_list(str(result.project))
    assert paths
    check_paths(paths)


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_flake8_passes(cookies, context, context_override):
    """Generated project should pass flake8."""
    baked_project = cookies.bake(extra_context={**context, **context_override})
    try:
        subprocess.check_output(
            ["flake8"],
            cwd=str(baked_project.project),
            timeout=20,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        pytest.fail(exc.output)
    except subprocess.TimeoutExpired:
        pytest.fail("Flake8 timeouted")


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_black_passes(cookies, context, context_override):
    """Generated project should pass black."""
    baked_project = cookies.bake(extra_context={**context, **context_override})

    try:
        subprocess.check_output(
            ["black", "--check", "--diff", "./"],
            cwd=str(baked_project.project),
            timeout=20,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        pytest.fail(exc.output)
    except subprocess.TimeoutExpired:
        pytest.fail("black timeouted")


@pytest.mark.parametrize("package_name", ["invalid name", "1plugin"])
def test_invalid_package_name(cookies, context, package_name):
    """Invalid package name should fail in pre-generation hook."""
    context.update({"plugin_package": package_name})

    result = cookies.bake(extra_context=context)

    assert result.exit_code != 0
    assert isinstance(result.exception, FailedHookException)


@pytest.mark.parametrize("invalid_context", UNSUPPORTED_COMBINATIONS)
def test_error_if_incompatible(cookies, context, invalid_context):
    """It should not generate project an incompatible combination is selected."""
    context.update(invalid_context)
    result = cookies.bake(extra_context=context)

    assert result.exit_code != 0
    assert isinstance(result.exception, FailedHookException)

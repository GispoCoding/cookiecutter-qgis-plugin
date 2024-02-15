from __future__ import annotations

import copy
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest
from cookiecutter.exceptions import FailedHookException, UndefinedVariableInTemplate

if TYPE_CHECKING:
    from pytest_cookies.plugin import Cookies, Result

LONG_PACKAGE_NAME = "hyperextralongpackagenametomessupimportformatting"


@pytest.fixture(scope="session")
def session_context():
    return {
        "plugin_name": "My QGIS plugin",
        "project_directory": "my-qgis-plugin",
        "plugin_package": "plugin",
        "git_repo_organization": "my-org",
        "git_repo_url": "https://github.com/my-org/my-qgis-plugin",
        "ci_provider": "GitHub",
        "add_vscode_config": "n",
        "add_pycharm_config": "n",
        "license": "GPL2",
        "use_qgis_plugin_tools": "n",  # to make test run faster
    }


@pytest.fixture
def context(session_context: dict[str, str]):
    return copy.deepcopy(session_context)


SUPPORTED_COMBINATIONS = [
    {"plugin_package": LONG_PACKAGE_NAME},
    {"ci_provider": "GitHub"},
    {"ci_provider": "None"},
    {"add_vscode_config": "y"},
    {"add_vscode_config": "n"},
    {"add_pycharm_config": "y"},
    {"add_pycharm_config": "n"},
    {"license": "GPL2"},
    {"license": "GPL3"},
]

UNSUPPORTED_COMBINATIONS = [
    {"license": "other"},
]


def _fixture_id(ctx: dict[str, str]):
    """Helper to get a user friendly test name from the parametrized context."""
    return "-".join(f"{key}:{value}" for key, value in ctx.items())


@pytest.fixture(scope="session", params=SUPPORTED_COMBINATIONS, ids=_fixture_id)
def baked_project(
    cookies_session: Cookies,
    session_context: dict[str, str],
    request: pytest.FixtureRequest,
) -> Result:
    context_override = request.param
    baked_project = cookies_session.bake(extra_context={**session_context, **context_override})
    if isinstance(baked_project.exception, UndefinedVariableInTemplate):
        print(baked_project.exception.message)  # noqa: T201
        print(f"Error message: {baked_project.exception.error.message}")  # noqa: T201
        sys.exit(1)

    return baked_project


def test_project_generation(baked_project: Result):
    """Test that project is generated and fully rendered."""

    assert baked_project.project_path.name == baked_project.context["project_directory"]
    assert baked_project.project_path.is_dir()


def run_cli_command(command: str, cwd: str):
    cmd = command.split()
    try:
        subprocess.check_output(
            cmd,
            cwd=cwd,
            timeout=20,
            universal_newlines=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        pytest.fail(exc.output)
    except subprocess.TimeoutExpired:
        pytest.fail("Command timeouted")


def test_ruff_linting_passes(baked_project: Result):
    """Generated project should pass ruff check."""

    if baked_project.context["plugin_package"] == LONG_PACKAGE_NAME:
        pytest.xfail(reason="long package names makes imports to be reformatted. TODO: fix")

    run_cli_command("ruff check .", cwd=str(baked_project.project_path))


def test_ruff_formatting_passes(baked_project: Result):
    """Generated project should pass ruff formatting."""

    if baked_project.context["plugin_package"] == LONG_PACKAGE_NAME:
        pytest.xfail(reason="long package names makes imports to be reformatted. TODO: fix")

    run_cli_command("ruff format --check .", cwd=str(baked_project.project_path))


@pytest.mark.parametrize("package_name", ["invalid name", "1plugin"])
def test_invalid_package_name(cookies: Cookies, context: dict[str, str], package_name: str):
    """Invalid package name should fail in pre-generation hook."""
    context.update({"plugin_package": package_name})

    result = cookies.bake(extra_context=context)

    assert result.exit_code != 0
    assert isinstance(result.exception, FailedHookException)


@pytest.mark.parametrize("invalid_context", UNSUPPORTED_COMBINATIONS)
def test_error_if_incompatible(cookies: Cookies, context: dict[str, str], invalid_context: dict[str, str]):
    """It should not generate project an incompatible combination is selected."""
    context.update(invalid_context)
    result = cookies.bake(extra_context=context)

    assert result.exit_code != 0
    assert isinstance(result.exception, FailedHookException)

from __future__ import annotations

import copy
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest
from cookiecutter.exceptions import FailedHookException, UndefinedVariableInTemplate

if TYPE_CHECKING:
    from pathlib import Path

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
        "ci_provider": "None",
        "add_vscode_config": False,
        "include_processing": False,
        "license": "GPL2",
        "use_qgis_plugin_tools": False,  # to make test run faster
    }


@pytest.fixture
def context(session_context: dict[str, str]):
    return copy.deepcopy(session_context)


SUPPORTED_COMBINATIONS = [
    {},
    {"plugin_package": LONG_PACKAGE_NAME},
    {"ci_provider": "None"},
    {"add_vscode_config": True},
    {"include_processing": True},
    {"use_qgis_plugin_tools": True},
    {"license": "GPL3"},
]

UNSUPPORTED_COMBINATIONS = [
    {"license": "other"},
]


def _fixture_id(ctx: dict[str, str]):
    """Helper to get a user friendly test name from the parametrized context."""
    if not ctx:
        return "default"
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

    assert baked_project.exit_code == 0
    assert baked_project.exception is None

    assert baked_project.project_path.name == baked_project.context["project_directory"]
    assert baked_project.project_path.is_dir()


def run_cli_command(args: list[str], cwd: str):
    try:
        subprocess.check_output(
            args,
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

    run_cli_command([sys.executable, "-m", "ruff", "check", "."], cwd=str(baked_project.project_path))


def test_ruff_formatting_passes(baked_project: Result):
    """Generated project should pass ruff formatting."""

    if baked_project.context["plugin_package"] == LONG_PACKAGE_NAME:
        pytest.xfail(reason="long package names makes imports to be reformatted. TODO: fix")

    run_cli_command([sys.executable, "-m", "ruff", "format", "--check", "."], cwd=str(baked_project.project_path))


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


class TestOptInFeaturesRemoved:
    @pytest.fixture(scope="class")
    def baked_project(self, cookies_session: Cookies) -> Result:
        extra_context = {
            "plugin_name": "My QGIS plugin",
            "ci_provider": "None",
            "add_vscode_config": False,
            "include_processing": False,
            "license": "GPL2",
            "use_qgis_plugin_tools": False,
        }
        return cookies_session.bake(extra_context=extra_context)

    @pytest.fixture(scope="class")
    def project_path(self, baked_project: Result) -> Path:
        assert baked_project.project_path
        return baked_project.project_path

    def test_no_vscode(self, baked_project: Result, project_path: Path) -> None:
        assert not (project_path / f"{baked_project.context['project_directory']}.code-workspace").exists()

    def test_no_github(self, project_path: Path) -> None:
        assert not (project_path / ".github").is_dir()

    def test_no_processing(self, baked_project: Result, project_path: Path) -> None:
        assert not (project_path / f"{baked_project.context['plugin_package']}_processing").is_dir()

    def test_no_plugin_tools(self, baked_project: Result, project_path: Path) -> None:
        assert not (project_path / baked_project.context["plugin_package"] / "qgis_plugin_tools").is_dir()

    def test_no_licenses_dir(self, project_path: Path) -> None:
        assert not (project_path / "licenses").is_dir()


class TestOptInFeaturesIncluded:
    @pytest.fixture(scope="class")
    def baked_project(self, cookies_session: Cookies) -> Result:
        extra_context = {
            "plugin_name": "My QGIS plugin",
            "ci_provider": "GitHub",
            "add_vscode_config": True,
            "include_processing": True,
            "license": "GPL2",
            "use_qgis_plugin_tools": True,
        }
        return cookies_session.bake(extra_context=extra_context)

    @pytest.fixture(scope="class")
    def project_path(self, baked_project: Result) -> Path:
        assert baked_project.project_path
        return baked_project.project_path

    def test_has_vscode(self, baked_project: Result, project_path: Path) -> None:
        assert (project_path / f"{baked_project.context['project_directory']}.code-workspace").exists()

    def test_has_github(self, project_path: Path) -> None:
        assert (project_path / ".github").is_dir()

    def test_has_processing(self, baked_project: Result, project_path: Path) -> None:
        processing_directory = (
            project_path
            / baked_project.context["plugin_package"]
            / f"{baked_project.context['plugin_package']}_processing"
        )
        assert processing_directory.is_dir()

    def test_has_plugin_tools(self, baked_project: Result, project_path: Path) -> None:
        assert (project_path / baked_project.context["plugin_package"] / "qgis_plugin_tools").is_dir()

    def test_no_licenses_dir(self, project_path: Path) -> None:
        assert not (project_path / "licenses").is_dir()

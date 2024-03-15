# SPDX-FileCopyrightText: 2024 Gispo Ltd. <info@gispo.fi>
#
# SPDX-License-Identifier: MIT

# ruff: noqa: T201

"""
This is a tool for creating a virtual environment for QGIS plugin development.

Originated from https://github.com/GispoCoding/qgis-venv-creator

Usage:
python create_qgis_venv.py [--help] [--venv-parent <path-to-venv-parent-directory>] [--venv-name <venv-name>]
"""


from __future__ import annotations

import argparse
import logging
import os
import platform
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator, Protocol, TypedDict, cast

if TYPE_CHECKING:

    class CliArgsType(TypedDict, total=False):
        qgis_installation: Path | None
        qgis_installation_search_path_pattern: str | None
        venv_parent: Path | None
        venv_name: str | None
        python_executable: Path | None
        debug: bool

    class SupportsVenvCreation(Protocol):
        @classmethod
        def create_venv(cls, *args: Any, **kwargs: Any) -> Path:
            ...

        @staticmethod
        def cli_arguments() -> list[CliArg]:
            ...


__version__ = "0.1.0"

cli_args: CliArgsType = {}


class CliArg:
    """Command line argument definition to be passed to argparse.ArgumentParser.add_argument()

    ```py
    import argparse

    parser = argparse.ArgumentParser()

    cli_arg = CliArg("--foo", help="Foo")
    parser.add_argument(*cli_arg.args, **cli_arg.kwargs)

    args = parser.parse_args(["--foo", "bar"])
    assert args.foo == "bar"
    ```
    """

    def __init__(self, *args: str, **kwargs: Any):
        self.args = args
        self.kwargs = kwargs


logger = logging.getLogger(__name__)


class VenvCreationError(RuntimeError):
    def __init__(self):
        super().__init__("Failed to create virtual environment")


class InvalidPythonExecutableError(RuntimeError):
    def __init__(self, executable_path: Path | None):
        super().__init__(f"{executable_path} is not a valid Python executable.")


class InvalidQgisPathError(RuntimeError):
    def __init__(self, qgis_installation: Path | None):
        super().__init__(f"{qgis_installation} is not a valid QGIS path.")


class VenvParentDirectoryNotExistsError(RuntimeError):
    def __init__(self, venv_directory: Path):
        super().__init__(f"Virtual environment directory {venv_directory} does not exist.")


class GlobPatternError(ValueError):
    def __init__(self, pattern: str):
        super().__init__(f"Invalid glob pattern: {pattern}. Wildcard in the first directory part is not supported.")


class UnsupportedPlatformError(RuntimeError):
    def __init__(self, platform: str):
        super().__init__(f"Unsupported platform: {platform}.")


def _is_valid_python_executable(python_executable: Path | None) -> bool:
    """Check if the given path is a valid Python executable."""

    return python_executable is not None and python_executable.exists() and os.access(python_executable, os.X_OK)


def _create_venv(python_executable: Path | None, venv_parent: Path | None = None, venv_name: str | None = None) -> Path:
    """Create a virtual environment for a QGIS plugin project."""

    if python_executable is None or not python_executable.exists() or not os.access(python_executable, os.X_OK):
        raise InvalidPythonExecutableError(python_executable)

    venv_parent = venv_parent or Path.cwd()
    if not venv_parent.exists():
        raise VenvParentDirectoryNotExistsError(venv_parent)

    venv_name = venv_name or ".venv"

    venv_directory = venv_parent / venv_name
    logger.debug("Creating virtual environment to '%s' using '%s'", venv_directory, python_executable)
    try:
        subprocess.run(
            [
                python_executable,
                "-m",
                "venv",
                "--system-site-packages",
                venv_directory,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.debug("Failed to create virtual environment. %s", e)
        raise VenvCreationError from e

    return venv_directory


def _create_glob_generator_from_pattern(pattern: str) -> Generator[Path, None, None]:
    """Create a glob generator from a pattern.

    The Path.glob() method does not support absolute paths. This is to overcome that limitation.
    """

    glob_parts: list[str] = []
    part_iterator = iter(Path(pattern).parts)
    root_part = next(part_iterator)
    if "*" in root_part:
        raise GlobPatternError(pattern)
    path = Path(root_part)
    for part in part_iterator:
        if not glob_parts and "*" not in part:
            path /= part
        else:
            glob_parts.append(part)

    return path.glob(os.sep.join(glob_parts))


class Platform(ABC):
    @classmethod
    @abstractmethod
    def create_venv(cls, *args: Any, **kwargs: Any) -> Path:
        """Create a virtual environment for plugin project."""

    @staticmethod
    def cli_arguments() -> list[CliArg]:
        """Returns environment specific command line arguments to be passed to argparse.ArgumentParser.add_argument()"""

        return []


class MultiQgisPlatform(Platform):
    @staticmethod
    @abstractmethod
    def _find_qgis_installations(qgis_installation_search_path_pattern: str | None = None) -> list[Path]:
        """Find all QGIS installations from the system."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _is_valid_qgis_path(qgis_path: Path) -> bool:
        """Validate that the given path is a valid QGIS installation."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _find_qgis_python_executable(qgis_install_directory: Path) -> Path | None:
        """Find the Python executable for the QGIS installation."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def create_venv(
        cls,
        python_executable: Path | None,
        qgis_installation: Path | None,
        venv_parent: Path,
        venv_name: str,
        qgis_installation_search_path_pattern: str | None = None,
    ) -> Path:
        raise NotImplementedError

    @classmethod
    def select_qgis_install(cls, custom_search_path_pattern: str | None = None) -> Path:
        """Prompts the user to select a QGIS installation from the system."""

        custom_search_path_pattern = custom_search_path_pattern or os.environ.get(
            "QGIS_INSTALLATION_SEARCH_PATH_PATTERN"
        )
        qgis_installations = list(cls._find_qgis_installations(custom_search_path_pattern))

        print("Found following QGIS installations from the system. Which one to use for development?")
        for i, path in enumerate(qgis_installations):
            print(f"  {i+1} - {path}")
        custom_selection_index = len(qgis_installations) + 1
        print(f"  {custom_selection_index} - Custom")
        choose_prompt = f"Choose from [{'/'.join(str(i+1) for i in range(custom_selection_index))}]"
        while True:
            try:
                selection = int(input(f"  {choose_prompt}: "))
            except ValueError:
                print("Invalid selection.")
                continue

            if selection == custom_selection_index:
                while True:
                    custom_qgis_path = Path(input("  Give path to QGIS installation: "))
                    if not cls._is_valid_qgis_path(custom_qgis_path):
                        print("Invalid qgis installation path")
                        continue
                    return custom_qgis_path
            else:
                try:
                    return qgis_installations[selection - 1]
                except IndexError:
                    print("Invalid selection")
                    continue

    @staticmethod
    def cli_arguments() -> list[CliArg]:
        return [
            CliArg(
                "--qgis-installation",
                help=(
                    "Path to the QGIS installation to use for development. "
                    "Installations made with official msi and Osgeo4W instellers are supported. "
                    "Give the path to the 'qgis' directory inside the 'apps' directory. "
                    "If not given, the user is prompted to select one."
                ),
                type=Path,
            ),
            CliArg(
                "--qgis-installation-search-path-pattern",
                help=(
                    "Custom glob pattern for QGIS installations to be selected. "
                    "Can be set also with QGIS_INSTALLATION_SEARCH_PATH_PATTERN environment variable."
                ),
                type=str,
            ),
            CliArg(
                "--python-executable",
                help=(
                    "Path to the Python executable used by the QGIS installation. "
                    "If not given, the Python executable is searched from the QGIS installation."
                ),
                type=Path,
            ),
        ]


class Windows(MultiQgisPlatform):
    @classmethod
    def _find_qgis_installations(cls, custom_search_path_pattern: str | None = None) -> list[Path]:
        """Find all QGIS installations from the Windows system."""

        possible_qgis_installation_generators = [
            Path("C:/Program Files").glob("QGIS*/apps/qgis*/"),
            Path("C:/OSGeo4W/apps").glob("qgis*/"),
            Path("C:/OSGeo4W64/apps").glob("qgis*/"),
        ]

        if custom_search_path_pattern is not None:
            if not custom_search_path_pattern.endswith(os.sep) or (
                os.altsep is not None and not custom_search_path_pattern.endswith(os.altsep)
            ):
                custom_search_path_pattern += os.sep
            possible_qgis_installation_generators.append(
                _create_glob_generator_from_pattern(custom_search_path_pattern)
            )

        return [
            qgis_installation
            for possible_qgis_installation_glob in possible_qgis_installation_generators
            for qgis_installation in possible_qgis_installation_glob
            if cls._is_valid_qgis_path(qgis_installation)
        ]

    @staticmethod
    def _is_valid_qgis_path(qgis_installation: Path) -> bool:
        root = qgis_installation.parent.parent
        bin_directory = root / "bin"
        qgis_bin_directory = qgis_installation / "bin"
        qt5_bin_directory = root / "apps" / "Qt5" / "bin"
        python_path = Windows._find_qgis_python_executable(qgis_installation)
        if not python_path:
            return False
        return all(d.exists() for d in (bin_directory, qgis_bin_directory, qt5_bin_directory, python_path))

    @staticmethod
    def _find_qgis_python_executable(qgis_install_directory: Path) -> Path | None:
        """Find the Python executable for the QGIS installation."""

        apps_directory = qgis_install_directory.parent
        python_install_directory = next(apps_directory.glob("Python*"), None)
        if not python_install_directory:
            return None
        return python_install_directory / "python.exe"

    @staticmethod
    def _create_sitecustomize_file(venv_directory: Path, qgis_installation: Path) -> None:
        root = qgis_installation.parent.parent
        bin_directory = root / "bin"
        qgis_bin_directory = qgis_installation / "bin"
        qt5_bin_directory = root / "apps" / "Qt5" / "bin"

        content = (
            "import os\n"
            "\n"
            f"os.add_dll_directory('{bin_directory.as_posix()}')\n"
            f"os.add_dll_directory('{qgis_bin_directory.as_posix()}')\n"
            f"os.add_dll_directory('{qt5_bin_directory.as_posix()}')\n"
        )
        sitecustomize_file_path = venv_directory / "Lib" / "site-packages" / "sitecustomize.py"
        logger.debug("Writing site customize file to '%s'", sitecustomize_file_path)
        sitecustomize_file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def _create_path_configuration_file(venv_directory: Path, qgis_installation: Path) -> None:
        content = (qgis_installation / "python").as_posix() + "\n"

        path_file_path = venv_directory / "qgis.pth"
        logger.debug("Writing qgis path configuration to '%s'", path_file_path)
        path_file_path.write_text(content, encoding="utf-8")

    @staticmethod
    def _patch_venv(venv_directory: Path, qgis_installation: Path) -> None:
        Windows._create_path_configuration_file(venv_directory, qgis_installation)
        Windows._create_sitecustomize_file(venv_directory, qgis_installation)

    @classmethod
    def create_venv(
        cls,
        python_executable: Path | None,
        qgis_installation: Path | None,
        venv_parent: Path,
        venv_name: str,
        qgis_installation_search_path_pattern: str | None = None,
    ) -> Path:
        qgis_installation = qgis_installation or cls.select_qgis_install(qgis_installation_search_path_pattern)
        if not cls._is_valid_qgis_path(qgis_installation):
            raise InvalidQgisPathError(qgis_installation)
        python_executable = python_executable or cls._find_qgis_python_executable(qgis_installation)
        if not _is_valid_python_executable(python_executable):
            raise InvalidPythonExecutableError(python_executable)
        venv_directory = _create_venv(python_executable, venv_parent, venv_name=venv_name)

        cls._patch_venv(venv_directory, qgis_installation)

        return venv_directory


class Linux(Platform):
    @classmethod
    def create_venv(
        cls, python_executable: Path | None = None, venv_parent: Path | None = None, venv_name: str | None = None
    ) -> Path:
        if python_executable is None:
            python3_command = Path("python3")
            python3_executable = shutil.which(python3_command)
            if python3_executable is None:
                raise InvalidPythonExecutableError(python3_command)
            python_executable = Path(python3_executable)

        return _create_venv(python_executable, venv_parent, venv_name=venv_name)


def cli() -> None:
    """Create a virtual environment for a QGIS plugin project."""

    environments: dict[str, SupportsVenvCreation] = {
        "Windows": Windows,
        "Linux": Linux,
        # "Darwin": MacOs, TODO: Implement MacOs support
    }
    environment = environments.get(platform.system())
    if environment is None:
        raise UnsupportedPlatformError(platform.system())

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--venv-parent",
        help=(
            "Path to the parent directory of the virtual environment to be created. "
            "Most likely your project directory. Default current directory."
        ),
        type=Path,
        default=Path.cwd(),
    )
    parser.add_argument("--venv-name", help="Name of the virtual environment", default=".venv")
    for cli_arg in environment.cli_arguments():
        parser.add_argument(*cli_arg.args, **cli_arg.kwargs)
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = cast("CliArgsType", vars(parser.parse_args()))
    cli_args.update(args)

    if args.pop("debug"):
        logging.basicConfig(level=logging.DEBUG)

    try:
        environment.create_venv(**args)
    except VenvCreationError:
        print("Virtual environment creation failed", file=sys.stderr)
        sys.exit(1)
    except (InvalidPythonExecutableError, InvalidQgisPathError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def main() -> None:
    try:
        cli()
    except KeyboardInterrupt:
        print("Virtual environment creation cancelled", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

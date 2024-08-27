from pathlib import Path

from pytest_cookies.plugin import Result


def processing_directory_exitst(baked_project: Result, project_path: Path) -> bool:
    """Returns True if the processing directory exists."""
    return (
        project_path
        / str(baked_project.context["plugin_package"])
        / f"{baked_project.context['plugin_package']}_processing"
    ).is_dir()

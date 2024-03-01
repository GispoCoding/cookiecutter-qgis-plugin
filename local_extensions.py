from cookiecutter.utils import simple_filter


@simple_filter
def selected(v):
    return v.lower() in ("y", "yes", "true", "1")

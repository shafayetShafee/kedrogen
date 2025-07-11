import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse

from typer import Exit
from kedrogen.logger import Logger


ALLOWED_GIT_PREFIXES = {"git+", "git@",
                        "ssh://", "git://",
                        "https://", "http://"}

ALLOWED_HG_PREFIXES = {"hg+", "hg+ssh://", "hg+https://"}

ZIP_EXTENSIONS = (".zip",)

GIT_SHORT_HAND_RE = re.compile(r"^(gh|gl|bb|bitbucket):[\w\-]+/[\w\-]+$")


def is_git_url(url: str) -> bool:
    """Check if the string is a Git-compatible URL."""
    parsed = urlparse(url)
    return (
        GIT_SHORT_HAND_RE.match(url) is not None or
        any(url.startswith(prefix) for prefix in ALLOWED_GIT_PREFIXES) or
        url.endswith(".git")
    )


def is_hg_url(url: str) -> bool:
    """Check if the string is a Mercurial-compatible URL."""
    return any(url.startswith(prefix) for prefix in ALLOWED_HG_PREFIXES)


def is_zip_file(source: str) -> bool:
    """Check if the input is a zip file (local or remote)."""
    return source.endswith(ZIP_EXTENSIONS)


def is_file_url(url: str) -> bool:
    """Check if it's a file:// URL."""
    parsed = urlparse(url)
    return parsed.scheme == "file"


def is_local_directory(path_str: str) -> bool:
    """Check if the path is an existing, readable directory."""
    path = Path(path_str)
    return path.exists() and path.is_dir() and os.access(path, os.R_OK)


def validate_template_source(template: str, logger: Logger) -> str:
    """
    Validate a given template source. Allow:
    - local directory
    - Git/Mercurial URLs
    - file:// URL
    - zip file (local or remote)
    - shorthand (gh:user/repo)
    """
    if is_local_directory(template):
        logger.debug(f"[grey]Using local template: {template}[/grey]")
        return str(Path(template).resolve())

    if (
        is_git_url(template)
        or is_hg_url(template)
        or is_file_url(template)
        or is_zip_file(template)
    ):
        logger.debug(f"[grey]Using remote template or archive: {template}[/grey]")
        return template

    logger.error(f"[red][x] Invalid template source: '{template}'[/red]")
    raise Exit(code=1)


def build_extra_context(template_path: Path, fixed_context: dict, logger: Logger) -> dict:
    """
    Prepares the extra context for cookiecutter by extending the fixed context
    with supplied keys from `cookiecutter.json` file and setting None to additional
    keys from `cookiecutter.json` file.
    """
    cookiecutter_json = template_path / "cookiecutter.json"

    if not cookiecutter_json.exists():
        logger.error(f"[red][x] [bold]cookiecutter.json[/bold] not found at: {cookiecutter_json}[/red]")
        raise Exit(code=1)

    try:
        template_context = json.loads(cookiecutter_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"[red][x] Invalid JSON in [bold]cookiecutter.json[/bold]: {e}[/red]")
        raise Exit(code=1)

    fixed_keys = fixed_context.keys()

    dynamic_context = {
        key: None for key in template_context.keys() if key not in fixed_keys
    }

    extra_context = {**dynamic_context, **fixed_context}
    return extra_context
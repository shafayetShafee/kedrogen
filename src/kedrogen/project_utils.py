import re
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

import typer
from kedrogen.logger import Logger


def get_current_dir_name() -> str:
    return Path.cwd().name


def validate_dirname(name: str, logger: Logger):
    pattern = r"^[\w\-_]{2,}$"
    if not re.match(pattern, name):
        logger.error(f"[red][x] Invalid directory name: [bold]'{name}'[/bold][/red]")
        logger.error("[red]    Must contain only alphanumeric characters, hyphens, or underscores and be at least 2 characters.[/red]")
        raise typer.Exit(code=1)


def get_kedro_version(logger: Logger) -> str:
    try:
        return version("kedro")
    except PackageNotFoundError:
        logger.error("[red][x] kedro is not installed. Please install it before proceeding.[/red]")
        raise typer.Exit(code=1)
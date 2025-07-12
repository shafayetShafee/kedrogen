import json
import re
import shutil
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Optional

from cookiecutter.utils import force_delete
from rich import print
from typer import Exit, confirm

from kedrogen import __version__


class Logger:
    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet

    def info(self, msg: str):
        if not self.quiet:
            print(msg)

    def debug(self, msg: str):
        if self.verbose and not self.quiet:
            print(msg)

    def warn(self, msg: str):
        print(msg)

    def error(self, msg: str):
        print(msg)


def version_callback(value: Optional[bool]):
    """
    Callback for the --version flag to display the current kedrogen version.

    Args:
        value (Optional[bool]): Flag indicating whether --version was passed.

    Raises:
        Exit: Terminates the CLI after printing version info.
    """
    if value:
        print(
            f"[blue]kedrogen version:[/blue] [bold magenta]{__version__}[/bold magenta]"
        )
        raise Exit()


def get_current_dir_name() -> str:
    """
    Return the name of the current working directory.

    Returns:
        str: The base name of the current working directory.
    """
    return Path.cwd().name


def validate_dirname(name: str, logger: Logger) -> None:
    """
    Validate whether the given directory name is valid for a Kedro project.

    A valid name must contain only alphanumeric characters, hyphens (-),
    or underscores (_), and be at least 2 characters long.

    Args:
        name (str): The name to validate (usually the current directory).
        logger (Logger): Logger instance for outputting messages.

    Raises:
        Exit: If the name is invalid, exits with error code 1.
    """
    pattern = r"^[\w\-_]{2,}$"
    if not re.match(pattern, name):
        logger.error(f"[red][x] Invalid directory name: [bold]'{name}'[/bold][/red]")
        logger.error(
            "[red]    Must contain only alphanumeric characters, hyphens, or underscores and be at least 2 characters.[/red]"
        )
        raise Exit(code=1)


def get_kedro_version(logger: Logger) -> str:
    """
    Retrieve the installed version of Kedro.

    Args:
        logger (Logger): Logger instance for outputting messages.

    Returns:
        str: The installed Kedro version.

    Raises:
        Exit: If Kedro is not installed, exits the CLI with an error message.
    """
    try:
        return version("kedro")
    except PackageNotFoundError as err:
        logger.error(
            "[red][x] kedro is not installed. Please install it before proceeding.[/red]"
        )
        raise Exit(code=1) from err


def prompt_overwrite(file_path: Path) -> bool:
    """
    Prompt the user to confirm overwriting an existing file or directory.

    Args:
        file_path (Path): The path to the file or directory that already exists.

    Returns:
        bool: True if the user confirms to overwrite, False otherwise.
    """
    return confirm(
        f"'{file_path}' already exists. Overwrite?", default=None, show_default=True
    )


def format_colored_dict(d: dict[str, Any]) -> str:
    """
    Format a dictionary as a string with Rich-style color formatting.

    Keys are displayed in magenta, and values are displayed in green.

    Args:
        d (Dict[str, Any]): The dictionary to format.

    Returns:
        str: A string representation of the dictionary with Rich markup.
    """
    lines = []
    for key, value in d.items():
        lines.append(f"  [magenta]{key}[/magenta]: [green]{repr(value)}[/green]")
    return "{\n" + ",\n".join(lines) + "\n}"


def move_contents(src_dir: Path, dest_dir: Path, logger: Logger) -> None:
    """
    Move the contents of a source directory to a destination directory.

    If a file or directory with the same name exists in the destination,
    the user is prompted for overwrite confirmation. The source directory
    is removed after a successful move.

    Args:
        src_dir (Path): The source directory whose contents are to be moved.
        dest_dir (Path): The target directory where contents will be moved to.
        logger (Logger): Logger instance for logging messages.

    Raises:
        Exit: If the source directory is invalid or a file operation fails.
    """
    if not src_dir.is_dir():
        logger.error(
            f"[red][x] Source directory [bold]'{src_dir}'[/bold] does not exist or is not a directory.[/red]"
        )
        raise Exit(code=1)

    for item in src_dir.iterdir():
        dest_item = dest_dir / item.name
        try:
            if dest_item.exists():
                if prompt_overwrite(dest_item):
                    if dest_item.is_dir():
                        shutil.rmtree(dest_item, onerror=force_delete)
                    else:
                        dest_item.unlink()
                else:
                    logger.warn(
                        f"[yellow][!] Skipping moving: [bold]'{dest_item}'[/bold][/yellow]"
                    )
                    continue

            shutil.move(str(item), str(dest_item))
            logger.debug(
                f"[blue][✔] Moved:[blue] [bold green]'{item.name}'[/bold green]"
            )
        except Exception as err:
            logger.error(
                f"[red][x] Failed to move [bold]'{item.name}'[/bold]: {err}[/red]"
            )
            raise Exit(code=1) from err

    try:
        shutil.rmtree(src_dir, onerror=force_delete)
        logger.debug(f"[blue][✔] Removed directory:[blue] [green]{src_dir}[/green]")
    except Exception as e:
        logger.warn(
            f"[yellow][!] Could not remove [bold]'{src_dir}'[/bold]. Reason:[/yellow] {e}"
        )


def build_context(template_path: Path, fixed_context: dict, logger: Logger) -> dict:
    """
    Build the final context dictionary used by Cookiecutter.

    This function reads `cookiecutter.json` from the given template path,
    and merges it with a fixed context dictionary provided by the CLI.
    Keys present in `cookiecutter.json` but not in the fixed context are added with `None` values.
    Fixed context values take precedence over the file-defined values.

    Args:
        template_path (Path): The local path to the cookiecutter template directory.
        fixed_context (Dict[str, Any]): Context values that must be enforced (e.g., project name, package name).
        logger (Logger): Logger instance for debug and error messages.

    Returns:
        Dict[str, Any]: The combined context to be passed to cookiecutter.

    Raises:
        Exit: If the `cookiecutter.json` file is missing or contains invalid JSON.
    """
    base_context_file = template_path / "cookiecutter.json"

    if not base_context_file.exists():
        logger.error(
            f"[red][x] [bold]cookiecutter.json[/bold] not found at: {base_context_file}[/red]"
        )
        raise Exit(code=1)

    try:
        base_context = json.loads(base_context_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        logger.error(
            f"[red][x] Invalid JSON in [bold]cookiecutter.json[/bold]: {err}[/red]"
        )
        raise Exit(code=1) from err

    fixed_keys = fixed_context.keys()

    modified_base_context = {
        key: None for key in base_context.keys() if key not in fixed_keys
    }

    context = {**modified_base_context, **fixed_context}
    return context


import shutil
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated

import typer
from rich import print
from cookiecutter.config import get_user_config
from cookiecutter.repository import determine_repo_dir
from cookiecutter.utils import force_delete
from cookiecutter.main import cookiecutter

from kedrogen import __version__
from kedrogen.logger import Logger
from kedrogen.project_utils import get_current_dir_name, validate_dirname, get_kedro_version
from kedrogen.template_utils import build_context


def prompt_overwrite(file_path: Path) -> bool:
    return typer.confirm(f"'{file_path}' already exists. Overwrite?", default=None, show_default=True)

def format_colored_dict(d: dict) -> str:
    lines = []
    for key, value in d.items():
        lines.append(f"  [magenta]{key}[/magenta]: [green]{repr(value)}[/green]")
    return "{\n" + ",\n".join(lines) + "\n}"

def move_contents(src_dir: Path, dest_dir: Path, logger: Logger):
    if not src_dir.is_dir():
        logger.error(f"[red][x] Source directory [bold]'{src_dir}'[/bold] does not exist or is not a directory.[/red]")
        raise typer.Exit(code=1)

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
                    logger.warn(f"[yellow][!] Skipping moving: [bold]'{dest_item}'[/bold][/yellow]")
                    continue

            shutil.move(str(item), str(dest_item))
            logger.debug(f"[blue][✔] Moved:[blue] [bold green]'{item.name}'[/bold green]")
        except Exception as e:
            logger.error(f"[red][x] Failed to move [bold]'{item.name}'[/bold]: {e}[/red]")

    try:
        shutil.rmtree(src_dir, onerror=force_delete)
        logger.debug(f"[blue][✔] Removed directory:[blue] [green]{src_dir}[/green]")
    except Exception as e:
        logger.warn(f"[yellow][!] Could not remove [bold]'{src_dir}'[/bold]. Reason:[/yellow] {e}")


def version_callback(value: bool):
    if value:
        print(f"[blue]kedrogen version:[/blue] [bold magenta]{__version__}[/bold magenta]")
        raise typer.Exit()


app = typer.Typer(
    help="Generate a Kedro project from a cookiecutter template in the current directory"
)


@app.command()
def generate(
    template_path: Annotated[
        str,
        typer.Argument(help="Path or Git URL of the Cookiecutter template.")
    ],
    verbose: Annotated[
        Optional[bool],
        typer.Option("--verbose", help="Show detailed output.")
    ] = False,
    quiet: Annotated[
        Optional[bool],
        typer.Option("--quiet", "-q", help="Suppress all non-error messages.")
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", "-v",
            help="Show the version and exit.", 
            callback=version_callback,
            is_eager=True
        )
    ] = None
):
    logger = Logger(verbose=verbose, quiet=quiet)
    
    if verbose and quiet:
        print("[red][x] Cannot use both --verbose and --quiet together.[/red]")
        raise typer.Exit(code=1)

    current_dir = get_current_dir_name()
    validate_dirname(current_dir, logger)
    kedro_version = get_kedro_version(logger)

    logger.info(f"[blue][✔] Using current directory as project name:[/blue] '[bold green]{current_dir}[/bold green]'")
    logger.info(f"[blue][✔] Detected Kedro version:[/blue] [bold green]{kedro_version}[/bold green]")

    fixed_context = {
        "project_name": current_dir.strip().replace("-", " ").replace("_", " ").title(),
        "repo_name": current_dir,
        "python_package": current_dir.strip().replace("-", "_").lower() + "_kedro",
        "kedro_version": kedro_version
    }

    try:
        config_dict = get_user_config(None, False)
    except Exception as e:
        logger.error(f"[red][x] {e}[/red]")
        raise typer.Exit(code=1)
    
    try:
        base_repo_dir, _ = determine_repo_dir(
            template=template_path,
            abbreviations=config_dict['abbreviations'],
            clone_to_dir=config_dict['cookiecutters_dir'],
            checkout=None,
            no_input=True,
            password=None,
            directory=None
        )
        logger.debug(f"[blue][✔] Cloned the project contents to:[blue] [bold green]'{base_repo_dir}'[/bold green]")
    except Exception as e:
        logger.error(f"[red][x] {e}[/red]")
        raise typer.Exit(code=1)

    extra_context = build_context(Path(base_repo_dir), fixed_context, logger=logger)
    logger.debug(f"[blue][✔] Using the cookiecutter context:[/blue] {format_colored_dict(fixed_context)}")

    try:
        result_path = cookiecutter(
            str(base_repo_dir),
            no_input=True,
            extra_context=extra_context
        )

        try:
            shutil.rmtree(base_repo_dir, onerror=force_delete)
        except Exception as e:
            logger.error(f"[red][x] {e}[/red]")
            raise typer.Exit(code=1)
        
        move_contents(Path(result_path), Path.cwd(), logger)
        logger.info(f"\n[green]✅ Project [bold]`{current_dir}`[/bold] generated successfully in the current directory![/green]")
    
    except Exception as e:
        logger.error(f"[red][x] {e}[/red]")
        raise typer.Exit(code=1)

import shutil
from pathlib import Path

import typer
from cookiecutter.main import cookiecutter

from kedrogen import __version__
from kedrogen.logger import Logger
from kedrogen.project_utils import get_current_dir_name, validate_dirname, get_kedro_version
from kedrogen.template_utils import build_extra_context, validate_template_source


def prompt_overwrite(file_path: Path) -> bool:
    return typer.confirm(f"'{file_path}' already exists. Overwrite?", default=None, show_default=True)


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
                        shutil.rmtree(dest_item)
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
        shutil.rmtree(src_dir)
        logger.debug(f"[blue][✔] Removed directory:[blue] [green]{src_dir}[/green]")
    except Exception as e:
        logger.warn(f"[yellow][!] Could not remove [bold]'{src_dir}'[/bold]. Reason:[/yellow] {e}")


def raise_exit():
    raise typer.Exit(code=1)



def generate(
    template: str = typer.Argument(..., help="Path or Git URL of the Cookiecutter template."),
    verbose: bool = typer.Option(False, "--verbose", help="Show detailed output."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress all non-error messages."),
    version: bool = typer.Option(False, "--version", help="Show the version and exit.", is_eager=True)
):
    if version:
        logger.info(f"kedrogen v{__version__}")
        raise typer.Exit()
    
    if verbose and quiet:
        print("[red][x] Cannot use both --verbose and --quiet together.[/red]")
        raise typer.Exit(code=1)

    logger = Logger(verbose=verbose, quiet=quiet)

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

    validated_template = validate_template_source(template, logger=logger)

    template_path_for_context = Path(validated_template) if Path(validated_template).exists() else None

    extra_context = (
        build_extra_context(template_path_for_context, fixed_context, logger=logger)
        if template_path_for_context else fixed_context
    )


    try:
        result_path = cookiecutter(
            template,
            no_input=True,
            extra_context=extra_context
        )
        move_contents(Path(result_path), Path.cwd(), logger)
        logger.info(f"\n[green]✅ Project [bold]`{current_dir}`[/bold] generated successfully in the current directory![/green]")
    except Exception as e:
        logger.error(f"[red][x] {e}[/red]")
        raise typer.Exit(code=1)


app = typer.Typer(
    callback=generate, 
    help="Generate a Kedro project from a cookiecutter template in the current directory"
)
from pathlib import Path
from typing import Annotated, Optional

from cookiecutter.config import get_user_config
from cookiecutter.main import cookiecutter
from cookiecutter.repository import determine_repo_dir
from cookiecutter.utils import rmtree
from typer import Argument, Exit, Option, Typer

from kedrogen.utils import (
    Logger,
    build_context,
    format_colored_dict,
    get_current_dir_name,
    get_kedro_version,
    move_contents,
    validate_dirname,
    version_callback,
)

app = Typer(
    help="Generate a Kedro project from a cookiecutter template in the current directory"
)

@app.command()
def generate(
    template_path: Annotated[
        str, Argument(help="Path or Git URL of the Cookiecutter template.")
    ],
    verbose: Annotated[
        Optional[bool], Option("--verbose", help="Show detailed output.")
    ] = False,
    quiet: Annotated[
        Optional[bool],
        Option("--quiet", "-q", help="Suppress all non-error messages."),
    ] = False,
    version: Annotated[
        Optional[bool],
        Option(
            "--version",
            "-v",
            help="Show the version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
):
    logger = Logger(verbose=verbose, quiet=quiet)

    if verbose and quiet:
        logger.error("[red][x] Cannot use both --verbose and --quiet together.[/red]")
        raise Exit(code=1)

    current_dir = get_current_dir_name()
    validate_dirname(current_dir, logger)
    kedro_version = get_kedro_version(logger)

    logger.info(
        f"[blue][✔] Using current directory as project name:[/blue] '[bold green]{current_dir}[/bold green]'"
    )
    logger.info(
        f"[blue][✔] Detected Kedro version:[/blue] [bold green]{kedro_version}[/bold green]"
    )

    fixed_context = {
        "project_name": current_dir.strip().replace("-", " ").replace("_", " ").title(),
        "repo_name": current_dir,
        "python_package": current_dir.strip().replace("-", "_").lower() + "_kedro",
        "kedro_version": kedro_version,
    }

    try:
        config_dict = get_user_config(None, False)
    except Exception as err:
        logger.error(f"[red][x] {err}[/red]")
        raise Exit(code=1) from err

    try:
        base_repo_dir, _ = determine_repo_dir(
            template=template_path,
            abbreviations=config_dict["abbreviations"],
            clone_to_dir=config_dict["cookiecutters_dir"],
            checkout=None,
            no_input=True,
            password=None,
            directory=None,
        )
        logger.debug(
            f"[blue][✔] Cloned the project contents to:[blue] [bold green]'{base_repo_dir}'[/bold green]"
        )
    except Exception as err:
        logger.error(f"[red][x] {err}[/red]")
        raise Exit(code=1) from err

    extra_context = build_context(Path(base_repo_dir), fixed_context, logger=logger)
    logger.debug(
        f"[blue][✔] Using the cookiecutter context:[/blue] {format_colored_dict(fixed_context)}"
    )

    try:
        result_path = cookiecutter(
            str(base_repo_dir), no_input=True, extra_context=extra_context
        )

        try:
            rmtree(base_repo_dir)
        except Exception as err:
            logger.error(f"[red][x] {err}[/red]")
            raise Exit(code=1) from err

        move_contents(Path(result_path), Path.cwd(), logger)
        logger.info(
            f"\n[green]✅ Project [bold]`{current_dir}`[/bold] generated successfully in the current directory![/green]"
        )

    except Exception as err:
        logger.error(f"[red][x] {err}[/red]")
        raise Exit(code=1) from err

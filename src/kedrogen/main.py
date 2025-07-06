import re
import json
import shutil
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

import typer
from rich import print
from cookiecutter.main import cookiecutter


app = typer.Typer(help="Generate a Kedro Cookiecutter project in the current directory.")


def get_current_dir_name() -> str:
    return Path.cwd().name


def validate_dirname(name: str):
    pattern = r"^[\w\-_]{2,}$"
    if not re.match(pattern, name):
        print(f"[red][x] Invalid directory name: [bold]'{name}'[/bold][/red]")
        print("[red]    Must contain only alphanumeric characters, hyphens, or underscores and be at least 2 characters.[/red]")
        raise typer.Exit(code=1)


def get_kedro_version() -> str:
    try:
        return version("kedro")
    except PackageNotFoundError:
        print("[red][x] kedro is not installed. Please install it before proceeding.[/red]")
        raise typer.Exit(code=1)


def prompt_overwrite(file_path: Path) -> bool:
    """Prompt the user whether to overwrite a file using Typer's confirm."""
    return typer.confirm(f"'{file_path}' already exists. Overwrite?", default=None, show_default=True)


def move_contents(src_dir: Path, dest_dir: Path):
    if not src_dir.is_dir():
        print(f"[red][x] Source directory [bold]'{src_dir}'[/bold] does not exist or is not a directory.[/red]")
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
                    print(f"[yellow][!] Skipping moving: [bold]'{dest_item}'[/bold][/yellow]")
                    continue

            shutil.move(str(item), str(dest_item))
            print(f"[blue][✔] Moved:[blue] [bold green]'{item.name}'[/bold green]")
        except Exception as e:
            print(f"[red]\[x] Failed to move [bold]'{item.name}'[/bold]: {e}[/red]")

    try:
        shutil.rmtree(src_dir)
        print(f"[blue][✔] Removed directory:[blue] [green]{src_dir}[/green]")
    except Exception as e:
        print(f"[yellow][!] Could not remove [bold]'{src_dir}'[/bold]. Reason:[/yellow] {e}")


def build_extra_context(template_path: Path, fixed_context: dict) -> dict:
    """Load cookiecutter.json and merge user-controlled fields into extra_context."""
    cookiecutter_json = template_path / "cookiecutter.json"

    if not cookiecutter_json.exists():
        print(f"[red][x] [bold]cookiecutter.json[/bold] not found at: {cookiecutter_json}[/red]")
        raise typer.Exit(code=1)

    try:
        template_context = json.loads(cookiecutter_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[red][x] Invalid JSON in [bold]cookiecutter.json[/bold]: {e}[/red]")
        raise typer.Exit(code=1)

    fixed_keys = fixed_context.keys()

    dynamic_context = {
        key: None for key in template_context.keys() if key not in fixed_keys
    }

    full_context = {**dynamic_context, **fixed_context}
    return full_context


@app.command()
def generate(
    template: Path = typer.Argument(
        ..., exists=True, readable=True, help="Path to the Cookiecutter template folder."
    )
):
    """Generate a Kedro project using a Cookiecutter template into the current directory."""
    current_dir = get_current_dir_name()
    validate_dirname(current_dir)
    kedro_version = get_kedro_version()

    print(f"[blue][✔] Setting project name from current directory name as:[/blue] '[bold green]{current_dir}[/bold green]'")
    print(f"[blue][✔] Detected Kedro version:[/blue] [bold green]{kedro_version}[/bold green]")

    fixed_context = {
        "project_name": current_dir.strip().replace("-", " ").replace("_", " ").title(),
        "repo_name": current_dir,
        "python_package": current_dir.strip().replace("-", "_").lower() + "_kedro",
        "kedro_version": kedro_version
    }

    extra_context = build_extra_context(template, fixed_context)

    try:
        result_path = cookiecutter(
            str(template),
            no_input=True,
            extra_context=extra_context
        )
        move_contents(Path(result_path), Path.cwd())
        print("\n[bold green]✅ Project generated successfully![/bold green]")
    except Exception as e:
        print(f"[red][x] {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

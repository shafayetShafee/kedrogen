import json
from pathlib import Path

from typer import Exit
from kedrogen.logger import Logger


def build_context(template_path: Path, fixed_context: dict, logger: Logger) -> dict:
    """
    Prepares the extra context for cookiecutter by extending the fixed context
    with supplied keys from `cookiecutter.json` file and setting None to additional
    keys from `cookiecutter.json` file.
    """
    base_context_file = template_path / "cookiecutter.json"

    if not base_context_file.exists():
        logger.error(f"[red][x] [bold]cookiecutter.json[/bold] not found at: {base_context_file}[/red]")
        raise Exit(code=1)

    try:
        base_context = json.loads(base_context_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"[red][x] Invalid JSON in [bold]cookiecutter.json[/bold]: {e}[/red]")
        raise Exit(code=1)

    fixed_keys = fixed_context.keys()

    modified_base_context = {
        key: None for key in base_context.keys() if key not in fixed_keys
    }

    context = {**modified_base_context, **fixed_context}
    return context
from pathlib import Path

import typer
from typer.main import get_command


def typer_to_justfile(app: typer.Typer, output_path: Path = Path("Justfile")) -> None:
    """Introspects Typer application commands and generates a Justfile."""
    click_cmd = get_command(app)

    recipes = [
        "# Auto-generated Justfile from Typer CLI introspection",
        'set shell := ["bash", "-c"]',
        "",
        "# Default recipe",
        "default:",
        "\t@just --list",
        "",
    ]

    def process_command(cmd, prefix=""):
        if hasattr(cmd, "commands"):
            for sub_name, sub_cmd in cmd.commands.items():
                new_prefix = f"{prefix} {sub_name}" if prefix else sub_name
                process_command(sub_cmd, new_prefix)
        else:
            if not prefix or prefix == "dev gen-just":
                return
            recipe_name = prefix.replace(" ", "-")
            doc = (cmd.help or "Run command").strip().split("\n")[0]
            recipes.append(f"# {doc}")
            recipes.append(f"{recipe_name} *args:")
            recipes.append(f"\tuv run python -m malta.cli.main {prefix} {{{{args}}}}\n")

    process_command(click_cmd)

    output_path.write_text("\n".join(recipes))
    print(f"Generated {output_path} successfully.")

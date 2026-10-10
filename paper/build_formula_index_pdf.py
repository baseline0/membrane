"""Render formula_index.md as a standalone PDF appendix.

Reads the markdown table written by validate_formulas.py, writes a Typst file
to generated/, and compiles it with the local typst binary. The appendix is a
separate document; including it in main.typ is an editorial choice.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent
INDEX = PAPER / "formula_index.md"
OUT_DIR = PAPER / "generated"
TYP = OUT_DIR / "formula_index_appendix.typ"
PDF = OUT_DIR / "formula_index_appendix.pdf"

ROW = re.compile(r"^\|(.+)\|\s*$")


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def typst_string(text: str) -> str:
    """Quote text for a Typst string literal, escaping backslashes and quotes."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_tables(markdown: str) -> list[tuple[list[str], list[list[str]]]]:
    """Return each markdown table as (header, rows). A table is a run of consecutive table lines."""
    tables: list[tuple[list[str], list[list[str]]]] = []
    current: list[list[str]] = []
    for line in markdown.splitlines():
        if ROW.match(line):
            current.append(cells(line))
            continue
        if current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    result = []
    for block in tables:
        header, body = block[0], block[1:]
        body = [row for row in body if not all(set(c) <= set("-:") for c in row)]
        result.append((header, body))
    if not result:
        raise SystemExit(f"no table found in {INDEX.name}")
    return result


def typst_table(header: list[str], rows: list[list[str]]) -> list[str]:
    cols = len(header)
    head = ", ".join(f'text(weight: "bold", {typst_string(h)})' for h in header)
    lines = [f"#table(columns: {cols}, stroke: 0.4pt, inset: 4pt,", f"  {head},"]
    for row in rows:
        cells_typ = ", ".join(
            f"raw({typst_string(c.strip('`'))})" if c.startswith("`") else typst_string(c) for c in row
        )
        lines.append(f"  {cells_typ},")
    lines.append(")")
    return lines


def build_typst(tables: list[tuple[list[str], list[list[str]]]]) -> str:
    lines = [
        '#set page(paper: "a4", margin: 1.5cm, numbering: "1")',
        "#set text(size: 8pt)",
        "",
        "= Formula Index",
        "",
        "Generated from model.py via validate_formulas.py.",
    ]
    for header, rows in tables:
        lines += ["", *typst_table(header, rows)]
    return "\n".join(lines) + "\n"


def main() -> int:
    if not INDEX.exists():
        print(f"missing {INDEX.name}; run validate_formulas.py first", file=sys.stderr)
        return 1
    if shutil.which("typst") is None:
        print("typst not found; install it with `just install-typst`", file=sys.stderr)
        return 1
    tables = parse_tables(INDEX.read_text())
    rows = sum(len(body) for _, body in tables)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TYP.write_text(build_typst(tables))
    result = subprocess.run(["typst", "compile", str(TYP), str(PDF)], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return 1
    print(f"wrote {PDF.relative_to(PAPER)} ({rows} rows in {len(tables)} tables)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

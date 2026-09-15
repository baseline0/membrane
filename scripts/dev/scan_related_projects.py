#!/usr/bin/env python3
"""
Scan related projects (learn-ollama, etf-pulse, etc.) for best practices,
library usage patterns, and architectural insights to potentially adopt in malta.

Run: uv run python scripts/dev/scan_related_projects.py
Output: Saved to scripts/dev/scan_findings.md
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ProjectScan:
    """Findings from scanning a related project."""

    name: str
    path: Path
    has_pyproject: bool = False
    python_version: Optional[str] = None
    dependencies: list = None
    cli_framework: Optional[str] = None
    testing_setup: Optional[str] = None
    interesting_patterns: list = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.interesting_patterns is None:
            self.interesting_patterns = []


def scan_project(project_path: Path) -> ProjectScan:
    """Scan a project for relevant patterns and dependencies."""
    scan = ProjectScan(name=project_path.name, path=project_path)

    # Check for pyproject.toml
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        scan.has_pyproject = True
        try:
            import tomllib

            with open(pyproject, "rb") as f:
                data = tomllib.load(f)

            # Extract Python version
            if "project" in data:
                scan.python_version = data["project"].get("requires-python")
                scan.dependencies = data["project"].get("dependencies", [])

            # Check for Typer, FastAPI, etc
            deps_str = " ".join(scan.dependencies)
            if "typer" in deps_str.lower():
                scan.cli_framework = "typer"
            elif "click" in deps_str.lower():
                scan.cli_framework = "click"
            elif "argparse" in deps_str.lower():
                scan.cli_framework = "argparse"

            # Check for test setup
            if "pytest" in deps_str.lower():
                scan.testing_setup = "pytest"
            elif "unittest" in deps_str.lower():
                scan.testing_setup = "unittest"
        except Exception as e:
            print(f"  (could not parse {pyproject.name}: {e})")

    # Check for justfile patterns
    justfile = project_path / "justfile"
    if justfile.exists():
        scan.interesting_patterns.append("justfile (task runner)")

    # Check for .pre-commit-config.yaml
    precommit = project_path / ".pre-commit-config.yaml"
    if precommit.exists():
        scan.interesting_patterns.append("pre-commit hooks")

    # Check for uv.lock
    uv_lock = project_path / "uv.lock"
    if uv_lock.exists():
        scan.interesting_patterns.append("uv package manager")

    # Check for CI/CD
    ci_dir = project_path / ".github" / "workflows"
    if ci_dir.exists():
        scan.interesting_patterns.append(f"GitHub Actions ({len(list(ci_dir.glob('*.yml')))} workflows)")

    return scan


def main():
    base = Path.home() / "projects" / "baseline0"
    projects_to_scan = [
        "learn-ollama",
        "etf-pulse",
        "task-tracker",
        "accidentallyadjacent",
    ]

    findings = []
    print("Scanning related projects for best practices...\n")

    for proj_name in projects_to_scan:
        proj_path = base / proj_name
        if not proj_path.exists():
            print(f"⊘ {proj_name}: not found at {proj_path}")
            continue

        print(f"✓ Scanning {proj_name}...")
        scan = scan_project(proj_path)
        findings.append(scan)

    # Generate report
    report_path = Path(__file__).parent / "scan_findings.md"
    with open(report_path, "w") as f:
        f.write("# Related Projects Scan\n\n")
        f.write("Findings from scanning sibling projects for best practices, libraries, and patterns.\n\n")

        for scan in findings:
            f.write(f"## {scan.name}\n\n")
            f.write(f"**Path:** `{scan.path.relative_to(base)}`\n\n")

            if scan.has_pyproject:
                f.write(f"**Python Version:** {scan.python_version or 'Not specified'}\n\n")

                if scan.cli_framework:
                    f.write(f"**CLI Framework:** {scan.cli_framework}\n\n")

                if scan.testing_setup:
                    f.write(f"**Testing:** {scan.testing_setup}\n\n")

                if scan.dependencies:
                    f.write("**Key Dependencies:**\n")
                    for dep in sorted(scan.dependencies)[:10]:  # First 10
                        f.write(f"- {dep}\n")
                    if len(scan.dependencies) > 10:
                        f.write(f"- ... and {len(scan.dependencies) - 10} more\n")
                    f.write("\n")
            else:
                f.write("(No pyproject.toml found)\n\n")

            if scan.interesting_patterns:
                f.write("**Patterns Observed:**\n")
                for pattern in scan.interesting_patterns:
                    f.write(f"- {pattern}\n")
                f.write("\n")

            f.write("---\n\n")

        # Summary & decision points
        f.write("## Summary & Decision Points\n\n")
        f.write("Use this scan to identify:\n")
        f.write("1. **Proven patterns:** What works in active projects?\n")
        f.write("2. **Library ecosystem:** Which libraries are used consistently?\n")
        f.write("3. **Architecture:** How are CLI/testing/deployment structured?\n")
        f.write("4. **Tooling:** Are there gaps we should fill in malta?\n\n")
        f.write("### Next Steps\n")
        f.write("- [ ] Review CLI framework choice (Typer vs alternatives)\n")
        f.write("- [ ] Check testing best practices across projects\n")
        f.write("- [ ] Identify dependency patterns for demos/apps\n")
        f.write("- [ ] Consider pre-commit/CI/CD setup for malta\n")

    print(f"\n✓ Findings written to {report_path}")
    print("  Review and decide next steps for malta/demos")


if __name__ == "__main__":
    main()

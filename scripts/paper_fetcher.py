#!/usr/bin/env python3
"""
Fetch membrane's curated paper list into reference/lit_review/.

Downloading, per-domain pacing, PDF validation, the manifest and the audit log come from tool-lit-review's
`fetch-list` command, which this script runs in a subprocess. This script keeps what is membrane's: the curated list,
the University of Michigan library report, the selection rules, the CLI, and the .fetch.log file.

Selection (--retry and --clean are required; pass true or false):
    --retry false --clean false   papers with no manifest entry yet (successful and failed papers are skipped)
    --retry true                  also papers whose manifest status is not success (failed)
    --clean true                  clear the manifest first, then select every paper

Papers that need UofM library access are not requested. They are recorded as failed and listed in LIBRARY_LOOKUP.txt.

Output (reference/lit_review/):
    pdf/<paper_id>.pdf        saved PDFs
    .manifest.json            one entry per paper id: paper_id, status (saved | cached | failed), source, path,
                              sha256, url, error, timestamp. Read by scripts/paper_status.py.
    fetch_audit.jsonl         every request and its outcome
    .fetch.log                run log
    LIBRARY_LOOKUP.txt        papers needing UofM library access

A manifest in an older format stops the run: move it aside and re-run.

Usage:
    python scripts/paper_fetcher.py --retry false --clean false   # Fetch new papers
    python scripts/paper_fetcher.py --retry true --clean false    # Also re-attempt failed papers
    python scripts/paper_fetcher.py --retry false --clean true     # Clear the manifest and start again
"""

import json
import logging
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any

import typer

OUTPUT_DIR = Path("reference/lit_review")
MANIFEST_NAME = ".manifest.json"
FETCH_LIST_NAME = ".fetch_list.json"
LOG_PATH = OUTPUT_DIR / ".fetch.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
LIBRARY_LOOKUP_NAME = "LIBRARY_LOOKUP.txt"
REQUEST_TIMEOUT_SECONDS = 10.0
MIN_DELAY_SECONDS = 2.0
SUCCESS_STATUSES = frozenset({"saved", "cached"})
TOOL_LIT_REVIEW_PROJECT = Path(__file__).resolve().parent.parent.parent / "tool-lit-review"

# The keys tool-lit-review writes for each manifest entry. A row without them is an old-format manifest.
MANIFEST_ROW_KEYS = frozenset({"paper_id", "status", "source", "path", "sha256", "url", "error", "timestamp"})


class TrueFalse(StrEnum):
    """A required boolean option value, passed as `true` or `false`."""

    TRUE = "true"
    FALSE = "false"


class ManifestError(ValueError):
    """The fetch manifest exists but is not in the format tool-lit-review writes."""


class FetchListFailed(RuntimeError):
    """tool-lit-review fetch-list exited with an error. The message carries its stderr."""


app = typer.Typer(
    help=(
        "Fetch the curated membrane paper list with rate limiting and caching. "
        "Output: reference/lit_review/pdf/<paper_id>.pdf and .manifest.json (status: saved, cached, failed)."
    ),
    add_completion=False,
)
logger = logging.getLogger(__name__)


def configure_logging(log_path: Path = LOG_PATH) -> None:
    """Send INFO logs to the fetch log file and to stdout."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout),
        ],
    )


@dataclass(frozen=True)
class CuratedPaper:
    """One paper on membrane's list. The fields tool-lit-review fetches by are paper_id, title, arxiv_id and doi.

    authors, year and the UofM library flags are membrane's own.
    """

    paper_id: str
    title: str = ""
    arxiv_id: str | None = None
    doi: str | None = None
    authors: str = ""
    year: int = 0
    requires_library: bool = False  # True if needs UofM library access
    is_open_access: bool = False  # True if genuinely open access (MDPI, IEEE Access)

    @property
    def needs_library(self) -> bool:
        """Paywalled: not open access, and marked as needing UofM library access."""
        return self.requires_library and not self.is_open_access


def load_paper_sources() -> list[CuratedPaper]:
    """Membrane's curated paper list.

    Placeholder DOIs ('...xxx') are kept as written, so the library report still shows them. The old journal and
    search URLs are not kept: tool-lit-review fetches arXiv, DOI and Semantic Scholar only, and those URLs were
    landing or search pages that never returned a PDF.
    """
    return [
        CuratedPaper(
            paper_id="Zhang_QuantumInspiredMembrane_2023",
            title="Quantum-Inspired Membrane Computing: A Survey and Perspective",
            authors="Gexiang Zhang, Marian Gheorghe, Chao Wu",
            year=2023,
            doi="10.3390/e25020xxx",
            is_open_access=True,  # MDPI Entropy is open access
        ),
        CuratedPaper(
            paper_id="Zhang_RealCodedQuantum_2021",
            title="Real-Coded Quantum-Inspired Evolutionary Membrane Algorithm for Numerical Optimization",
            authors="Gexiang Zhang, Haina Rong, Ferrante Neri, Mario J. Pérez-Jiménez",
            year=2021,
            doi="10.1016/j.ins.2021.xxx",
            requires_library=True,  # Information Sciences (paywalled)
        ),
        CuratedPaper(
            paper_id="Diaz_SoftwareToolsMembraneComputing_2010",
            title="Software Tools for Membrane Computing: P-Lingua and MeCoSim",
            authors="Diego Díaz-Pernil, Agustín Berciano, Fernando Peña-Cantillana, Miguel A. Gutiérrez-Naranjo",
            year=2010,
            doi="10.15837/ijccc.2010.2.xxx",
            requires_library=True,
        ),
        CuratedPaper(
            paper_id="Leporati_SimulatingQuantumCircuits_2005",
            title="Simulating Quantum Circuits with P Systems with Active Membranes",
            authors="Alberto Leporati, Claudio Zandron, Ferruccio Ferretti, Giancarlo Mauri",
            year=2005,
            doi="10.1016/j.tcs.2004.xxx",
            requires_library=True,  # TCS (paywalled)
        ),
        CuratedPaper(
            paper_id="Xiao_QuantumInspiredMembrane_2022",
            title="A Quantum-Inspired Membrane Algorithm for Combinatorial Optimization Problems",
            authors="Jiao Xiao, Gexiang Zhang, Xiyu Liu",
            year=2022,
            doi="10.3390/math10010xxx",
            is_open_access=True,  # MDPI Mathematics (open access)
        ),
        CuratedPaper(
            paper_id="Paun_OpenProblemsMembraneComputing_2019",
            title="Open Problems in Membrane Computing: A Retrospective and Future Outlook",
            authors="Gheorghe Păun, Linqiang Pan, Mario J. Pérez-Jiménez",
            year=2019,
            doi="10.1007/s41965-019-xxxxx",
            requires_library=True,  # Springer (likely paywalled)
        ),
        CuratedPaper(
            paper_id="Liu_NovelHybridQuantum_2021",
            title="A Novel Hybrid Quantum-Inspired Membrane Algorithm for Global Numerical Optimization",
            authors="Xiangrong Liu, Gexiang Zhang, Thomas Back",
            year=2021,
            doi="10.1109/ACCESS.2021.xxxxx",
            is_open_access=True,  # IEEE Access (open access)
        ),
        CuratedPaper(
            paper_id="Nishimura_QuantumPSystems_2022",
            title="Quantum P Systems: Theoretical Framework and Computational Power",
            authors="Harumichi Nishimura, Jiang Zhao",
            year=2022,
            doi="10.1016/j.ijuc.2022.xxx",
            requires_library=True,  # IJUC (check arXiv first; no arXiv id is recorded yet)
        ),
        CuratedPaper(
            paper_id="Valencia_ParallelImplementation_2023",
            title="Parallel Implementation of Quantum-Inspired Membrane Algorithms on GPUs",
            authors="Luis Valencia-Cabrera, David Orellana-Martín, Mario J. Pérez-Jiménez",
            year=2023,
            doi="10.3390/app13010xxx",
            is_open_access=True,  # MDPI Applied Sciences (open access)
        ),
        CuratedPaper(
            paper_id="Liu_MembranComputingQuantumInfo_2020",
            title="Membrane Computing and Quantum Information Processing: A Synthesis",
            authors="Xiyu Liu, Thomas Hinze, Gexiang Zhang",
            year=2020,
            doi="10.1016/j.biosystems.2020.xxx",
            requires_library=True,  # Biosystems (paywalled)
        ),
    ]


def read_manifest(manifest_path: Path) -> dict[str, dict[str, Any]]:
    """The manifest rows keyed by paper id. Empty when there is no manifest yet.

    Raises ManifestError when the file is unreadable or a row is not in tool-lit-review's format.
    """
    if not manifest_path.exists():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ManifestError(f"Cannot read fetch manifest {manifest_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError(f"Cannot read fetch manifest {manifest_path}: expected a JSON object")
    for paper_id, row in data.items():
        if not isinstance(row, dict) or not row.keys() >= MANIFEST_ROW_KEYS:
            raise ManifestError(
                f"Cannot read fetch manifest {manifest_path}: entry {paper_id!r} is not in fetch format"
            )
    return data


def write_manifest(manifest_path: Path, rows: dict[str, dict[str, Any]]) -> None:
    """Write the manifest rows, sorted by paper id, in the format tool-lit-review uses."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {paper_id: rows[paper_id] for paper_id in sorted(rows)}
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def papers_to_fetch(papers: list[CuratedPaper], manifest: dict[str, dict[str, Any]], retry: bool) -> list[CuratedPaper]:
    """Select the papers this run attempts.

    Default: papers with no manifest entry. --retry also includes papers whose status is not success.
    """
    selected: list[CuratedPaper] = []
    for paper in papers:
        previous = manifest.get(paper.paper_id)
        if previous is None or (retry and previous.get("status") not in SUCCESS_STATUSES):
            selected.append(paper)
    return selected


def library_gap_row(paper: CuratedPaper) -> dict[str, Any]:
    """The manifest row for a paywalled paper. It is recorded as failed without any network request."""
    return {
        "paper_id": paper.paper_id,
        "status": "failed",
        "source": None,
        "path": None,
        "sha256": None,
        "url": None,
        "error": f"Requires UofM library access (DOI: {paper.doi})",
        "timestamp": datetime.now(UTC).isoformat(),
        "licence": None,
    }


def fetch_list_row(paper: CuratedPaper) -> dict[str, Any]:
    """The record tool-lit-review's fetch-list reads for one paper."""
    return {"paper_id": paper.paper_id, "title": paper.title, "arxiv_id": paper.arxiv_id, "doi": paper.doi}


def invoke_fetch_list(list_path: Path, output_dir: Path, clean: bool) -> None:
    """Run tool-lit-review's fetch-list over the list file. Its output goes to the membrane log.

    Raises FetchListFailed when the command exits non-zero.
    """
    command = [
        "uv",
        "run",
        "--project",
        str(TOOL_LIT_REVIEW_PROJECT.resolve()),
        "tool-lit-review",
        "fetch-list",
        "--records",
        str(list_path.resolve()),
        "--output",
        str(output_dir.resolve()),
        "--min-delay",
        str(MIN_DELAY_SECONDS),
        "--timeout",
        str(REQUEST_TIMEOUT_SECONDS),
        "--clean",
        "true" if clean else "false",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    for line in completed.stdout.splitlines():
        logger.info(f"   {line}")
    if completed.returncode != 0:
        raise FetchListFailed(f"tool-lit-review fetch-list exited {completed.returncode}: {completed.stderr.strip()}")


def generate_library_lookup(papers: list[CuratedPaper], output_dir: Path) -> None:
    """Write the library-access report for papers that need UofM library access."""
    library_papers = [p for p in papers if p.needs_library]
    if not library_papers:
        return

    lookup_path = output_dir / LIBRARY_LOOKUP_NAME
    with open(lookup_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PAPERS REQUIRING UOFM LIBRARY ACCESS\n")
        f.write("=" * 80 + "\n\n")
        f.write("These papers are paywalled. Access via:\n")
        f.write("  1. UofM Libraries website (alumni login)\n")
        f.write("  2. On-campus access to full databases\n")
        f.write("  3. Interlibrary loan (ILL) request\n\n")

        for i, paper in enumerate(library_papers, 1):
            f.write(f"{i}. {paper.title}\n")
            f.write(f"   Authors: {paper.authors} ({paper.year})\n")
            if paper.doi:
                f.write(f"   DOI: {paper.doi}\n")
            f.write("   → Search via UofM Libraries\n")
            f.write("\n")

    logger.info(f"📋 Library lookup: {lookup_path}")


def generate_status_report(manifest: dict[str, dict[str, Any]], output_dir: Path) -> None:
    """Log a summary of the manifest."""
    total = len(manifest)
    succeeded = sum(1 for r in manifest.values() if r.get("status") in SUCCESS_STATUSES)
    failed = total - succeeded

    logger.info("\n" + "=" * 80)
    logger.info("📊 FETCH SUMMARY")
    logger.info(f"   Total papers: {total}")
    logger.info(f"   Fetched: {succeeded}")
    logger.info(f"   Failed: {failed}")
    if total > 0:
        logger.info(f"   Success rate: {100 * succeeded / total:.0f}%")

    if failed > 0:
        logger.info("\n⚠️  Failed papers:")
        for paper_id, result in manifest.items():
            if result.get("status") not in SUCCESS_STATUSES:
                logger.info(f"   - {paper_id}: {result.get('error')}")

    logger.info(f"\n📁 Manifest: {output_dir / MANIFEST_NAME}")
    logger.info(f"📁 Papers: {output_dir}/")
    logger.info("=" * 80)


def run_session(
    papers: list[CuratedPaper],
    retry: bool,
    clean: bool,
    output_dir: Path = OUTPUT_DIR,
    invoke: Callable[[Path, Path, bool], None] = invoke_fetch_list,
) -> None:
    """Select the papers, fetch the open ones through tool-lit-review, record the paywalled ones, then report.

    clean=True makes every paper selectable again: tool-lit-review's fetch-list deletes the manifest first.
    The manifest is always read first, so an old-format manifest stops the run even with clean.
    """
    manifest_path = output_dir / MANIFEST_NAME
    existing = read_manifest(manifest_path)
    selected = papers_to_fetch(papers, {} if clean else existing, retry)

    to_request: list[CuratedPaper] = []
    library_gaps: list[CuratedPaper] = []
    for paper in selected:
        if paper.needs_library and not (output_dir / "pdf" / f"{paper.paper_id}.pdf").exists():
            library_gaps.append(paper)
        else:
            to_request.append(paper)

    list_path = output_dir / FETCH_LIST_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    list_path.write_text(
        json.dumps([fetch_list_row(p) for p in to_request], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    # Always invoked, even with nothing to request, so that --clean clears the manifest.
    invoke(list_path, output_dir, clean)
    list_path.unlink()

    rows = read_manifest(manifest_path)  # what fetch-list wrote; empty after --clean if nothing was requested
    for paper in library_gaps:
        logger.info(f"📄 {paper.title}")
        logger.info(f"   Authors: {paper.authors} ({paper.year})")
        logger.info(f"   [Library access required, see {LIBRARY_LOOKUP_NAME}]")
        rows[paper.paper_id] = library_gap_row(paper)
    write_manifest(manifest_path, rows)

    generate_library_lookup(papers, output_dir)
    generate_status_report(rows, output_dir)


@app.command()
def main(
    retry: Annotated[TrueFalse, typer.Option("--retry", help="true also re-attempts papers whose last fetch failed")],
    clean: Annotated[
        TrueFalse, typer.Option("--clean", help="true clears the manifest first, then selects every paper")
    ],
) -> None:
    """Fetch the curated membrane paper list with rate limiting and caching.

    Writes reference/lit_review/pdf/<paper_id>.pdf and .manifest.json (status: saved, cached, failed).
    Without --retry or --clean: papers with no manifest entry yet. Use --retry true for failed papers.
    """
    configure_logging()
    logger.info("🚀 Paper fetcher (tool-lit-review sources, membrane paper list)")
    try:
        run_session(load_paper_sources(), retry=retry == TrueFalse.TRUE, clean=clean == TrueFalse.TRUE)
    except ManifestError as exc:
        logger.error(f"{exc}")
        logger.error(
            f"Move the manifest aside (mv {OUTPUT_DIR / MANIFEST_NAME} {OUTPUT_DIR / '.manifest.v1.json'}) and re-run."
        )
        raise typer.Exit(code=1) from exc
    except FetchListFailed as exc:
        logger.error(f"{exc}")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()

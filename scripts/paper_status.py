#!/usr/bin/env python3
"""
Paper status report: read the fetch manifest and show which papers are available for review.

Outputs:
- Console report (ready-to-review papers, pending papers, missing PDFs)
- Integration hints for LITERATURE_REVIEW.md

The manifest is written by tool_lit_review.fetch (through scripts/paper_fetcher.py). It has one entry per paper id,
with status 'saved', 'cached' or 'failed', plus path, source, error and timestamp. It stores no titles, so titles
come from membrane's curated list.
"""

import json
import sys
from pathlib import Path
from typing import Any

MANIFEST_PATH = Path("reference/lit_review/.manifest.json")
SUCCESS_STATUSES = frozenset({"saved", "cached"})  # same as scripts/paper_fetcher.py
REPO_ROOT = Path(__file__).resolve().parent.parent

Entry = tuple[str, dict[str, Any]]  # (paper id, manifest row)
AvailableEntry = tuple[str, dict[str, Any], float]  # (paper id, manifest row, size in MB)


def load_manifest(manifest_path: Path) -> dict[str, dict[str, Any]]:
    """Load fetch manifest."""
    if not manifest_path.exists():
        print("❌ No manifest found. Run: python scripts/paper_fetcher.py --retry false --clean false")
        sys.exit(1)

    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def load_titles() -> dict[str, str]:
    """Titles from membrane's curated paper list, keyed by paper id."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.paper_fetcher import load_paper_sources

    return {paper.paper_id: paper.title for paper in load_paper_sources()}


def _short_title(title: str) -> str:
    return title[:60] + "..." if len(title) > 60 else title


def generate_console_report(
    manifest: dict[str, dict[str, Any]], titles: dict[str, str]
) -> tuple[list[AvailableEntry], list[Entry], list[Entry]]:
    """Print the status report. Returns (available, unavailable, missing) lists of (paper id, manifest row, ...)."""
    print("\n" + "=" * 80)
    print("📚 LITERATURE REVIEW STATUS")
    print("=" * 80)

    available: list[AvailableEntry] = []
    unavailable: list[Entry] = []
    missing: list[Entry] = []

    for paper_id, result in manifest.items():
        if result.get("status") in SUCCESS_STATUSES:
            path = result.get("path")
            if path and Path(path).exists():
                size_mb = Path(path).stat().st_size / (1024 * 1024)
                available.append((paper_id, result, size_mb))
            else:
                missing.append((paper_id, result))
        else:
            unavailable.append((paper_id, result))

    # Report available
    if available:
        print(f"\n✅ AVAILABLE ({len(available)} papers ready for review):")
        print("-" * 80)
        for paper_id, result, size_mb in available:
            print(f"  [{paper_id}]")
            print(f"    Title: {_short_title(titles.get(paper_id, paper_id))}")
            print(f"    Source: {result.get('source') or result['status']} | Size: {size_mb:.1f} MB")
            print(f"    Fetched: {result['timestamp'][:10]}")
            print()

    # Report unavailable
    if unavailable:
        print(f"\n⏳ PENDING ({len(unavailable)} papers):")
        print("-" * 80)
        for paper_id, result in unavailable:
            title = titles.get(paper_id, paper_id)
            print(f"  [{paper_id}]")
            print(f"    Title: {_short_title(title)}")
            print(f"    Last attempt: {result.get('timestamp', 'N/A')[:10]}")
            print(f"    Error: {result.get('error') or 'Unknown'}")
            print(f"    → Manual search: https://scholar.google.com/scholar?q={title[:40]}")
            print()

    # Report corrupted cache
    if missing:
        print(f"\n⚠️  CORRUPTED CACHE ({len(missing)} papers):")
        print("-" * 80)
        for paper_id, result in missing:
            print(f"  {paper_id}: {result.get('path')} missing")
            print("    → Delete manifest and re-fetch: python scripts/paper_fetcher.py --retry false --clean true")
        print()

    # Summary
    total = len(manifest)
    pct = 100 * len(available) / total if total > 0 else 0
    print("=" * 80)
    print(f"Summary: {len(available)}/{total} papers available ({pct:.0f}%)")
    print("=" * 80)

    return available, unavailable, missing


def generate_lit_review_hints(available: list[AvailableEntry], titles: dict[str, str]) -> None:
    """Generate hints for updating LITERATURE_REVIEW.md."""
    if not available:
        return

    print("\n💡 NEXT STEPS:")
    print("-" * 80)
    print("For each available paper, fill in docs/LITERATURE_REVIEW.md:")
    print()
    for paper_id, result, _size_mb in available[:3]:  # Show first 3
        title_short = titles.get(paper_id, paper_id).split(":")[0][:50]
        print(f"  ## {paper_id}")
        print(f"  - **Paper:** {title_short}...")
        print(f"  - **Location:** {result.get('path')}")
        print("  - **Key finding:** [TODO: read and extract]")
        print()

    print(f"  ... and {len(available) - 3} more papers")
    print()
    print("See docs/LITERATURE_REVIEW.md for template fields:")
    print("  - Key contribution (1 sentence)")
    print("  - Methods used")
    print("  - CEC2017 results (if applicable)")
    print("  - Relevant quotes")
    print("  - How it relates to QIPS")


def main() -> None:
    """Generate status report."""
    manifest = load_manifest(MANIFEST_PATH)
    titles = load_titles()
    available, unavailable, missing = generate_console_report(manifest, titles)

    generate_lit_review_hints(available, titles)

    # Exit with useful code
    if len(unavailable) > 0:
        print("\n→ Re-run fetcher: python scripts/paper_fetcher.py --retry true --clean false")
    if len(missing) > 0:
        print("\n→ Clean and restart: python scripts/paper_fetcher.py --retry false --clean true")


if __name__ == "__main__":
    main()

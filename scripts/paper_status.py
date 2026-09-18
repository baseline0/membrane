#!/usr/bin/env python3
"""
Paper status report: Generate from manifest, show which papers are available for review.

Outputs:
- Console report (ready-to-review papers)
- HTML report (optional, for browsing)
- Integration hints for LITERATURE_REVIEW.md
"""

import json
import sys
from pathlib import Path
from typing import Dict, List


def load_manifest(manifest_path: Path) -> Dict:
    """Load fetch manifest."""
    if not manifest_path.exists():
        print("❌ No manifest found. Run: python scripts/paper_fetcher.py")
        sys.exit(1)

    with open(manifest_path) as f:
        return json.load(f)


def generate_console_report(manifest: Dict, papers_dir: Path):
    """Generate console report of available papers."""
    print("\n" + "=" * 80)
    print("📚 LITERATURE REVIEW STATUS")
    print("=" * 80)

    available = []
    unavailable = []
    missing = []

    for name, result in manifest.items():
        if result["success"]:
            filepath = Path(result["filepath"])
            if filepath.exists():
                size_mb = filepath.stat().st_size / (1024 * 1024)
                available.append((name, result, size_mb))
            else:
                missing.append((name, result))
        else:
            unavailable.append((name, result))

    # Report available
    if available:
        print(f"\n✅ AVAILABLE ({len(available)} papers ready for review):")
        print("-" * 80)
        for name, result, size_mb in available:
            title = result["title"][:60] + "..." if len(result["title"]) > 60 else result["title"]
            print(f"  [{name}]")
            print(f"    Title: {title}")
            print(f"    Source: {result['source']} | Size: {size_mb:.1f} MB")
            print(f"    Fetched: {result['timestamp'][:10]}")
            print()

    # Report unavailable
    if unavailable:
        print(f"\n⏳ PENDING ({len(unavailable)} papers):")
        print("-" * 80)
        for name, result in unavailable:
            title = result["title"][:60] + "..." if len(result["title"]) > 60 else result["title"]
            print(f"  [{name}]")
            print(f"    Title: {title}")
            print(f"    Last attempt: {result.get('timestamp', 'N/A')[:10]}")
            print(f"    Error: {result.get('error', 'Unknown')}")
            print(f"    → Manual search: https://scholar.google.com/scholar?q={result['title'][:40]}")
            print()

    # Report corrupted cache
    if missing:
        print(f"\n⚠️  CORRUPTED CACHE ({len(missing)} papers):")
        print("-" * 80)
        for name, result in missing:
            print(f"  {name}: {result['filepath']} missing")
            print("    → Delete manifest and re-fetch: python scripts/paper_fetcher.py --clean")
        print()

    # Summary
    total = len(manifest)
    pct = 100 * len(available) / total if total > 0 else 0
    print("=" * 80)
    print(f"Summary: {len(available)}/{total} papers available ({pct:.0f}%)")
    print("=" * 80)

    return available, unavailable, missing


def generate_lit_review_hints(available: List):
    """Generate hints for updating LITERATURE_REVIEW.md."""
    if not available:
        return

    print("\n💡 NEXT STEPS:")
    print("-" * 80)
    print("For each available paper, fill in docs/LITERATURE_REVIEW.md:")
    print()
    for name, result, size_mb in available[:3]:  # Show first 3
        title_short = result["title"].split(":")[0][:50]
        print(f"  ## {name}")
        print(f"  - **Paper:** {title_short}...")
        print(f"  - **Location:** reference/lit_review/{name}.pdf")
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


def main():
    """Generate status report."""
    manifest_path = Path("reference/lit_review/.manifest.json")
    papers_dir = Path("reference/lit_review")

    manifest = load_manifest(manifest_path)
    available, unavailable, missing = generate_console_report(manifest, papers_dir)

    generate_lit_review_hints(available)

    # Exit with useful code
    if len(unavailable) > 0:
        print("\n→ Re-run fetcher: python scripts/paper_fetcher.py --retry")
    if len(missing) > 0:
        print("\n→ Clean and restart: python scripts/paper_fetcher.py --clean")


if __name__ == "__main__":
    main()

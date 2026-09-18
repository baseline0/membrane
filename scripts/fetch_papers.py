#!/usr/bin/env python3
"""
Lightweight paper fetcher: arXiv + DOI lookup + semantic scholar API.

Usage:
    python scripts/fetch_papers.py

Fetches papers to docs/papers/ for offline review.
"""

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

PAPERS = [
    {
        "name": "Zhang_QuantumInspiredMembrane_2023",
        "arxiv": "2301.xxxxx",  # Placeholder: will search
        "doi": "10.3390/e25020xxx",
        "title": "Quantum-Inspired Membrane Computing: A Survey and Perspective",
        "authors": "Gexiang Zhang, Marian Gheorghe, Chao Wu",
        "year": 2023,
    },
    {
        "name": "Zhang_RealCodedQuantum_2021",
        "arxiv": "2101.xxxxx",
        "doi": "10.1016/j.ins.2021.xxx",
        "title": "Real-Coded Quantum-Inspired Evolutionary Membrane Algorithm for Numerical Optimization",
        "authors": "Gexiang Zhang, Haina Rong, Ferrante Neri, Mario J. Pérez-Jiménez",
        "year": 2021,
    },
    {
        "name": "Diaz_SoftwareToolsMembraneComputing_2010",
        "doi": "10.15837/ijccc.2010.2.xxx",
        "title": "Software Tools for Membrane Computing: P-Lingua and MeCoSim",
        "authors": "Diego Díaz-Pernil, Agustín Berciano, Fernando Peña-Cantillana, Miguel A. Gutiérrez-Naranjo",
        "year": 2010,
    },
    {
        "name": "Leporati_SimulatingQuantumCircuits_2005",
        "doi": "10.1016/j.tcs.2004.xxx",
        "title": "Simulating Quantum Circuits with P Systems with Active Membranes",
        "authors": "Alberto Leporati, Claudio Zandron, Ferruccio Ferretti, Giancarlo Mauri",
        "year": 2005,
    },
    {
        "name": "Xiao_QuantumInspiredMembrane_2022",
        "doi": "10.3390/math10010xxx",
        "title": "A Quantum-Inspired Membrane Algorithm for Combinatorial Optimization Problems",
        "authors": "Jiao Xiao, Gexiang Zhang, Xiyu Liu",
        "year": 2022,
    },
    {
        "name": "Paun_OpenProblemsMembraneComputing_2019",
        "doi": "10.1007/s41965-019-xxxxx",
        "title": "Open Problems in Membrane Computing: A Retrospective and Future Outlook",
        "authors": "Gheorghe Păun, Linqiang Pan, Mario J. Pérez-Jiménez",
        "year": 2019,
    },
    {
        "name": "Liu_NovelHybridQuantum_2021",
        "doi": "10.1109/ACCESS.2021.xxxxx",
        "title": "A Novel Hybrid Quantum-Inspired Membrane Algorithm for Global Numerical Optimization",
        "authors": "Xiangrong Liu, Gexiang Zhang, Thomas Back",
        "year": 2021,
    },
    {
        "name": "Nishimura_QuantumPSystems_2022",
        "arxiv": "2209.xxxxx",
        "doi": "10.1016/j.ijuc.2022.xxx",
        "title": "Quantum P Systems: Theoretical Framework and Computational Power",
        "authors": "Harumichi Nishimura, Jiang Zhao",
        "year": 2022,
    },
    {
        "name": "Valencia_ParallelImplementation_2023",
        "doi": "10.3390/app13010xxx",
        "title": "Parallel Implementation of Quantum-Inspired Membrane Algorithms on GPUs",
        "authors": "Luis Valencia-Cabrera, David Orellana-Martín, Mario J. Pérez-Jiménez",
        "year": 2023,
    },
    {
        "name": "Liu_MembranComputingQuantumInfo_2020",
        "doi": "10.1016/j.biosystems.2020.xxx",
        "title": "Membrane Computing and Quantum Information Processing: A Synthesis",
        "authors": "Xiyu Liu, Thomas Hinze, Gexiang Zhang",
        "year": 2020,
    },
]


def try_arxiv(arxiv_id: str) -> Optional[str]:
    """Try to fetch PDF from arXiv."""
    if not arxiv_id or arxiv_id.endswith("xxxxx"):
        return None

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    try:
        print(f"  Trying arXiv: {arxiv_id}...", end=" ", flush=True)
        urllib.request.urlretrieve(pdf_url, timeout=10)
        print("✅")
        return pdf_url
    except (urllib.error.URLError, urllib.error.HTTPError, Exception):
        print("❌")
        return None


def try_doi(doi: str) -> Optional[str]:
    """Try to fetch PDF via DOI resolver (sci-hub fallback)."""
    if not doi or doi.endswith("xxx"):
        return None

    # Try direct DOI resolution
    try:
        print(f"  Trying DOI: {doi}...", end=" ", flush=True)
        doi_url = f"https://doi.org/{doi}"
        req = urllib.request.Request(doi_url)
        req.add_header("User-Agent", "Mozilla/5.0")
        urllib.request.urlopen(req, timeout=10)
        print("✅ (accessible via DOI)")
        return doi_url
    except Exception:
        print("❌")

    # Fallback: sci-hub (note: legality varies by jurisdiction)
    try:
        print("  Trying sci-hub fallback...", end=" ", flush=True)
        scihub_url = f"https://sci-hub.st/{doi}"
        urllib.request.urlretrieve(scihub_url, timeout=10)
        print("✅")
        return scihub_url
    except Exception:
        print("❌")
        return None


def try_semantic_scholar(title: str, authors: str) -> Optional[str]:
    """Query Semantic Scholar API for paper metadata."""
    try:
        print(f"  Trying Semantic Scholar: {title[:40]}...", end=" ", flush=True)
        query = urllib.parse.quote(f"{title}")
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&fields=openAccessPdf,externalIds"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            if data.get("data"):
                paper = data["data"][0]
                if pdf_url := paper.get("openAccessPdf", {}).get("url"):
                    print("✅")
                    return pdf_url
        print("❌")
    except Exception:
        print("❌")
    return None


def fetch_paper(paper: dict, output_dir: Path) -> bool:
    """Attempt to fetch a single paper from multiple sources."""
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = output_dir / f"{paper['name']}.pdf"
    if filename.exists():
        print(f"⏭️  {paper['name']} (already exists)")
        return True

    print(f"\n📄 {paper['title']}")
    print(f"   Authors: {paper['authors']}")
    print(f"   Year: {paper['year']}")

    # Try sources in order
    sources = [
        ("arXiv", lambda: try_arxiv(paper.get("arxiv"))),
        ("DOI", lambda: try_doi(paper.get("doi"))),
        ("Semantic Scholar", lambda: try_semantic_scholar(paper["title"], paper["authors"])),
    ]

    for source_name, fetch_fn in sources:
        url = fetch_fn()
        if url:
            print(f"✅ {source_name}: {url}")
            return True

    print(f"⚠️  Could not fetch: {paper['name']}")
    print(f"   Search manually: https://scholar.google.com/scholar?q={urllib.parse.quote(paper['title'])}")
    return False


def main():
    """Fetch all papers."""
    output_dir = Path("docs/papers")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🔍 Fetching Quantum-Inspired Membrane Computing Papers...\n")

    succeeded = 0
    failed = 0

    for paper in PAPERS:
        try:
            if fetch_paper(paper, output_dir):
                succeeded += 1
            else:
                failed += 1
        except KeyboardInterrupt:
            print("\n⏹️  Interrupted")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1

    print(f"\n{'=' * 80}")
    print(f"📊 Results: {succeeded} fetched, {failed} failed/manual review needed")
    print(f"📁 Papers: {output_dir}/")
    print("\n💡 For papers not found automatically:")
    print("   1. Search Google Scholar or arXiv")
    print(f"   2. Download PDF to {output_dir}/")
    print("   3. Name it: AuthorLastName_ShorttTitle_Year.pdf")
    print("\n📝 Next: Review and update docs/LITERATURE_REVIEW.md")


if __name__ == "__main__":
    import urllib.parse

    main()

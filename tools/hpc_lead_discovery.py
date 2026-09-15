#!/usr/bin/env python3
"""
HPC Faculty Discovery Pipeline for Membrane Computing Collaboration.

Orchestrates entity mapping, resolution, enrichment, and lead scoring to identify
academic faculty with HPC allocations who could benefit from membrane computing
collaboration.

Pipeline stages:
  1. Search: Web scraping or institution list input
  2. Resolution: Normalize names → ROR IDs, ORCID identifiers (via entity mapping)
  3. Enrichment: Query OpenAlex + ORCID for publications, affiliations, HPC access
  4. Scoring: Rank leads by research relevance + HPC engagement + contact confidence
  5. Export: CSV for manual review + personalized outreach

Usage:
    # Specific institutions
    python tools/hpc_lead_discovery.py \\
      --institutions "UC San Diego" "Georgia Tech" \\
      --output leads.csv --top-n 20

    # From file
    python tools/hpc_lead_discovery.py \\
      --institutions-file docs/outreach/target_institutions.txt \\
      --output full_leads.csv

Scoring formula:
  score = (
    research_relevance * 0.40 +     # Keywords: membrane, GPU, parallel, etc.
    hpc_engagement * 0.30 +         # HPC publications + allocations
    contact_confidence * 0.10 +     # Email verified
    data_confidence * 0.20          # Source reliability (OpenAlex, ORCID, etc.)
  )

Next steps after discovery:
  1. Verify emails via institution directories
  2. Personalize from EMAIL_TEMPLATES.md (5 templates provided)
  3. Log activity in OUTREACH_LOG.md
  4. Follow 12-week plan in GETTING_STARTED.md

Integrates with: baseline0/research/src/research/resolvers/academic_hpc.py
"""

import argparse
import asyncio
import csv
import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)


def validate_dependencies():
    """Check required packages are installed."""
    required = ["pandas"]
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.error(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)


def score_lead(row: pd.Series) -> float:
    """
    Score a faculty lead for outreach priority (0.0–1.0).

    Scoring breakdown:
      - Research relevance (40%): membrane, p-system, GPU, parallel, HPC keywords
      - HPC engagement (30%): confirmed allocations (ACCESS, PRACE, etc.)
      - Contact confidence (10%): verified email address
      - Data confidence (20%): source reliability (OpenAlex, ORCID, etc.)

    Higher scores = better collaboration fit + more reliable contact data.

    Example score interpretation:
      0.85+  : High priority (send email immediately)
      0.70-0.84: Medium (verify email, personalize carefully)
      <0.70  : Lower priority (skip or send follow-up batch)

    Args:
        row: DataFrame row from discovery output

    Returns:
        Composite score 0.0–1.0
    """
    score = 0.0

    # Research relevance (40%)
    # Check for membrane computing + natural computing keywords
    research_keywords = [
        "membrane",
        "p-system",
        "computing",
        "parallel",
        "gpu",
        "hpc",
        "evolutionary",
        "unconventional",
    ]
    research_text = (
        (str(row.get("research_focus", "")).lower())
        + " "
        + (str(row.get("lab_url", "")).lower())
    )
    keyword_matches = sum(1 for kw in research_keywords if kw in research_text)
    score += min(0.40, keyword_matches * 0.08)

    # HPC engagement (30%)
    if row.get("has_hpc_access"):
        score += 0.20
    hpc_mentions = len(row.get("hpc_networks", "").split(";")) if row.get(
        "hpc_networks"
    ) else 0
    score += min(0.10, hpc_mentions * 0.05)

    # Contact confidence (10%)
    if row.get("email") and "@" in str(row.get("email")):
        score += 0.10

    # Data confidence (20%)
    confidence = row.get("confidence_score", 0.5)
    if isinstance(confidence, str):
        try:
            confidence = float(confidence)
        except (ValueError, TypeError):
            confidence = 0.5
    score += confidence * 0.20

    return round(min(1.0, score), 3)


def main():
    """Parse arguments and run discovery pipeline."""
    parser = argparse.ArgumentParser(
        description="Discover HPC faculty collaborators for membrane computing research"
    )
    parser.add_argument(
        "--institutions",
        nargs="+",
        help="Institution names to search",
    )
    parser.add_argument(
        "--institutions-file",
        help="File with institution names (one per line)",
    )
    parser.add_argument(
        "--output",
        default="docs/outreach/discovered_leads.csv",
        help="Output CSV file for lead list",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=50,
        help="Number of top leads to display",
    )
    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=0.5,
        help="Delay between API calls (seconds)",
    )

    args = parser.parse_args()

    def _run_discovery(
        institutions: list,
        institutions_file: Optional[str],
        output: str,
        top_n: int,
        rate_limit_delay: float,
    ):
        """
        Discover HPC faculty collaborators for membrane computing research.

        Pipeline:
        1. Load institution targets
        2. Query OpenAlex + ORCID for faculty
        3. Resolve institutional affiliations (ROR)
        4. Enrich with HPC/publication data
        5. Score and rank by collaboration fit
        6. Export lead list to CSV
        """
        validate_dependencies()

        logger.info("🚀 HPC Faculty Discovery Pipeline")
        logger.info("=" * 60)

        # Load institutions
        target_institutions = list(institutions) if institutions else []

        if institutions_file:
            try:
                with open(institutions_file) as f:
                    file_institutions = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                    target_institutions.extend(file_institutions)
            except FileNotFoundError:
                logger.error(f"Institutions file not found: {institutions_file}")
                sys.exit(1)

        if not target_institutions:
            logger.error("No institutions specified. Use --institutions or --institutions-file")
            sys.exit(1)

        logger.info(f"Target institutions ({len(target_institutions)}):")
        for inst in target_institutions:
            logger.info(f"  • {inst}")

        # NOTE: Full async execution requires AcademicHPCResolver from baseline0/research
        # For this MVP, we'll create a mock dataset and demonstrate the pipeline
        logger.info("\n📊 Simulating discovery (mock data for demo)...")

        # Mock discovery results (in real implementation, this comes from AcademicHPCResolver)
        mock_leads = [
            {
                "faculty_name": "Dr. Jane Smith",
                "institution_name": "UC San Diego",
                "institution_ror_id": "02meqm098",
                "title": "Professor",
                "department": "Computer Science & Engineering",
                "email": "j.smith@ucsd.edu",
                "research_focus": "GPU computing; evolutionary algorithms; natural computing paradigms",
                "lab_url": "https://cs.ucsd.edu/~jsmith/lab",
                "has_hpc_access": True,
                "hpc_networks": "XSEDE; Comet",
                "google_scholar_url": "https://scholar.google.com/citations?user=jsmith",
                "orcid": "0000-0001-2345-6789",
                "confidence_score": 0.92,
                "evidence_sources": "OpenAlex; ORCID; institution_website",
            },
            {
                "faculty_name": "Prof. Michael Chen",
                "institution_name": "Georgia Tech",
                "institution_ror_id": "01n6pte06",
                "title": "Associate Professor",
                "department": "School of Computational Science & Engineering",
                "email": "mchen@cc.gatech.edu",
                "research_focus": "Parallel algorithms; supercomputing; bio-inspired computing",
                "lab_url": "https://www.cc.gatech.edu/~mchen/",
                "has_hpc_access": True,
                "hpc_networks": "ACCESS; Bridges-2",
                "google_scholar_url": "https://scholar.google.com/citations?user=mchen123",
                "orcid": "0000-0002-3456-7890",
                "confidence_score": 0.88,
                "evidence_sources": "OpenAlex; ORCID",
            },
            {
                "faculty_name": "Dr. Sarah Williams",
                "institution_name": "University of Seville",
                "institution_ror_id": "02k5kx123",
                "title": "Researcher",
                "department": "Department of Computer Science",
                "email": "swilliams@us.es",
                "research_focus": "Membrane computing; P systems; formal methods",
                "lab_url": "https://www.us.es/psystems/",
                "has_hpc_access": True,
                "hpc_networks": "PRACE; MareNostrum",
                "google_scholar_url": "https://scholar.google.com/citations?user=sw789",
                "orcid": "0000-0003-4567-8901",
                "confidence_score": 0.95,
                "evidence_sources": "OpenAlex; Google Scholar; institution_website",
            },
        ]

        # Convert to DataFrame
        df = pd.DataFrame(mock_leads)
        logger.info(f"✓ Generated {len(df)} lead records (mock data)")

        # Score and rank
        logger.info("📈 Scoring leads...")
        df["outreach_score"] = df.apply(score_lead, axis=1)
        df = df.sort_values("outreach_score", ascending=False).reset_index(drop=True)

        # Export
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"✓ Results exported → {output_path}")

        # Display top leads
        logger.info(f"\n🎯 Top {min(top_n, len(df))} Leads for Outreach:")
        logger.info("=" * 60)

        for idx, row in df.head(top_n).iterrows():
            logger.info(
                f"\n{idx + 1}. {row['faculty_name']} "
                f"({row['institution_name']}) — Score: {row['outreach_score']}"
            )
            logger.info(f"   Research: {row['research_focus'][:80]}...")
            logger.info(f"   Email: {row['email']}")
            logger.info(f"   HPC Access: {row['hpc_networks']}")

        # Summary statistics
        logger.info("\n📊 Summary Statistics:")
        logger.info(f"   Total Leads: {len(df)}")
        logger.info(f"   High Confidence (>0.85): {len(df[df['confidence_score'] > 0.85])}")
        logger.info(f"   HPC Access Confirmed: {df['has_hpc_access'].sum()}")
        logger.info(f"   Average Score: {df['outreach_score'].mean():.3f}")
        logger.info(f"   Median Score: {df['outreach_score'].median():.3f}")

        logger.info("\n✅ Discovery complete!")
        logger.info(f"Next: Review {output_path} and personalize outreach emails.")
        logger.info("\n📧 EMAIL TEMPLATE (General Research Overlap):")
        logger.info("""
Dear Dr. [NAME],

I've been following your work on [SPECIFIC_PAPER], particularly your approach to
[THEIR_KEYWORD]. I'm developing membrane computing algorithms for [YOUR_AREA], and
believe your expertise would be valuable.

I'd like to propose an unpaid Adjunct Researcher position at [THEIR_UNIVERSITY]:
- Institutional affiliation for my grants
- Access to your HPC infrastructure
- Co-authored publications leveraging your ACCESS/PRACE allocation

In exchange, I'll contribute novel algorithms + grant proposal support.

Would you be open to a 20-minute call? Looking forward to it.

Best,
Mark Alexiuk
        """)
        logger.info("📧 EMAIL TEMPLATE (Membrane Computing Research Hub):")
        logger.info("""
Dear Dr. [NAME],

Your P-Systems group's work on [PAPER] aligns directly with my quantum-inspired
membrane computing research. I believe combining your theoretical expertise with
modern HPC could yield significant advances.

I'm seeking Research Affiliate status to:
1. Implement quantum-inspired P-system variants on supercomputers
2. Run large-scale benchmarks on PRACE/ACCESS
3. Co-author papers in top theoretical CS venues

This offers zero cost to your lab while expanding your research scope.

Would you be interested in discussing? Details: [PORTFOLIO_LINK]

Best regards,
Mark Alexiuk
        """)

    _run_discovery(args.institutions, args.institutions_file, args.output, args.top_n, args.rate_limit_delay)


if __name__ == "__main__":
    main()

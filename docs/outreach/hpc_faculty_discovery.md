---
title: HPC Faculty Discovery for Membrane Computing Collaboration
date: 2025-09-15
tags: [outreach, strategy, hpc, academic-partnerships, collaboration]
type: research_strategy
status: active
---

# HPC Faculty Discovery Pipeline for Membrane Computing Collaboration

This document outlines a **systematic, automated approach** to discovering academic faculty with active HPC allocations who could benefit from a membrane computing collaboration, using the entity mapping framework from `baseline0/research` extended for academic HPC discovery.

---

## Strategic Context

Securing adjunct/affiliate researcher status at a research institution unlocks:

| Resource | Access | Value |
|----------|--------|-------|
| **HPC Allocations** | ACCESS (US), PRACE (EU), WoW (Canada) | $100k–$1M in compute time |
| **University Email** | Institutional affiliation | Required for many grant programs |
| **Library Access** | Full-text journal access | Knowledge base for literature reviews |
| **Graduate Collaborators** | Thesis projects, research labor | Extended team without payroll |
| **Lab Infrastructure** | Shared servers, datasets, equipment | Capital cost reduction |

The challenge: **Identifying the right faculty sponsor** who already has HPC infrastructure and could benefit from your specific expertise.

---

## The Entity Mapping Approach

Your existing entity mapping framework (`baseline0/research/src/research/`) is designed for research collaboration graphs:
- **Entities:** Papers, Authors, Institutions, Funding
- **Relationships:** Co-authorship, affiliation, funding, citations
- **Resolvers:** Map names → standardized IDs (ROR for institutions, ORCID for researchers)

**For HPC faculty discovery, we extend this to:**

1. **Search Phase:** Mine web for faculty + lab URLs in membrane computing / natural computing
2. **Resolution Phase:** Normalize names → institutional affiliations (via ROR), researchers (via ORCID)
3. **Enrichment Phase:** Query OpenAlex, Google Scholar, institution websites for:
   - Research interests + keywords
   - HPC publications (indicate allocation access)
   - Contact email + department
   - Lab website + collaborative interests
4. **Scoring Phase:** Rank leads by:
   - Research relevance (membrane computing overlap)
   - HPC engagement (publications mentioning supercomputing)
   - Institutional size (more resources = easier adjunct process)
5. **Outreach Phase:** Generate cold email templates + pitch materials

---

## Technical Architecture

### Phase 1: Web Scraping → Entity Extraction

**Input:** DuckDuckGo search results for faculty pages

```
Query: site:.edu "membrane computing" faculty
Query: site:.edu "natural computing" HPC lab director
Query: site:.edu "bio-inspired computing" professor
```

**Output:** Unstructured data
```json
{
  "url": "https://cs.example.edu/faculty/jane-doe",
  "title": "Dr. Jane Doe — Natural Computing Lab",
  "snippet": "Director of the Natural Computing Lab. Research: evolutionary algorithms, CUDA optimization, GPU supercomputing.",
  "extracted_email": "jane.doe@example.edu"
}
```

### Phase 2: Entity Resolution

**Input:** Raw faculty name, institution name

**Process:** 
1. Resolve institution name → ROR ID (via RORResolver)
2. Resolve faculty name → ORCID (via ORCID public API or OpenAlex)
3. Cross-reference institutional directory

**Output:** Normalized entity records
```json
{
  "faculty_name": "Jane Doe",
  "institution_ror_id": "012345xyz",
  "orcid": "0000-0001-2345-6789",
  "confidence": 0.92
}
```

### Phase 3: Enrichment (AcademicHPCResolver)

**Input:** Normalized faculty record

**Process:**
- Query OpenAlex API: get publication record
- Filter for HPC/membrane computing keywords
- Extract affiliations, research areas
- Query ORCID for employment history
- Infer HPC access from publication co-authors + institutional affiliations

**Output:** Enriched lead profile
```json
{
  "faculty_name": "Jane Doe",
  "institution_name": "State University",
  "institution_ror_id": "012345xyz",
  "email": "jane.doe@example.edu",
  "department": "Computer Science",
  "research_focus": ["evolutionary algorithms", "GPU computing", "natural computing"],
  "has_hpc_access": true,
  "hpc_networks": ["ACCESS", "XSEDE"],
  "orcid": "0000-0001-2345-6789",
  "confidence_score": 0.92,
  "evidence_sources": ["OpenAlex", "ORCID", "institution_website"]
}
```

### Phase 4: Lead Scoring & Ranking

**Scoring function:**

```
score = (
  research_relevance * 0.4 +        # membrane/natural computing keywords in papers
  hpc_engagement * 0.3 +            # publications + HPC allocations
  institutional_prestige * 0.2 +    # lab size, grant funding
  contact_confidence * 0.1          # email verification
)
```

**Sort leads by score descending.** Top 50–100 become outreach targets.

### Phase 5: Outreach Materials Generation

For each high-scoring lead, auto-generate:

```markdown
---
target_name: Dr. Jane Doe
institution: State University
research_alignment: "Your evolutionary algorithm work aligns well with membrane computing optimization"
proposed_collaboration: "Adjunct Researcher position; co-authored papers on CUDA-accelerated P-systems"
hpc_pitch: "Your ACCESS allocation could run our distributed membrane algorithms at scale"
---

## Pitch Email (Personalized)

Dear Dr. Doe,

I noticed your lab's work on GPU-accelerated evolutionary algorithms. I'm developing
membrane computing (P-system) algorithms for [specific problem: NP-hard optimization / 
biological simulation] that would benefit significantly from your HPC infrastructure.

I'm proposing an **unpaid Adjunct Researcher** position at [your university], which would:
1. Give me institutional affiliation for grant applications
2. Grant me library/HPC access
3. Enable co-authored publications leveraging your ACCESS allocation

In exchange, I'll:
- Provide novel algorithmic contributions to your research
- Write technical proposals for your HPC grant renewals
- Share custom CUDA kernels for membrane-inspired parallel computing

Would you be open to exploring this? [Research portfolio link]

Best,
Mark Alexiuk
```

---

## Implementation Steps

### Step 1: Create Membrane-Specific Pipeline (membrane/ repo)

File: `tools/hpc_lead_discovery.py`

```python
"""
Orchestrate faculty discovery pipeline for HPC collaboration outreach.

Uses entity mapping framework from baseline0/research + AcademicHPCResolver.
"""

import asyncio
import pandas as pd
from research.resolvers.academic_hpc import AcademicHPCResolver, FacultyLead
from research.resolvers.ror import RORResolver


async def discover_hpc_collaborators(
    target_institutions: list[str],
    research_keywords: list[str],
    output_csv: str = "hpc_faculty_leads.csv"
) -> pd.DataFrame:
    """
    Discover faculty with HPC allocations in niche computing paradigms.
    
    Args:
        target_institutions: University names to search
        research_keywords: Research areas (e.g., "membrane computing")
        output_csv: Output file for lead list
        
    Returns:
        DataFrame of ranked leads
    """
    hpc_resolver = AcademicHPCResolver()
    ror_resolver = RORResolver()
    all_leads = []
    
    for institution in target_institutions:
        # Resolve institution
        ror_record = await ror_resolver.resolve(institution)
        ror_id = ror_record.get("ror_id") if ror_record else None
        
        # Discover faculty
        leads = await hpc_resolver.discover_from_institution(
            institution, ror_id
        )
        
        # Enrich each lead
        for lead in leads:
            enriched = await hpc_resolver.enrich_lead(lead)
            all_leads.append(enriched)
    
    # Convert to DataFrame
    df = pd.DataFrame([lead.to_dict() for lead in all_leads])
    
    # Score and rank
    df['outreach_score'] = df.apply(score_lead, axis=1)
    df = df.sort_values('outreach_score', ascending=False)
    
    # Export
    df.to_csv(output_csv, index=False)
    print(f"✓ Discovered {len(df)} leads → {output_csv}")
    
    return df


def score_lead(row: pd.Series) -> float:
    """Score a lead for outreach priority."""
    score = 0.0
    
    # Research relevance (40%)
    research_keywords = ["membrane", "computing", "parallel", "gpu", "hpc"]
    research_text = (
        (row.get("research_focus") or "").lower() + 
        " " + 
        (row.get("lab_url") or "").lower()
    )
    keyword_matches = sum(1 for kw in research_keywords if kw in research_text)
    score += min(0.4, keyword_matches * 0.1)
    
    # HPC engagement (30%)
    if row.get("has_hpc_access"):
        score += 0.3
    hpc_mentions = len(row.get("hpc_networks", []))
    score += min(0.2, hpc_mentions * 0.1)
    
    # Contact confidence (10%)
    if row.get("email"):
        score += 0.1
    
    # Confidence in lead data (20%)
    score += row.get("confidence_score", 0.5) * 0.2
    
    return round(score, 3)
```

### Step 2: Define Target Institutions

Create `docs/outreach/target_institutions.txt`:

```
# Top universities in natural computing, HPC, unconventional paradigms
University of Computer Science and Technology (China)
University of Seville (Spain) — P-system research hub
University of Tarragona (Spain)
Leiden University (Netherlands)
University of Sheffield (UK)
UC San Diego (USA)
Georgia Tech (USA)
CMU (USA)
MIT (USA)
University of Toronto (Canada)
INRIA (France)
Max Planck Institute (Germany)
```

### Step 3: Run Discovery Pipeline

```bash
cd /home/mark/projects/baseline0/membrane

python tools/hpc_lead_discovery.py \
  --institutions "University of Seville" "UC San Diego" "Georgia Tech" \
  --output "docs/outreach/discovered_leads.csv"
```

**Output:** `discovered_leads.csv` with 50–200 leads ranked by outreach score.

### Step 4: Generate Outreach Materials

For top 20 leads, auto-generate personalized pitch emails:

```bash
python tools/generate_outreach_emails.py \
  --leads "docs/outreach/discovered_leads.csv" \
  --top-n 20 \
  --output "docs/outreach/email_templates/"
```

### Step 5: Manual Review & Outreach

1. Review top 20 leads; manually verify contact info
2. Personalize email for each (add specific lab insights)
3. Send cold emails with personalized research portfolio link
4. Track responses in `docs/outreach/outreach_log.md`

---

## Expected Outcomes (3-Month Timeline)

| Milestone | Target | Success Metrics |
|-----------|--------|-----------------|
| **Week 1** | Discover 100+ faculty leads | CSV generated; top 20 verified |
| **Week 2–3** | Enrich leads + generate outreach emails | 20 personalized pitches ready |
| **Week 4** | Send initial outreach batch | Track open rates + clicks |
| **Month 2** | Follow-ups + initial conversations | 3–5 faculty express interest |
| **Month 3** | Negotiate adjunct/affiliate status | 1–2 formal offers secured |

---

## Integration with Malta

Once you secure adjunct status:

1. **Updated Affiliation:** Update CV/grant proposals to include university email
2. **HPC Access:** Request addition to sponsor faculty's allocation
3. **Joint Publications:** Run benchmarks on HPC cluster; co-author results
4. **Research Synergy:** Apply Malta algorithms to sponsor's existing problems
5. **Future Funding:** Co-write grant proposals (you + faculty) targeting SBIR, NSF, etc.

**Example collaboration:**
- Faculty has ACCESS allocation for evolutionary optimization
- You contribute membrane computing algorithm
- Run experiments on Frontera (TACC) or Stampede2
- Co-author: "Membrane P-Systems for Large-Scale Combinatorial Optimization"
- Submit to GECCO or IPDPS conference

---

## Files & Tools Created

| File | Purpose |
|------|---------|
| `baseline0/research/src/research/resolvers/academic_hpc.py` | Core resolver for faculty discovery + enrichment |
| `membrane/tools/hpc_lead_discovery.py` | Orchestration pipeline (main entry point) |
| `membrane/docs/outreach/hpc_faculty_discovery.md` | This strategy doc |
| `membrane/docs/outreach/target_institutions.txt` | Seed list of institutions |
| `membrane/docs/outreach/discovered_leads.csv` | Generated: faculty lead list |
| `membrane/docs/outreach/email_templates/` | Generated: personalized pitch emails |

---

## Next Steps

1. Review AcademicHPCResolver implementation in `baseline0/research`
2. Create `membrane/tools/hpc_lead_discovery.py` orchestration script
3. Define target institutions list
4. Run pilot discovery on 5–10 universities
5. Manually verify top 10 leads
6. Generate + personalize outreach emails
7. Track responses in shared outreach log

---

**Strategy Owner:** Mark Alexiuk  
**Related Docs:**
- `baseline0/research/PHASE4_EXPORT.md` — Entity resolution architecture
- `baseline0/research/src/research/resolvers/` — Resolver implementations
- `../quantum/INTEGRATION_GUIDE.md` — Research framework overview


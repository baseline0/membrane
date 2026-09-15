# HPC Faculty Collaboration Outreach

Discover and reach out to academic faculty with HPC allocations for adjunct researcher partnerships.

## Quick Start

```bash
cd /home/mark/projects/baseline0/membrane

# Run discovery on target institutions
python tools/hpc_lead_discovery.py \
  --institutions-file docs/outreach/target_institutions.txt \
  --output leads.csv \
  --top-n 20

# Verify emails manually, then send personalized emails
# Log activity for tracking conversion funnel
```

## Files

- `target_institutions.txt` — 50+ universities (tiered by research focus)
- `discovered_leads.csv` — Generated lead list (faculty name, email, HPC access, score)
- `tools/hpc_lead_discovery.py` — CLI discovery tool

## Next Steps

1. Review generated CSV
2. Verify top 20 leads' emails via institution directories
3. Personalize 3–5 emails from examples in code docstrings
4. Send, track responses, follow up after 10 days
5. Schedule calls with interested faculty
6. Submit adjunct researcher appointment forms

## Expected Outcome

- 20% email response rate → 3–4 conversations → 1–2 adjunct positions

## Integration

- Consumes: `baseline0/research/src/research/resolvers/academic_hpc.py`
- Produces: CSV lead list + outreach tracking data

---

See code docstrings in `tools/hpc_lead_discovery.py` and
`baseline0/research/src/research/resolvers/academic_hpc.py` for detailed
email templates, scoring formula, and per-phase instructions.

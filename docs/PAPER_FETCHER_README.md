# Paper Fetcher: Realistic Guide

**TL;DR:** Automated fetcher gets ~10-20% of papers (those with public direct links). The rest need manual collection. System handles both seamlessly: everything goes to `reference/lit_review/` and gets tracked in manifest.

---

## What Actually Works

### ✅ Successful Auto-Fetch (Working Now)
- **Liu et al. (2021)** — IEEE Access
  - Fetched: 37KB
  - Cached: `reference/lit_review/Liu_NovelHybridQuantum_2021.pdf`
  - Tracked: `.manifest.json`

### ⏳ Expected Failures (Also Working)
- Zhang et al. (2023) — MDPI portal (no direct PDF link)
- Xiao et al. (2022) — MDPI archive (JavaScript required)
- arXiv papers — Author query pages (not direct PDFs)

**Why they fail:**
```
MDPI portal → HTML page (no PDF link exposed) ❌
IEEE Access → Direct PDF link ✅
arXiv search → Author listing (not PDF) ❌
```

---

## Hybrid Workflow (Realistic)

### Stage 1: Auto-Fetch (2 min)
```bash
python scripts/paper_fetcher.py
# Gets what's publicly available: ~1-2 papers typically
```

### Stage 2: Manual Fetch (15 min)
For remaining papers, use [PAPER_SOURCES.md](PAPER_SOURCES.md):

1. Open Google Scholar link for paper
2. Look for **[PDF]** link on right sidebar
3. Download PDF
4. Save to: `reference/lit_review/AuthorLastName_ShortTitle_Year.pdf`

**Example:**
```bash
# Download Zhang 2023, save as:
reference/lit_review/Zhang_QuantumInspiredSurvey_2023.pdf
```

### Stage 3: Update Manifest (Manual)
Edit `.manifest.json` to track manually-added papers:

```json
{
  "Zhang_QuantumInspiredSurvey_2023": {
    "paper_name": "Zhang_QuantumInspiredSurvey_2023",
    "title": "Quantum-Inspired Membrane Computing: A Survey and Perspective",
    "success": true,
    "source": "manual",
    "filepath": "reference/lit_review/Zhang_QuantumInspiredSurvey_2023.pdf",
    "content_hash": "[compute via `sha256sum` if desired, or leave null]",
    "timestamp": "2026-09-18T16:00:00",
    "url": "[paste Google Scholar URL]",
    "error": null
  }
}
```

Or just leave `.manifest.json` as-is; `paper_status.py` will show PDFs even if not in manifest.

---

## Commands Reference

### Check What We Have
```bash
python scripts/paper_status.py
# Shows:
# ✅ AVAILABLE (1 paper ready for review)
# ⏳ PENDING (9 papers — need manual or retry)
```

### Retry Failed Auto-Fetches
```bash
python scripts/paper_fetcher.py --retry
# Re-attempts papers that failed before
# (Usually still fail unless source changed)
```

### Add Single Paper Manually
```bash
# Just copy/download PDF to reference/lit_review/
cp ~/Downloads/paper.pdf reference/lit_review/Author_Title_Year.pdf

# Manifest will be updated automatically on next `paper_fetcher.py` run,
# or can be left out (paper_status.py still detects it)
```

### Verify Downloaded Papers
```bash
ls -lh reference/lit_review/*.pdf
# Shows what's actually cached locally
```

### View Fetch History
```bash
cat reference/lit_review/.fetch.log
# Shows what the fetcher attempted and why it succeeded/failed

cat reference/lit_review/.manifest.json | python -m json.tool
# Shows structured record of all fetch attempts
```

---

## FAQ

### Q: Why doesn't it auto-fetch all papers?
**A:** Academic publisher sites (MDPI, Springer, IEEE) use JavaScript, authentication, and redirects to prevent mass scraping. Our fetcher is being respectful (rate limits, proper User-Agent), so it stops at these gates. Manual download + local cache is the pragmatic solution.

### Q: Do I need to update `.manifest.json` for manually-added papers?
**A:** No. `paper_status.py` will show any PDFs in `reference/lit_review/` regardless. Manifest is optional — it just adds provenance (which source, when, hash). For manual papers, you can skip it or add an entry for bookkeeping.

### Q: Can I edit `.manifest.json` directly?
**A:** Yes. It's just JSON. Be careful not to break syntax. The fetcher will reload it on next run.

### Q: What if a paper is paywalled?
**A:**
1. Check if your institution has access (login via university VPN or library)
2. Email the author directly (most researchers share PDFs on request)
3. Check ResearchGate (many authors upload their own papers)
4. Try arXiv preprints (often available for free)

### Q: How do I know if a paper is already fetched?
```bash
# Check manifest
cat reference/lit_review/.manifest.json | grep -i "author name"

# Or just list files
ls reference/lit_review/*.pdf
```

---

## Performance Expectations

| Task | Time | Success |
|------|------|---------|
| Auto-fetch all 10 papers | ~60s | ~10-20% |
| Manual download 9 papers | ~15 min | ~100% |
| Total time | ~20 min | ~100% |

**Breakdown:**
- Fetcher: Fast (respects rate limits, quick fail on non-public links)
- Manual: Moderate (Google Scholar search, 1-2 min per paper typically)
- Together: Gives you full paper set in ~20 min

---

## What Happens Next

Once you have papers (auto + manual):

1. **Review:** Open PDFs, read, take notes
2. **Fill LITERATURE_REVIEW.md:** Extract key findings per template
3. **Synthesize:** Draft novelty statement based on findings
4. **Implement:** Use findings to fill `paper/model.py`, benchmark config, etc.

See [LITERATURE_REVIEW_GUIDE.md](LITERATURE_REVIEW_GUIDE.md) for detailed workflow.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Fetcher crashes | Check error in `.fetch.log`; usually network timeout |
| Paper marked "failed" but you know it exists | Run `python scripts/paper_fetcher.py --retry` |
| Want to force-refetch a paper | Delete from `reference/lit_review/` and from `.manifest.json`, re-run |
| `.manifest.json` corrupted | Run `python scripts/paper_fetcher.py --clean` (wipes cache, starts fresh) |

---

## Summary

✅ **System is designed for hybrid use:**
- Automation handles what's public (PDF links, direct access)
- Manual handles what's gated (paywalls, authentication)
- Both feed into same cache + audit trail

✅ **20 min total to get all 10 papers:**
- 1 min: Auto-fetch attempt (get ~1-2)
- 15 min: Manual downloads (get ~8-9)
- 4 min: Organize, verify

✅ **Then literature review begins** with full paper set ready.

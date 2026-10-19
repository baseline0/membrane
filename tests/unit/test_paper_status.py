"""Tests for the paper status report, reading the manifest format that tool_lit_review.fetch writes."""

import json
from pathlib import Path

import pytest

from scripts import paper_status


def _entry(paper_id: str, status: str, path: str | None = None, error: str | None = None) -> dict:
    return {
        "paper_id": paper_id,
        "status": status,
        "source": "arXiv" if status == "saved" else None,
        "path": path,
        "sha256": None,
        "url": None,
        "error": error,
        "timestamp": "2026-10-10T12:00:00+00:00",
    }


def _write_pdf(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"%PDF-1.4 " + b"x" * 1024)
    return str(path)


def test_report_sorts_entries_by_status_and_file_presence(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    saved_pdf = _write_pdf(tmp_path / "pdf" / "saved_one.pdf")
    cached_pdf = _write_pdf(tmp_path / "pdf" / "cached_one.pdf")
    manifest = {
        "saved_one": _entry("saved_one", "saved", saved_pdf),
        "cached_one": _entry("cached_one", "cached", cached_pdf),
        "gone": _entry("gone", "saved", str(tmp_path / "pdf" / "gone.pdf")),
        "paywalled": _entry("paywalled", "failed", error="Requires UofM library access (DOI: 10.1/x)"),
    }
    titles = {"saved_one": "A Saved Paper", "paywalled": "A Paywalled Paper"}

    available, unavailable, missing = paper_status.generate_console_report(manifest, titles)

    assert [pid for pid, _result, _size in available] == ["saved_one", "cached_one"]
    assert [pid for pid, _result in unavailable] == ["paywalled"]
    assert [pid for pid, _result in missing] == ["gone"]
    out = capsys.readouterr().out
    assert "Title: A Saved Paper" in out
    assert "Summary: 2/4 papers available (50%)" in out
    assert "Requires UofM library access" in out


def test_main_reads_manifest_from_the_default_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    pdf = _write_pdf(tmp_path / "reference" / "lit_review" / "pdf" / "ok.pdf")
    manifest_path = tmp_path / "reference" / "lit_review" / ".manifest.json"
    manifest_path.write_text(
        json.dumps({"ok": _entry("ok", "saved", pdf), "bad": _entry("bad", "failed", error="HTTP 404")}),
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_status, "load_titles", lambda: {"ok": "Ok Paper", "bad": "Bad Paper"})

    paper_status.main()

    out = capsys.readouterr().out
    assert "Summary: 1/2 papers available (50%)" in out
    assert "**Location:** " + pdf in out
    assert "→ Re-run fetcher: python scripts/paper_fetcher.py --retry true --clean false" in out


def test_main_exits_when_manifest_is_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        paper_status.main()

    assert excinfo.value.code == 1

"""Tests for the paper fetcher: selection, cleaning, session flow, and the Typer wiring."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from scripts import paper_fetcher
from scripts.paper_fetcher import (
    FetchResult,
    PaperFetcher,
    PaperSource,
    clear_manifest,
    load_paper_sources,
    papers_to_fetch,
    run_session,
)


def _paper(name: str, requires_library: bool = True) -> PaperSource:
    return PaperSource(
        name=name,
        title=f"Title {name}",
        authors="A. Author",
        year=2020,
        doi="10.0000/xxx",
        requires_library=requires_library,
        sources={},
    )


def _result(name: str, success: bool) -> FetchResult:
    return FetchResult(
        paper_name=name,
        title=f"Title {name}",
        success=success,
        source="MDPI" if success else None,
        filepath=None,
        content_hash=None,
        timestamp="2026-10-10T00:00:00",
        url=None,
        error=None if success else "All sources exhausted",
    )


def _fetcher(tmp_path: Path) -> PaperFetcher:
    return PaperFetcher(output_dir=tmp_path / "lit", manifest_path=tmp_path / "lit" / ".manifest.json")


def test_papers_to_fetch_skips_cached_successes_by_default() -> None:
    papers = [_paper("ok"), _paper("failed"), _paper("new")]
    manifest = {"ok": _result("ok", True), "failed": _result("failed", False)}

    selected = papers_to_fetch(papers, manifest, retry=False)

    assert [p.name for p in selected] == ["failed", "new"]


def test_papers_to_fetch_retry_selects_everything() -> None:
    papers = [_paper("ok"), _paper("failed")]
    manifest = {"ok": _result("ok", True), "failed": _result("failed", False)}

    assert papers_to_fetch(papers, manifest, retry=True) == papers


def test_papers_to_fetch_with_empty_manifest_selects_all() -> None:
    papers = [_paper("a"), _paper("b")]

    assert papers_to_fetch(papers, {}, retry=False) == papers


def test_clear_manifest_empties_memory_and_disk(tmp_path: Path) -> None:
    fetcher = _fetcher(tmp_path)
    fetcher.manifest = {"ok": _result("ok", True)}
    fetcher._save_manifest()

    clear_manifest(fetcher)

    assert fetcher.manifest == {}
    assert PaperFetcher(output_dir=fetcher.output_dir, manifest_path=fetcher.manifest_path).manifest == {}


def test_run_session_records_library_papers_without_network(tmp_path: Path) -> None:
    fetcher = _fetcher(tmp_path)
    papers = [_paper("paywalled")]

    run_session(fetcher, papers, retry=False, clean=False)

    assert fetcher.manifest["paywalled"].success is False
    assert "UofM library access" in (fetcher.manifest["paywalled"].error or "")
    assert (fetcher.output_dir / "LIBRARY_LOOKUP.txt").exists()


def test_run_session_clean_discards_cached_success(tmp_path: Path) -> None:
    fetcher = _fetcher(tmp_path)
    fetcher.manifest = {"paywalled": _result("paywalled", True)}
    fetcher._save_manifest()

    run_session(fetcher, [_paper("paywalled")], retry=False, clean=True)

    assert fetcher.manifest["paywalled"].success is False


def test_run_session_skips_cached_success_without_clean(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher = _fetcher(tmp_path)
    cached = _result("ok", True)
    fetcher.manifest = {"ok": cached}
    attempted: list[str] = []
    monkeypatch.setattr(fetcher, "fetch_paper", lambda paper: attempted.append(paper.name))

    run_session(fetcher, [_paper("ok", requires_library=False)], retry=False, clean=False)

    assert attempted == []
    assert fetcher.manifest["ok"] is cached


def test_load_paper_sources_has_unique_names_and_open_access_sources() -> None:
    papers = load_paper_sources()

    names = [p.name for p in papers]
    assert len(papers) == 10
    assert len(set(names)) == len(names)
    for paper in papers:
        if paper.is_open_access:
            assert paper.sources, f"{paper.name} is open access but has no source URL"
        else:
            assert paper.requires_library, f"{paper.name} is neither open access nor library-only"


def test_cli_help_lists_both_flags() -> None:
    result = CliRunner().invoke(paper_fetcher.app, ["--help"])

    assert result.exit_code == 0
    assert "--retry" in result.output
    assert "--clean" in result.output


def test_cli_rejects_unknown_flag() -> None:
    result = CliRunner().invoke(paper_fetcher.app, ["--bogus"])

    assert result.exit_code == 2


def test_cli_passes_flags_to_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[bool, bool]] = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(paper_fetcher, "configure_logging", lambda *a, **k: None)
    monkeypatch.setattr(paper_fetcher, "load_paper_sources", lambda: [])
    monkeypatch.setattr(
        paper_fetcher,
        "run_session",
        lambda fetcher, papers, retry, clean: calls.append((retry, clean)),
    )

    result = CliRunner().invoke(paper_fetcher.app, ["--retry", "--clean"])

    assert result.exit_code == 0
    assert calls == [(True, True)]

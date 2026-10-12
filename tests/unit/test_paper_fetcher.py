"""Tests for the paper fetcher: the curated list, selection, --retry and --clean, the library report, and the CLI.

No test touches the network: requests go to an httpx.MockTransport that serves PDFs from memory.
"""

import logging
from pathlib import Path

import httpx
import pytest
from tool_lit_review.fetch import ARXIV_SOURCE, PaperFetcher, PaperRecord, RateLimiter, pdf_path
from typer.testing import CliRunner

from scripts import paper_fetcher
from scripts.paper_fetcher import CuratedPaper, load_paper_sources, run_session

MANIFEST_NAME = ".manifest.json"


class FakeArxiv:
    """Serves a PDF for each arXiv id in `available`, 404 for the rest, and records every request URL."""

    def __init__(self) -> None:
        self.available: set[str] = set()
        self.requests: list[str] = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(str(request.url))
        arxiv_id = str(request.url).rsplit("/", 1)[-1]
        if arxiv_id in self.available:
            return httpx.Response(200, content=b"%PDF-1.4 fake", headers={"content-type": "application/pdf"})
        return httpx.Response(404)


def _fetcher(root: Path, server: FakeArxiv) -> PaperFetcher:
    """A fetcher as make_fetcher builds it, but with arXiv only, a mock client, and no sleeping."""
    return PaperFetcher(
        sources=(ARXIV_SOURCE,),
        root=root,
        client=httpx.Client(transport=httpx.MockTransport(server.handle)),
        limiter=RateLimiter(min_delay=0.0, clock=lambda: 0.0, sleep=lambda _seconds: None),
        manifest_path=root / MANIFEST_NAME,
        sleep=lambda _seconds: None,
    )


def _paper(paper_id: str, arxiv_id: str | None = None, requires_library: bool = False) -> CuratedPaper:
    return CuratedPaper(
        paper_id=paper_id,
        title=f"Title {paper_id}",
        authors="A. Author",
        year=2020,
        arxiv_id=arxiv_id,
        requires_library=requires_library,
    )


def test_curated_list_keeps_every_paper_and_its_library_flags() -> None:
    papers = load_paper_sources()
    by_id = {p.paper_id: p for p in papers}

    assert set(by_id) == {
        "Zhang_QuantumInspiredMembrane_2023",
        "Zhang_RealCodedQuantum_2021",
        "Diaz_SoftwareToolsMembraneComputing_2010",
        "Leporati_SimulatingQuantumCircuits_2005",
        "Xiao_QuantumInspiredMembrane_2022",
        "Paun_OpenProblemsMembraneComputing_2019",
        "Liu_NovelHybridQuantum_2021",
        "Nishimura_QuantumPSystems_2022",
        "Valencia_ParallelImplementation_2023",
        "Liu_MembranComputingQuantumInfo_2020",
    }
    assert all(isinstance(p, PaperRecord) for p in papers)


def test_library_flag_survives_the_mapping() -> None:
    by_id = {p.paper_id: p for p in load_paper_sources()}

    paywalled = by_id["Zhang_RealCodedQuantum_2021"]
    assert paywalled.requires_library is True
    assert paywalled.is_open_access is False
    assert paywalled.needs_library is True
    assert paywalled.doi == "10.1016/j.ins.2021.xxx"

    open_access = by_id["Zhang_QuantumInspiredMembrane_2023"]
    assert open_access.is_open_access is True
    assert open_access.needs_library is False


def test_default_run_fetches_new_papers_then_makes_no_requests_for_recorded_ones(tmp_path: Path) -> None:
    server = FakeArxiv()
    server.available.add("0001.0001")
    papers = [_paper("ok", "0001.0001"), _paper("missing", "0002.0002")]

    run_session(_fetcher(tmp_path, server), papers, retry=False, clean=False)

    assert server.requests == ["https://arxiv.org/pdf/0001.0001", "https://arxiv.org/pdf/0002.0002"]
    reloaded = _fetcher(tmp_path, server)
    assert reloaded.manifest["ok"].status == "saved"
    assert reloaded.manifest["missing"].status == "failed"

    server.requests.clear()
    run_session(reloaded, papers, retry=False, clean=False)

    assert server.requests == []


def test_default_run_does_not_retry_failures(tmp_path: Path) -> None:
    server = FakeArxiv()
    papers = [_paper("missing", "0002.0002")]
    run_session(_fetcher(tmp_path, server), papers, retry=False, clean=False)

    server.available.add("0002.0002")
    server.requests.clear()
    run_session(_fetcher(tmp_path, server), papers, retry=False, clean=False)

    assert server.requests == []


def test_retry_refetches_failed_papers_and_not_successful_ones(tmp_path: Path) -> None:
    server = FakeArxiv()
    server.available.add("0001.0001")
    papers = [_paper("ok", "0001.0001"), _paper("missing", "0002.0002")]
    run_session(_fetcher(tmp_path, server), papers, retry=False, clean=False)

    server.available.add("0002.0002")
    server.requests.clear()
    fetcher = _fetcher(tmp_path, server)
    run_session(fetcher, papers, retry=True, clean=False)

    assert server.requests == ["https://arxiv.org/pdf/0002.0002"]
    assert fetcher.manifest["missing"].status == "saved"
    assert fetcher.manifest["ok"].status == "saved"


def test_clean_clears_manifest_and_refetches_without_redownloading_pdfs_on_disk(tmp_path: Path) -> None:
    server = FakeArxiv()
    server.available.add("0001.0001")
    papers = [_paper("ok", "0001.0001"), _paper("missing", "0002.0002")]
    run_session(_fetcher(tmp_path, server), papers, retry=False, clean=False)

    server.available.add("0002.0002")
    server.requests.clear()
    fetcher = _fetcher(tmp_path, server)
    run_session(fetcher, papers, retry=False, clean=True)

    # The saved PDF is still on disk, so it is recorded as cached and not requested again.
    assert server.requests == ["https://arxiv.org/pdf/0002.0002"]
    assert fetcher.manifest["ok"].status == "cached"
    assert fetcher.manifest["missing"].status == "saved"
    assert pdf_path(tmp_path, "ok").exists()


def test_library_paper_is_recorded_as_failed_without_any_request(tmp_path: Path) -> None:
    server = FakeArxiv()
    server.available.add("0003.0003")
    fetcher = _fetcher(tmp_path, server)

    run_session(fetcher, [_paper("paywalled", "0003.0003", requires_library=True)], retry=False, clean=False)

    assert server.requests == []
    assert fetcher.manifest["paywalled"].status == "failed"
    assert "UofM library access" in (fetcher.manifest["paywalled"].error or "")
    lookup = (tmp_path / "LIBRARY_LOOKUP.txt").read_text(encoding="utf-8")
    assert "Title paywalled" in lookup


def test_library_paper_with_pdf_already_in_place_is_cached(tmp_path: Path) -> None:
    server = FakeArxiv()
    target = pdf_path(tmp_path, "paywalled")
    target.parent.mkdir(parents=True)
    target.write_bytes(b"%PDF-1.4 added by hand")

    fetcher = _fetcher(tmp_path, server)
    run_session(fetcher, [_paper("paywalled", requires_library=True)], retry=False, clean=False)

    assert server.requests == []
    assert fetcher.manifest["paywalled"].status == "cached"


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
    monkeypatch.setattr(paper_fetcher, "make_fetcher", lambda: object())
    monkeypatch.setattr(paper_fetcher, "load_paper_sources", lambda: [])
    monkeypatch.setattr(
        paper_fetcher,
        "run_session",
        lambda fetcher, papers, retry, clean: calls.append((retry, clean)),
    )

    result = CliRunner().invoke(paper_fetcher.app, ["--retry", "--clean"])

    assert result.exit_code == 0
    assert calls == [(True, True)]


def test_cli_stops_with_guidance_on_an_old_format_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.chdir(tmp_path)
    manifest = tmp_path / paper_fetcher.MANIFEST_PATH
    manifest.parent.mkdir(parents=True)
    manifest.write_text('{"Old_Entry_2020": {"paper_name": "Old_Entry_2020", "success": true}}', encoding="utf-8")
    monkeypatch.setattr(paper_fetcher, "configure_logging", lambda *a, **k: None)

    with caplog.at_level(logging.ERROR):
        result = CliRunner().invoke(paper_fetcher.app, [])

    assert result.exit_code == 1
    assert "Cannot read fetch manifest" in caplog.text
    assert "Move the manifest aside" in caplog.text

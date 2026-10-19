"""Tests for the paper fetcher: the curated list, selection, --retry and --clean, the library report, and the CLI.

No test runs tool-lit-review or touches the network. run_session takes an `invoke` callable; the fake below stands in
for `tool-lit-review fetch-list` and writes the manifest rows it is told to write.
"""

import json
import logging
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from scripts import paper_fetcher
from scripts.paper_fetcher import (
    CuratedPaper,
    FetchListFailed,
    ManifestError,
    invoke_fetch_list,
    load_paper_sources,
    run_session,
)

MANIFEST_NAME = ".manifest.json"


class FakeFetchList:
    """Stands in for `tool-lit-review fetch-list`: records each call and writes a manifest row per listed paper.

    outcomes maps paper id to the status the fake gives it ('saved' or 'failed'). Papers not in outcomes are saved.
    Like the real command, a PDF already on disk is 'cached', and clean deletes the manifest first.
    """

    def __init__(self, outcomes: dict[str, str] | None = None) -> None:
        self.outcomes = outcomes or {}
        self.calls: list[dict[str, object]] = []

    def __call__(self, list_path: Path, output_dir: Path, clean: bool) -> None:
        records = json.loads(list_path.read_text(encoding="utf-8"))
        self.calls.append({"ids": [r["paper_id"] for r in records], "clean": clean})
        manifest_path = output_dir / MANIFEST_NAME
        if clean and manifest_path.exists():
            manifest_path.unlink()
        rows = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        for record in records:
            paper_id = record["paper_id"]
            pdf = output_dir / "pdf" / f"{paper_id}.pdf"
            if pdf.exists():
                status = "cached"
            else:
                status = self.outcomes.get(paper_id, "saved")
                if status == "saved":
                    pdf.parent.mkdir(parents=True, exist_ok=True)
                    pdf.write_bytes(b"%PDF-1.4 fake")
            rows[paper_id] = {
                "paper_id": paper_id,
                "status": status,
                "source": "DOI" if status in {"saved", "cached"} else None,
                "path": str(pdf) if status in {"saved", "cached"} else None,
                "sha256": None,
                "url": None,
                "error": None if status in {"saved", "cached"} else "HTTP 404",
                "timestamp": "2026-10-18T00:00:00+00:00",
                "licence": None,
            }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def _paper(paper_id: str, requires_library: bool = False, doi: str | None = None) -> CuratedPaper:
    return CuratedPaper(
        paper_id=paper_id,
        title=f"Title {paper_id}",
        authors="A. Author",
        year=2020,
        doi=doi or f"10.1000/{paper_id}",
        requires_library=requires_library,
    )


def _manifest(output_dir: Path) -> dict[str, dict]:
    return json.loads((output_dir / MANIFEST_NAME).read_text(encoding="utf-8"))


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


def test_library_flag_survives_the_mapping() -> None:
    by_id = {p.paper_id: p for p in load_paper_sources()}

    paywalled = by_id["Zhang_RealCodedQuantum_2021"]
    assert paywalled.requires_library is True
    assert paywalled.is_open_access is False
    assert paywalled.needs_library is True
    assert paywalled.doi is None  # placeholder DOI removed; no identifier, so the fetcher refuses it

    open_access = by_id["Zhang_QuantumInspiredMembrane_2023"]
    assert open_access.is_open_access is True
    assert open_access.needs_library is False


def test_default_run_requests_only_new_papers_then_requests_nothing_for_recorded_ones(tmp_path: Path) -> None:
    fake = FakeFetchList()
    papers = [_paper("ok"), _paper("other")]

    run_session(papers, retry=False, clean=False, output_dir=tmp_path, invoke=fake)

    assert fake.calls == [{"ids": ["ok", "other"], "clean": False}]
    assert {k: v["status"] for k, v in _manifest(tmp_path).items()} == {"ok": "saved", "other": "saved"}

    run_session(papers, retry=False, clean=False, output_dir=tmp_path, invoke=fake)

    assert fake.calls[-1] == {"ids": [], "clean": False}


def test_default_run_does_not_retry_failures(tmp_path: Path) -> None:
    papers = [_paper("missing")]
    run_session(papers, retry=False, clean=False, output_dir=tmp_path, invoke=FakeFetchList({"missing": "failed"}))

    fake = FakeFetchList()
    run_session(papers, retry=False, clean=False, output_dir=tmp_path, invoke=fake)

    assert fake.calls == [{"ids": [], "clean": False}]
    assert _manifest(tmp_path)["missing"]["status"] == "failed"


def test_retry_requests_failed_papers_and_not_successful_ones(tmp_path: Path) -> None:
    papers = [_paper("ok"), _paper("missing")]
    run_session(papers, retry=False, clean=False, output_dir=tmp_path, invoke=FakeFetchList({"missing": "failed"}))

    fake = FakeFetchList()
    run_session(papers, retry=True, clean=False, output_dir=tmp_path, invoke=fake)

    assert fake.calls == [{"ids": ["missing"], "clean": False}]
    assert _manifest(tmp_path)["missing"]["status"] == "saved"


def test_clean_passes_clean_true_and_requests_every_paper(tmp_path: Path) -> None:
    papers = [_paper("ok"), _paper("missing")]
    run_session(papers, retry=False, clean=False, output_dir=tmp_path, invoke=FakeFetchList({"missing": "failed"}))

    fake = FakeFetchList()
    run_session(papers, retry=False, clean=True, output_dir=tmp_path, invoke=fake)

    assert fake.calls == [{"ids": ["ok", "missing"], "clean": True}]


def test_library_paper_is_recorded_as_failed_and_never_sent_to_fetch_list(tmp_path: Path) -> None:
    fake = FakeFetchList()
    paper = _paper("paywalled", requires_library=True, doi="10.1016/j.ins.2021.xxx")

    run_session([paper], retry=False, clean=False, output_dir=tmp_path, invoke=fake)

    assert fake.calls == [{"ids": [], "clean": False}]
    row = _manifest(tmp_path)["paywalled"]
    assert row["status"] == "failed"
    assert "UofM library access" in row["error"]
    assert "10.1016/j.ins.2021.xxx" in row["error"]
    lookup = (tmp_path / "LIBRARY_LOOKUP.txt").read_text(encoding="utf-8")
    assert "Title paywalled" in lookup


def test_library_paper_with_pdf_already_in_place_is_sent_to_fetch_list_as_cached(tmp_path: Path) -> None:
    (tmp_path / "pdf").mkdir()
    (tmp_path / "pdf" / "paywalled.pdf").write_bytes(b"%PDF-1.4 added by hand")
    fake = FakeFetchList()

    run_session(
        [_paper("paywalled", requires_library=True)], retry=False, clean=False, output_dir=tmp_path, invoke=fake
    )

    assert fake.calls == [{"ids": ["paywalled"], "clean": False}]
    assert _manifest(tmp_path)["paywalled"]["status"] == "cached"


def test_session_refuses_a_manifest_in_the_old_format(tmp_path: Path) -> None:
    (tmp_path / MANIFEST_NAME).write_text('{"Old_Entry_2020": {"paper_name": "x", "success": true}}', encoding="utf-8")
    fake = FakeFetchList()

    with pytest.raises(ManifestError, match="not in fetch format"):
        run_session([_paper("ok")], retry=False, clean=True, output_dir=tmp_path, invoke=fake)

    assert fake.calls == []


def test_invoke_builds_the_fetch_list_command_and_raises_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        return subprocess.CompletedProcess(command, 3, stdout="", stderr="boom")

    monkeypatch.setattr(paper_fetcher.subprocess, "run", fake_run)

    with pytest.raises(FetchListFailed, match="exited 3: boom"):
        invoke_fetch_list(tmp_path / "list.json", tmp_path, clean=True)

    command = commands[0]
    assert command[:3] == ["uv", "run", "--project"]
    assert command[3].endswith("tool-lit-review")
    assert command[4:6] == ["tool-lit-review", "fetch-list"]
    assert command[command.index("--clean") + 1] == "true"
    assert command[command.index("--min-delay") + 1] == str(paper_fetcher.MIN_DELAY_SECONDS)
    assert command[command.index("--timeout") + 1] == str(paper_fetcher.REQUEST_TIMEOUT_SECONDS)


def test_cli_help_lists_both_flags() -> None:
    # Pin width and colour: rich wraps and colours help text differently on CI, which split the flag names.
    runner = CliRunner(env={"COLUMNS": "200", "NO_COLOR": "1", "TERM": "dumb"})
    result = runner.invoke(paper_fetcher.app, ["--help"])

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
        lambda papers, retry, clean: calls.append((retry, clean)),
    )

    result = CliRunner().invoke(paper_fetcher.app, ["--retry", "true", "--clean", "true"])

    assert result.exit_code == 0
    assert calls == [(True, True)]


def test_cli_flags_are_required_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(paper_fetcher, "configure_logging", lambda *a, **k: None)

    result = CliRunner().invoke(paper_fetcher.app, [])

    assert result.exit_code == 2


def test_cli_stops_with_guidance_on_an_old_format_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.chdir(tmp_path)
    manifest = tmp_path / paper_fetcher.OUTPUT_DIR / MANIFEST_NAME
    manifest.parent.mkdir(parents=True)
    manifest.write_text('{"Old_Entry_2020": {"paper_name": "Old_Entry_2020", "success": true}}', encoding="utf-8")
    monkeypatch.setattr(paper_fetcher, "configure_logging", lambda *a, **k: None)

    with caplog.at_level(logging.ERROR):
        result = CliRunner().invoke(paper_fetcher.app, ["--retry", "false", "--clean", "false"])

    assert result.exit_code == 1
    assert "Cannot read fetch manifest" in caplog.text
    assert "Move the manifest aside" in caplog.text

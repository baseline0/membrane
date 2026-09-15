"""Integration tests for simulation exporters.

Tests verify:
- JSON export/import round-trip
- YAML export works (if PyYAML available)
- Optimization results export
- Quantum state export
"""

import json
import tempfile
from pathlib import Path

import pytest

from malta.trace import MembraneTrace
from malta.exporters import SimulationExporter
from malta.quantum_inspired import Candidate


class TestSimulationExporter:
    """Tests for simulation data export."""

    def test_export_trace_to_json_string(self):
        """Export trace to JSON string."""
        trace = MembraneTrace(description="Test trace")
        trace.record_rule_applied(1, "root", "rule_A", {"X": 1}, {"Y": 1})

        json_str = SimulationExporter.export_trace_to_json(trace)

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["metadata"]["description"] == "Test trace"
        assert data["metadata"]["total_events"] == 1

    def test_export_trace_to_json_file(self):
        """Export trace to JSON file."""
        trace = MembraneTrace(description="Test")
        trace.record_rule_applied(1, "root", "rule_A")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trace.json"
            json_str = SimulationExporter.export_trace_to_json(trace, output_path)

            # File should exist and be readable
            assert output_path.exists()
            data = json.loads(output_path.read_text())
            assert data["metadata"]["total_events"] == 1

    def test_export_trace_to_yaml(self):
        """Export trace to YAML string."""
        trace = MembraneTrace(description="Test")
        trace.record_rule_applied(1, "root", "rule_A")

        try:
            yaml_str = SimulationExporter.export_trace_to_yaml(trace)
            assert "Test" in yaml_str  # Description should be in YAML
        except ImportError:
            pytest.skip("PyYAML not installed")

    def test_export_optimization_result_json(self):
        """Export optimization result to JSON."""
        candidate = Candidate(values=[1.5, 2.5], fitness=10.0)
        final_multiset = {"A": 3, "B": 1}

        result_str = SimulationExporter.export_optimization_result(
            candidate, final_multiset, format="json"
        )

        data = json.loads(result_str)
        assert data["result"]["best_fitness"] == 10.0
        assert data["result"]["best_solution"] == [1.5, 2.5]
        assert data["final_state"]["multiset"] == {"A": 3, "B": 1}

    def test_export_optimization_result_with_trace(self):
        """Export optimization result including trace."""
        candidate = Candidate(values=[1.0, 2.0], fitness=5.0)
        final_multiset = {"A": 1}
        trace = MembraneTrace()
        trace.record_rule_applied(1, "root", "rule_A")

        result_str = SimulationExporter.export_optimization_result(
            candidate, final_multiset, trace=trace, format="json"
        )

        data = json.loads(result_str)
        assert data["result"]["best_fitness"] == 5.0
        assert "trace" in data
        assert data["trace"]["metadata"]["total_events"] == 1

    def test_export_optimization_result_to_file(self):
        """Export optimization result to file."""
        candidate = Candidate(values=[1.0], fitness=1.0)
        multiset = {"X": 1}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "result.json"
            SimulationExporter.export_optimization_result(
                candidate, multiset, output_path=output_path, format="json"
            )

            assert output_path.exists()
            data = json.loads(output_path.read_text())
            assert data["result"]["best_fitness"] == 1.0

    def test_export_quantum_state(self):
        """Export quantum state snapshot."""
        state = {"00": 0.5, "11": 0.5}

        json_str = SimulationExporter.export_quantum_state(
            state, step=5, membrane_id="root"
        )

        data = json.loads(json_str)
        assert data["step"] == 5
        assert data["membrane_id"] == "root"
        assert data["amplitudes"]["00"] == 0.5
        assert data["probabilities"]["00"] == 0.25  # |0.5|^2
        assert data["probabilities"]["11"] == 0.25

    def test_export_quantum_state_to_file(self):
        """Export quantum state to file."""
        state = {"0": 0.707, "1": 0.707}

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "quantum.json"
            SimulationExporter.export_quantum_state(
                state, step=1, membrane_id="inner", output_path=output_path
            )

            assert output_path.exists()
            data = json.loads(output_path.read_text())
            assert "probabilities" in data

    def test_import_trace_from_json(self):
        """Import trace from JSON file."""
        trace = MembraneTrace(description="Test")
        trace.record_rule_applied(1, "root", "rule_A")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trace.json"
            SimulationExporter.export_trace_to_json(trace, output_path)

            # Import and verify
            imported = SimulationExporter.import_trace_from_json(output_path)
            assert imported["metadata"]["description"] == "Test"
            assert imported["metadata"]["total_events"] == 1

    def test_export_unsupported_format(self):
        """Unsupported export format raises error."""
        candidate = Candidate(values=[1.0], fitness=1.0)
        multiset = {"X": 1}

        with pytest.raises(ValueError, match="Unsupported format"):
            SimulationExporter.export_optimization_result(
                candidate, multiset, format="xml"
            )

    def test_export_round_trip_json(self):
        """Export and re-import preserves data."""
        trace = MembraneTrace(description="Round trip test")
        trace.record_rule_applied(1, "root", "rule_A", {"X": 1}, {"Y": 2})
        trace.record_measurement(2, "root", {"A": 0.5, "B": 0.5}, "A", 0.5)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "trace.json"

            # Export
            SimulationExporter.export_trace_to_json(trace, output_path)

            # Import
            imported = SimulationExporter.import_trace_from_json(output_path)

            # Verify
            assert imported["metadata"]["total_events"] == 2
            assert len(imported["events"]) == 2
            assert imported["events"][0]["rule_name"] == "rule_A"
            assert imported["events"][1]["event_type"] == "measurement"

    def test_export_json_is_valid_json(self):
        """Exported JSON is always valid JSON."""
        trace = MembraneTrace()
        trace.record_rule_applied(1, "root", "rule")
        trace.record_state_transition(2, "inner", {"A": 1}, {"B": 2})
        trace.record_measurement(3, "outer", {"0": 0.707}, "0", 0.5)

        json_str = SimulationExporter.export_trace_to_json(trace)

        # Should parse without error
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert "metadata" in data
        assert "events" in data

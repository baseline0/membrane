"""Unit tests for membrane execution tracing.

Tests verify:
- Events are recorded correctly
- Filtering works (by membrane, by type)
- Exports are complete and valid
"""

import json

from malta.trace import MembraneTrace, TraceEvent


class TestTraceEvent:
    """Tests for TraceEvent dataclass."""

    def test_trace_event_creation(self):
        """TraceEvent initializes with required fields."""
        event = TraceEvent(
            timestamp="2026-09-15T12:34:56.789Z",
            event_type="rule_applied",
            step=5,
            membrane_id="root",
            rule_name="apply_rule_A",
        )

        assert event.timestamp == "2026-09-15T12:34:56.789Z"
        assert event.event_type == "rule_applied"
        assert event.step == 5
        assert event.membrane_id == "root"

    def test_trace_event_to_dict(self):
        """TraceEvent converts to dictionary."""
        event = TraceEvent(
            timestamp="2026-09-15T12:34:56.789Z",
            event_type="rule_applied",
            step=5,
            membrane_id="root",
            rule_name="apply_rule_A",
            details={"input": {"A": 1}, "output": {"B": 1}},
        )

        event_dict = event.to_dict()

        assert event_dict["timestamp"] == "2026-09-15T12:34:56.789Z"
        assert event_dict["event_type"] == "rule_applied"
        assert event_dict["details"]["input"] == {"A": 1}


class TestMembraneTrace:
    """Tests for membrane execution trace."""

    def test_trace_initialization(self):
        """Trace initializes with description."""
        trace = MembraneTrace(description="Test simulation")
        assert trace.description == "Test simulation"
        assert trace.events == []

    def test_record_rule_applied(self):
        """Record rule application."""
        trace = MembraneTrace()
        trace.record_rule_applied(
            step=1,
            membrane_id="root",
            rule_name="rule_A",
            input_multiset={"X": 1},
            output_multiset={"Y": 1},
        )

        assert len(trace.events) == 1
        event = trace.events[0]
        assert event.event_type == "rule_applied"
        assert event.rule_name == "rule_A"
        assert event.details["input"] == {"X": 1}
        assert event.details["output"] == {"Y": 1}

    def test_record_measurement(self):
        """Record measurement event."""
        trace = MembraneTrace()
        trace.record_measurement(
            step=2,
            membrane_id="root",
            quantum_state_before={"A": 0.707, "B": 0.707},
            outcome="A",
            probability=0.5,
        )

        assert len(trace.events) == 1
        event = trace.events[0]
        assert event.event_type == "measurement"
        assert event.details["outcome"] == "A"
        assert event.details["probability"] == 0.5

    def test_record_state_transition(self):
        """Record state transition."""
        trace = MembraneTrace()
        trace.record_state_transition(
            step=1,
            membrane_id="inner",
            multiset_before={"A": 2, "B": 1},
            multiset_after={"B": 3},
            reason="rule_application",
        )

        assert len(trace.events) == 1
        event = trace.events[0]
        assert event.event_type == "state_transition"
        assert event.details["before"] == {"A": 2, "B": 1}
        assert event.details["after"] == {"B": 3}

    def test_record_membrane_created(self):
        """Record membrane creation."""
        trace = MembraneTrace()
        trace.record_membrane_created(step=1, parent_membrane_id="root", new_membrane_id="inner_1")

        assert len(trace.events) == 1
        event = trace.events[0]
        assert event.event_type == "membrane_created"
        assert event.details["parent"] == "root"

    def test_get_events_all(self):
        """Get all events."""
        trace = MembraneTrace()
        trace.record_rule_applied(1, "root", "rule_A")
        trace.record_rule_applied(2, "inner", "rule_B")
        trace.record_measurement(3, "root", {}, "A", 0.5)

        events = trace.get_events()
        assert len(events) == 3

    def test_get_events_by_membrane(self):
        """Filter events by membrane ID."""
        trace = MembraneTrace()
        trace.record_rule_applied(1, "root", "rule_A")
        trace.record_rule_applied(2, "inner", "rule_B")
        trace.record_rule_applied(3, "root", "rule_C")

        root_events = trace.get_events(membrane_id="root")
        assert len(root_events) == 2
        assert all(e.membrane_id == "root" for e in root_events)

        inner_events = trace.get_events(membrane_id="inner")
        assert len(inner_events) == 1
        assert inner_events[0].rule_name == "rule_B"

    def test_get_events_by_type(self):
        """Filter events by type."""
        trace = MembraneTrace()
        trace.record_rule_applied(1, "root", "rule_A")
        trace.record_measurement(2, "root", {}, "A", 0.5)
        trace.record_rule_applied(3, "root", "rule_B")

        rule_events = trace.get_events_by_type("rule_applied")
        assert len(rule_events) == 2
        assert all(e.event_type == "rule_applied" for e in rule_events)

        measurement_events = trace.get_events_by_type("measurement")
        assert len(measurement_events) == 1

    def test_summary(self):
        """Get execution summary."""
        trace = MembraneTrace(description="Test run")
        trace.record_rule_applied(1, "root", "rule_A")
        trace.record_measurement(2, "root", {}, "A", 0.5)
        trace.record_rule_applied(3, "root", "rule_B")

        summary = trace.summary()

        assert summary["description"] == "Test run"
        assert summary["total_events"] == 3
        assert summary["event_counts"]["rule_applied"] == 2
        assert summary["event_counts"]["measurement"] == 1

    def test_export_to_dict(self):
        """Export trace to dictionary (JSON-serializable)."""
        trace = MembraneTrace(description="Test run")
        trace.record_rule_applied(1, "root", "rule_A", {"X": 1}, {"Y": 1})

        exported = trace.export_to_dict()

        assert "metadata" in exported
        assert "events" in exported
        assert exported["metadata"]["total_events"] == 1
        assert len(exported["events"]) == 1

        # Verify JSON-serializable
        json_str = json.dumps(exported)
        assert json_str is not None

    def test_export_round_trip(self):
        """Export to JSON and back preserves data."""
        trace = MembraneTrace(description="Test")
        trace.record_rule_applied(1, "root", "rule_A", {"X": 1}, {"Y": 1})

        exported = trace.export_to_dict()
        json_str = json.dumps(exported)
        reimported = json.loads(json_str)

        assert reimported["metadata"]["description"] == "Test"
        assert reimported["metadata"]["total_events"] == 1
        assert reimported["events"][0]["rule_name"] == "rule_A"

    def test_events_chronological(self):
        """Events are recorded in chronological order."""
        trace = MembraneTrace()
        for i in range(5):
            trace.record_rule_applied(i, "root", f"rule_{i}")

        events = trace.get_events()
        assert len(events) == 5

        # Each event's step should be incrementing
        steps = [e.step for e in events]
        assert steps == [0, 1, 2, 3, 4]

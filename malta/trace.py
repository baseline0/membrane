"""Membrane execution tracing for audit and debugging.

Logs all rule applications, state transitions, and measurements to enable:
- Execution audit trail (what happened and when)
- Debugging (which rule triggered, what was the state before/after)
- Analysis (evolution of multiset, membrane structure over time)
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class TraceEvent:
    """Single event in membrane execution trace.

    Records what happened at a point in time.
    """

    timestamp: str  # ISO format: 2026-09-15T12:34:56.789Z
    event_type: str  # "rule_applied", "state_transition", "measurement", "membrane_created"
    step: int  # Generation or iteration number
    membrane_id: str  # Which membrane (e.g., "root", "skin", "inner_1")
    rule_name: str  # Name of rule that fired (or "system")
    details: dict = field(default_factory=dict)  # Event-specific data

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return asdict(self)


class MembraneTrace:
    """Audit trail of membrane execution.

    Records all significant events during simulation:
    - Rule applications and outcomes
    - State changes (multiset contents, quantum states)
    - Measurement collapses
    - Membrane topology changes
    """

    def __init__(self, description: str = ""):
        """Initialize trace.

        Args:
            description: Optional description of this trace (e.g., algorithm name)
        """
        self.description = description
        self.events: list[TraceEvent] = []
        self.start_time = datetime.now(timezone.utc)

    def record_rule_applied(
        self,
        step: int,
        membrane_id: str,
        rule_name: str,
        input_multiset: Optional[dict] = None,
        output_multiset: Optional[dict] = None,
        quantum_state_before: Optional[dict] = None,
        quantum_state_after: Optional[dict] = None,
    ) -> None:
        """Record a rule application.

        Args:
            step: Iteration/generation number
            membrane_id: Which membrane
            rule_name: Name of the rule
            input_multiset: Multiset items consumed
            output_multiset: Multiset items produced
            quantum_state_before: Quantum amplitudes before (optional)
            quantum_state_after: Quantum amplitudes after (optional)
        """
        event = TraceEvent(
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            event_type="rule_applied",
            step=step,
            membrane_id=membrane_id,
            rule_name=rule_name,
            details={
                "input": input_multiset or {},
                "output": output_multiset or {},
            },
        )

        if quantum_state_before is not None:
            event.details["quantum_before"] = quantum_state_before
        if quantum_state_after is not None:
            event.details["quantum_after"] = quantum_state_after

        self.events.append(event)

    def record_measurement(
        self,
        step: int,
        membrane_id: str,
        quantum_state_before: dict,
        outcome: str,
        probability: float,
    ) -> None:
        """Record a measurement event.

        Args:
            step: Iteration number
            membrane_id: Which membrane
            quantum_state_before: Superposition before measurement
            outcome: Basis state that was measured
            probability: Probability of this outcome
        """
        event = TraceEvent(
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            event_type="measurement",
            step=step,
            membrane_id=membrane_id,
            rule_name="measurement",
            details={
                "state_before": quantum_state_before,
                "outcome": outcome,
                "probability": probability,
            },
        )
        self.events.append(event)

    def record_state_transition(
        self,
        step: int,
        membrane_id: str,
        multiset_before: dict,
        multiset_after: dict,
        reason: str = "rule_application",
    ) -> None:
        """Record a state change.

        Args:
            step: Iteration number
            membrane_id: Which membrane changed
            multiset_before: Contents before
            multiset_after: Contents after
            reason: Why it changed (e.g., "rule_application", "membrane_creation")
        """
        event = TraceEvent(
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            event_type="state_transition",
            step=step,
            membrane_id=membrane_id,
            rule_name="system",
            details={
                "before": multiset_before,
                "after": multiset_after,
                "reason": reason,
            },
        )
        self.events.append(event)

    def record_membrane_created(
        self,
        step: int,
        parent_membrane_id: str,
        new_membrane_id: str,
        initial_multiset: Optional[dict] = None,
    ) -> None:
        """Record membrane creation event.

        Args:
            step: Iteration when created
            parent_membrane_id: Parent membrane
            new_membrane_id: ID of new membrane
            initial_multiset: Initial contents (optional)
        """
        event = TraceEvent(
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            event_type="membrane_created",
            step=step,
            membrane_id=new_membrane_id,
            rule_name="system",
            details={
                "parent": parent_membrane_id,
                "initial_multiset": initial_multiset or {},
            },
        )
        self.events.append(event)

    def get_events(self, membrane_id: Optional[str] = None) -> list[TraceEvent]:
        """Get trace events, optionally filtered by membrane.

        Args:
            membrane_id: If provided, return only events from this membrane

        Returns:
            List of trace events (chronological order)
        """
        if membrane_id is None:
            return self.events
        return [e for e in self.events if e.membrane_id == membrane_id]

    def get_events_by_type(self, event_type: str) -> list[TraceEvent]:
        """Get events of a specific type.

        Args:
            event_type: Event type filter (e.g., "measurement")

        Returns:
            List of matching events
        """
        return [e for e in self.events if e.event_type == event_type]

    def summary(self) -> dict:
        """Get summary statistics of execution.

        Returns:
            Dictionary with counts and summary info
        """
        event_counts = {}
        for event in self.events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

        duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        return {
            "description": self.description,
            "total_events": len(self.events),
            "event_counts": event_counts,
            "duration_seconds": duration,
            "start_time": self.start_time.isoformat() + "Z",
            "end_time": datetime.now(timezone.utc).isoformat() + "Z",
        }

    def export_to_dict(self) -> dict:
        """Export complete trace as dictionary.

        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            "metadata": self.summary(),
            "events": [e.to_dict() for e in self.events],
        }

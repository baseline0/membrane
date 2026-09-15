"""Export membrane simulation data to structured formats.

Supports JSON and YAML export for:
- Execution traces (events, timestamps, state transitions)
- Optimization results (best candidates, fitness, multiset state)
- Quantum state information (amplitudes, measurements)

Enables external analysis, visualization, and persistence.
"""

import json
from typing import Any, Optional
from pathlib import Path

from malta.trace import MembraneTrace


class SimulationExporter:
    """Export simulation results and traces to structured formats."""

    @staticmethod
    def export_trace_to_json(
        trace: MembraneTrace, output_path: Optional[Path] = None
    ) -> str:
        """Export trace to JSON string.

        Args:
            trace: MembraneTrace object to export
            output_path: If provided, write to file

        Returns:
            JSON string
        """
        exported = trace.export_to_dict()
        json_str = json.dumps(exported, indent=2)

        if output_path:
            output_path.write_text(json_str)

        return json_str

    @staticmethod
    def export_trace_to_yaml(
        trace: MembraneTrace, output_path: Optional[Path] = None
    ) -> str:
        """Export trace to YAML string.

        Args:
            trace: MembraneTrace object to export
            output_path: If provided, write to file

        Returns:
            YAML string
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

        exported = trace.export_to_dict()
        yaml_str = yaml.dump(exported, default_flow_style=False, sort_keys=False)

        if output_path:
            output_path.write_text(yaml_str)

        return yaml_str

    @staticmethod
    def export_optimization_result(
        best_candidate: Any,
        final_multiset: dict,
        trace: Optional[MembraneTrace] = None,
        output_path: Optional[Path] = None,
        format: str = "json",
    ) -> str:
        """Export optimization result (best candidate + final state).

        Args:
            best_candidate: Best solution found (e.g., Candidate object)
            final_multiset: Final membrane multiset state
            trace: Optional trace to include
            output_path: If provided, write to file
            format: "json" or "yaml"

        Returns:
            Formatted string
        """
        result = {
            "result": {
                "best_fitness": getattr(best_candidate, "fitness", None),
                "best_solution": getattr(best_candidate, "values", None),
            },
            "final_state": {"multiset": final_multiset},
        }

        if trace:
            result["trace"] = trace.export_to_dict()

        if format == "json":
            output_str = json.dumps(result, indent=2)
        elif format == "yaml":
            try:
                import yaml

                output_str = yaml.dump(
                    result, default_flow_style=False, sort_keys=False
                )
            except ImportError:
                raise ImportError(
                    "PyYAML not installed. Install with: pip install pyyaml"
                )
        else:
            raise ValueError(f"Unsupported format: {format}")

        if output_path:
            output_path.write_text(output_str)

        return output_str

    @staticmethod
    def export_quantum_state(
        quantum_state: dict,
        step: int,
        membrane_id: str,
        output_path: Optional[Path] = None,
    ) -> str:
        """Export quantum state snapshot.

        Args:
            quantum_state: Dict mapping basis states to amplitudes
            step: Iteration/generation number
            membrane_id: Which membrane
            output_path: If provided, write to file

        Returns:
            JSON string
        """
        snapshot = {
            "step": step,
            "membrane_id": membrane_id,
            "amplitudes": quantum_state,
            "probabilities": {
                basis: amp**2 for basis, amp in quantum_state.items()
            },
        }

        json_str = json.dumps(snapshot, indent=2)

        if output_path:
            output_path.write_text(json_str)

        return json_str

    @staticmethod
    def import_trace_from_json(json_path: Path) -> dict:
        """Load trace from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            Dictionary representation of trace
        """
        with open(json_path) as f:
            return json.load(f)

    @staticmethod
    def import_trace_from_yaml(yaml_path: Path) -> dict:
        """Load trace from YAML file.

        Args:
            yaml_path: Path to YAML file

        Returns:
            Dictionary representation of trace
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

        with open(yaml_path) as f:
            return yaml.safe_load(f)

"""Unit tests for quantum gates.

Tests verify:
- Hadamard gate creates correct superposition
- Measurement collapses to valid basis state
- Phase gate applies rotation
- State normalization
"""

import math

import pytest

from malta.quantum_gates import HadamardGate, MeasurementGate, PhaseGate, QuantumState


class TestQuantumState:
    """Tests for QuantumState management."""

    def test_quantum_state_initialization(self):
        """State initializes with vector and maintains amplitude."""
        state = QuantumState(state_vector={"A": 1.0})
        assert state.state_vector == {"A": 1.0}

    def test_normalization(self):
        """Normalization scales amplitudes to unit norm."""
        state = QuantumState(state_vector={"A": 1.0, "B": 1.0})
        state.normalize()

        # After normalization: each amplitude = 1/√2
        expected = 1.0 / math.sqrt(2)
        assert abs(state.state_vector["A"] - expected) < 1e-10
        assert abs(state.state_vector["B"] - expected) < 1e-10

    def test_normalization_sums_to_one(self):
        """After normalization, sum of probabilities = 1.0."""
        state = QuantumState(state_vector={"A": 2.0, "B": 2.0})
        state.normalize()

        prob_sum = sum(amp**2 for amp in state.state_vector.values())
        assert abs(prob_sum - 1.0) < 1e-10

    def test_state_copy(self):
        """Copy creates independent state."""
        state1 = QuantumState(state_vector={"A": 1.0})
        state2 = state1.copy()

        state2.state_vector["A"] = 0.5
        assert state1.state_vector["A"] == 1.0  # Original unchanged


class TestHadamardGate:
    """Tests for Hadamard gate (superposition rule)."""

    def test_hadamard_creates_superposition(self):
        """Hadamard splits |A⟩ into (|A_0⟩ + |A_1⟩)/√2."""
        gate = HadamardGate(target_state="A")
        state = QuantumState(state_vector={"A": 1.0})

        result = gate.apply_to_quantum_state(state, "A")

        expected_amp = 1.0 / math.sqrt(2)
        assert abs(result.state_vector["A_0"] - expected_amp) < 1e-10
        assert abs(result.state_vector["A_1"] - expected_amp) < 1e-10
        assert "A" not in result.state_vector

    def test_hadamard_preserves_probability(self):
        """Total probability remains 1.0 after Hadamard."""
        gate = HadamardGate(target_state="A")
        state = QuantumState(state_vector={"A": 1.0})

        result = gate.apply_to_quantum_state(state, "A")
        total_prob = sum(amp**2 for amp in result.state_vector.values())

        assert abs(total_prob - 1.0) < 1e-10

    def test_hadamard_on_nonexistent_state(self):
        """Hadamard on missing state returns unchanged."""
        gate = HadamardGate(target_state="A")
        state = QuantumState(state_vector={"B": 1.0})

        result = gate.apply_to_quantum_state(state, "A")

        assert result.state_vector == {"B": 1.0}

    def test_hadamard_with_superposition_amplitude(self):
        """Hadamard works on amplitudes < 1.0, always normalizes to 1/√2."""
        gate = HadamardGate(target_state="A")
        state = QuantumState(state_vector={"A": 0.5})

        result = gate.apply_to_quantum_state(state, "A")

        # Hadamard always produces 1/√2 amplitudes after normalization
        expected_amp = 1.0 / math.sqrt(2)
        assert abs(result.state_vector["A_0"] - expected_amp) < 1e-10
        assert abs(result.state_vector["A_1"] - expected_amp) < 1e-10

        # Total probability still 1.0
        total_prob = sum(amp**2 for amp in result.state_vector.values())
        assert abs(total_prob - 1.0) < 1e-10


class TestMeasurementGate:
    """Tests for measurement gate (collapse rule)."""

    def test_measurement_collapses_superposition(self):
        """Measurement produces single basis state."""
        gate = MeasurementGate()
        state = QuantumState(
            state_vector={"A": 1.0 / math.sqrt(2), "B": 1.0 / math.sqrt(2)}
        )

        result = gate.apply_to_quantum_state(state)

        # After collapse, exactly one state with amplitude 1.0
        assert len(result.state_vector) == 1
        collapsed_states = list(result.state_vector.keys())
        assert collapsed_states[0] in ["A", "B"]
        assert abs(result.state_vector[collapsed_states[0]] - 1.0) < 1e-10

    def test_measurement_respects_probabilities(self):
        """Measurement chooses outcomes proportional to |amplitude|²."""
        gate = MeasurementGate()

        # Run 1000 measurements to test statistical distribution
        outcomes = {"A": 0, "B": 0}
        state = QuantumState(
            state_vector={"A": 1.0 / math.sqrt(2), "B": 1.0 / math.sqrt(2)}
        )

        for _ in range(1000):
            result = gate.apply_to_quantum_state(state)
            outcome = list(result.state_vector.keys())[0]
            outcomes[outcome] += 1

        # Both outcomes should occur roughly 50% each (within 10% margin)
        a_ratio = outcomes["A"] / 1000
        b_ratio = outcomes["B"] / 1000
        assert 0.4 < a_ratio < 0.6
        assert 0.4 < b_ratio < 0.6

    def test_measurement_on_definite_state(self):
        """Measurement on definite state returns same state."""
        gate = MeasurementGate()
        state = QuantumState(state_vector={"A": 1.0})

        result = gate.apply_to_quantum_state(state)

        assert result.state_vector == {"A": 1.0}


class TestPhaseGate:
    """Tests for phase gate."""

    def test_phase_gate_rotates_amplitude(self):
        """Phase gate applies cos(θ) modulation."""
        angle = math.pi / 4
        gate = PhaseGate(phase_radians=angle)
        state = QuantumState(state_vector={"A": 1.0})

        result = gate.apply_to_quantum_state(state, "A")

        expected = math.cos(angle)
        assert abs(result.state_vector["A"] - expected) < 1e-10

    def test_phase_gate_single_state_probability_changes(self):
        """Phase gate reduces probability of target state (since cos < 1)."""
        gate = PhaseGate(phase_radians=math.pi / 4)
        state = QuantumState(state_vector={"A": 1.0})

        result = gate.apply_to_quantum_state(state, "A")

        # Amplitude reduced by cos(π/4) ≈ 0.707
        expected_amp = math.cos(math.pi / 4)
        assert abs(result.state_vector["A"] - expected_amp) < 1e-10

        # Probability is |amplitude|²
        expected_prob = expected_amp ** 2
        actual_prob = result.state_vector["A"] ** 2
        assert abs(actual_prob - expected_prob) < 1e-10

    def test_phase_gate_on_nonexistent_state(self):
        """Phase gate on missing state returns unchanged."""
        gate = PhaseGate()
        state = QuantumState(state_vector={"B": 1.0})

        result = gate.apply_to_quantum_state(state, "A")

        assert result.state_vector == {"B": 1.0}


class TestQuantumGateChaining:
    """Tests for sequential application of gates (common use case)."""

    def test_hadamard_then_measurement(self):
        """Apply Hadamard then measure."""
        h_gate = HadamardGate(target_state="A")
        m_gate = MeasurementGate()

        state = QuantumState(state_vector={"A": 1.0})
        state = h_gate.apply_to_quantum_state(state, "A")
        assert len(state.state_vector) == 2  # A_0 and A_1

        state = m_gate.apply_to_quantum_state(state)
        assert len(state.state_vector) == 1  # Collapsed to one outcome

    def test_double_hadamard(self):
        """Apply Hadamard twice (should collapse to original with phase info)."""
        h_gate = HadamardGate(target_state="A")
        state = QuantumState(state_vector={"A": 1.0})

        # First Hadamard: A → (A_0 + A_1)/√2
        state = h_gate.apply_to_quantum_state(state, "A")
        assert "A_0" in state.state_vector
        assert "A_1" in state.state_vector

        # Second Hadamard: applied to different targets (A_0, A_1)
        # This demonstrates need for more sophisticated gate handling
        # For now, test that we can chain applications
        h_gate_0 = HadamardGate(target_state="A_0")
        state = h_gate_0.apply_to_quantum_state(state, "A_0")

        # Verify probability is preserved
        total_prob = sum(amp**2 for amp in state.state_vector.values())
        assert abs(total_prob - 1.0) < 1e-10

"""Unit tests for Cyprus membrane lifecycle and execution model.

Tests the contracts codified in src/cyprus/contracts.py:
- MembraneState lifecycle (ACTIVE, DISSOLVED)
- ExecutionPhase state machine (STAGE1, STAGE2, HALT)
- Particle kinds and specifications (REGULAR, OSMOSE, DISSOLVE)
- ExecutionModel clock and phase semantics
"""

import pytest

from cyprus.contracts import (
    DissolutionParticleSpec,
    ExecutionModel,
    ExecutionPhase,
    MembraneState,
    OsmosisParticleSpec,
    ParticleKind,
    Stage1Config,
)


class TestMembraneState:
    """Tests for MembraneState enum."""

    def test_membrane_state_active(self):
        """ACTIVE state represents an intact membrane."""
        state = MembraneState.ACTIVE
        assert state.value == "active"
        assert state == MembraneState.ACTIVE

    def test_membrane_state_dissolved(self):
        """DISSOLVED state represents a dissolved membrane."""
        state = MembraneState.DISSOLVED
        assert state.value == "dissolved"
        assert state == MembraneState.DISSOLVED

    def test_membrane_states_are_distinct(self):
        """ACTIVE and DISSOLVED are distinct states."""
        assert MembraneState.ACTIVE != MembraneState.DISSOLVED

    def test_membrane_state_enumeration(self):
        """All membrane states are enumerable."""
        states = list(MembraneState)
        assert len(states) == 2
        assert MembraneState.ACTIVE in states
        assert MembraneState.DISSOLVED in states


class TestExecutionPhase:
    """Tests for ExecutionPhase enum."""

    def test_execution_phase_stage1(self):
        """STAGE1 represents reaction application phase."""
        phase = ExecutionPhase.STAGE1
        assert phase.value == "stage1"

    def test_execution_phase_stage2(self):
        """STAGE2 represents side-effect processing phase."""
        phase = ExecutionPhase.STAGE2
        assert phase.value == "stage2"

    def test_execution_phase_halt(self):
        """HALT represents clock termination."""
        phase = ExecutionPhase.HALT
        assert phase.value == "halt"

    def test_execution_phases_are_distinct(self):
        """All phases are distinct."""
        assert ExecutionPhase.STAGE1 != ExecutionPhase.STAGE2
        assert ExecutionPhase.STAGE2 != ExecutionPhase.HALT
        assert ExecutionPhase.HALT != ExecutionPhase.STAGE1

    def test_execution_phase_enumeration(self):
        """All execution phases are enumerable."""
        phases = list(ExecutionPhase)
        assert len(phases) == 3
        assert ExecutionPhase.STAGE1 in phases
        assert ExecutionPhase.STAGE2 in phases
        assert ExecutionPhase.HALT in phases


class TestParticleKind:
    """Tests for ParticleKind enum."""

    def test_particle_kind_regular(self):
        """REGULAR represents normal symbols."""
        kind = ParticleKind.REGULAR
        assert kind.value == "regular"

    def test_particle_kind_osmose(self):
        """OSMOSE represents particles that traverse membranes."""
        kind = ParticleKind.OSMOSE
        assert kind.value == "osmose"

    def test_particle_kind_dissolve(self):
        """DISSOLVE represents particles that trigger dissolution."""
        kind = ParticleKind.DISSOLVE
        assert kind.value == "dissolve"

    def test_particle_kinds_are_distinct(self):
        """All particle kinds are distinct."""
        assert ParticleKind.REGULAR != ParticleKind.OSMOSE
        assert ParticleKind.OSMOSE != ParticleKind.DISSOLVE
        assert ParticleKind.DISSOLVE != ParticleKind.REGULAR


class TestStage1Config:
    """Tests for Stage1Config dataclass."""

    def test_stage1_config_defaults(self):
        """Default Stage1Config uses maximal, non-deterministic application."""
        config = Stage1Config()
        assert config.max_iterations == 10000
        assert config.non_deterministic is True
        assert config.apply_maximally is True

    def test_stage1_config_custom_iterations(self):
        """Can customize max_iterations."""
        config = Stage1Config(max_iterations=100)
        assert config.max_iterations == 100

    def test_stage1_config_deterministic(self):
        """Can disable non-determinism for testing."""
        config = Stage1Config(non_deterministic=False)
        assert config.non_deterministic is False

    def test_stage1_config_non_maximal(self):
        """Can disable maximal application (research only)."""
        config = Stage1Config(apply_maximally=False)
        assert config.apply_maximally is False

    def test_stage1_config_frozen(self):
        """Stage1Config is immutable."""
        config = Stage1Config()
        with pytest.raises(AttributeError):
            config.max_iterations = 5000  # type: ignore[attr-defined]

    def test_stage1_config_validates_max_iterations_positive(self):
        """max_iterations must be >= 1."""
        with pytest.raises(ValueError, match="max_iterations must be >= 1"):
            Stage1Config(max_iterations=0)

    def test_stage1_config_validates_max_iterations_negative(self):
        """max_iterations cannot be negative."""
        with pytest.raises(ValueError, match="max_iterations must be >= 1"):
            Stage1Config(max_iterations=-1)

    def test_stage1_config_min_iterations(self):
        """min value of 1 is accepted."""
        config = Stage1Config(max_iterations=1)
        assert config.max_iterations == 1


class TestDissolutionParticleSpec:
    """Tests for DissolutionParticleSpec dataclass."""

    def test_dissolution_particle_self_dissolve(self):
        """DissolveParticle with no target dissolves self."""
        spec = DissolutionParticleSpec()
        assert spec.target is None
        assert spec.payload is None

    def test_dissolution_particle_named_target(self):
        """DissolveParticle can target a named membrane."""
        spec = DissolutionParticleSpec(target="membrane_x")
        assert spec.target == "membrane_x"

    def test_dissolution_particle_frozen(self):
        """DissolutionParticleSpec is immutable."""
        spec = DissolutionParticleSpec()
        with pytest.raises(AttributeError):
            spec.target = "membrane_y"  # type: ignore[attr-defined]

    def test_dissolution_particle_validates_empty_target(self):
        """target cannot be an empty string."""
        with pytest.raises(ValueError, match="target must be None or a non-empty string"):
            DissolutionParticleSpec(target="")

    def test_dissolution_particle_payload_optional(self):
        """payload is optional (kept for API compatibility)."""
        spec = DissolutionParticleSpec(payload="x")
        assert spec.payload == "x"

    def test_dissolution_particle_valid_combinations(self):
        """Valid combinations of target and payload."""
        # Self-dissolution with no payload
        spec1 = DissolutionParticleSpec()
        assert spec1.target is None and spec1.payload is None

        # Self-dissolution with payload (ignored)
        spec2 = DissolutionParticleSpec(payload="x")
        assert spec2.target is None and spec2.payload == "x"

        # Named dissolution with no payload
        spec3 = DissolutionParticleSpec(target="m1")
        assert spec3.target == "m1" and spec3.payload is None

        # Named dissolution with payload
        spec4 = DissolutionParticleSpec(target="m1", payload="x")
        assert spec4.target == "m1" and spec4.payload == "x"


class TestOsmosisParticleSpec:
    """Tests for OsmosisParticleSpec dataclass."""

    def test_osmosis_particle_to_parent(self):
        """OsmoseParticle can osmose to parent (no target)."""
        spec = OsmosisParticleSpec(payload="x")
        assert spec.target is None
        assert spec.payload == "x"

    def test_osmosis_particle_to_named_target(self):
        """OsmoseParticle can target a named membrane."""
        spec = OsmosisParticleSpec(payload="x", target="membrane_y")
        assert spec.target == "membrane_y"
        assert spec.payload == "x"

    def test_osmosis_particle_frozen(self):
        """OsmosisParticleSpec is immutable."""
        spec = OsmosisParticleSpec(payload="x")
        with pytest.raises(AttributeError):
            spec.payload = "y"  # type: ignore[attr-defined]

    def test_osmosis_particle_validates_payload_not_none(self):
        """payload is required and cannot be None."""
        with pytest.raises(ValueError, match="payload must be a non-empty string"):
            OsmosisParticleSpec(payload=None)

    def test_osmosis_particle_validates_payload_not_empty(self):
        """payload cannot be an empty string."""
        with pytest.raises(ValueError, match="payload must be a non-empty string"):
            OsmosisParticleSpec(payload="")

    def test_osmosis_particle_validates_target_not_empty(self):
        """target cannot be an empty string."""
        with pytest.raises(ValueError, match="target must be None or a non-empty string"):
            OsmosisParticleSpec(payload="x", target="")

    def test_osmosis_particle_valid_payloads(self):
        """Valid payload examples."""
        for payload in ["a", "x", "symbol123", "A", "PARTICLE"]:
            spec = OsmosisParticleSpec(payload=payload)
            assert spec.payload == payload

    def test_osmosis_particle_valid_targets(self):
        """Valid target examples."""
        for target in ["m1", "membrane_a", "nested_x"]:
            spec = OsmosisParticleSpec(payload="x", target=target)
            assert spec.target == target


class TestExecutionModel:
    """Tests for ExecutionModel dataclass."""

    def test_execution_model_default(self):
        """Default ExecutionModel starts in STAGE1."""
        model = ExecutionModel.default()
        assert model.current_phase == ExecutionPhase.STAGE1
        assert model.should_halt is False
        assert model.rule_applied_in_stage1 is False

    def test_execution_model_custom_stage1_config(self):
        """ExecutionModel accepts custom Stage1Config."""
        config = Stage1Config(max_iterations=100)
        model = ExecutionModel(stage1_config=config)
        assert model.stage1_config.max_iterations == 100

    def test_execution_model_frozen(self):
        """ExecutionModel is immutable."""
        model = ExecutionModel.default()
        with pytest.raises(AttributeError):
            model.current_phase = ExecutionPhase.STAGE2  # type: ignore[attr-defined]

    def test_execution_model_cannot_halt_in_stage1(self):
        """Cannot set should_halt=True while in STAGE1."""
        with pytest.raises(ValueError, match="should_halt cannot be True while in stage1"):
            ExecutionModel(
                stage1_config=Stage1Config(),
                current_phase=ExecutionPhase.STAGE1,
                should_halt=True,
            )

    def test_execution_model_cannot_halt_in_stage2(self):
        """Cannot set should_halt=True while in STAGE2."""
        with pytest.raises(ValueError, match="should_halt cannot be True while in stage2"):
            ExecutionModel(
                stage1_config=Stage1Config(),
                current_phase=ExecutionPhase.STAGE2,
                should_halt=True,
            )

    def test_execution_model_must_halt_in_halt_phase(self):
        """When current_phase is HALT, should_halt must be True."""
        with pytest.raises(ValueError, match="current_phase cannot be HALT unless should_halt is True"):
            ExecutionModel(
                stage1_config=Stage1Config(),
                current_phase=ExecutionPhase.HALT,
                should_halt=False,
            )

    def test_execution_model_valid_halt_state(self):
        """Valid HALT state has should_halt=True."""
        model = ExecutionModel(
            stage1_config=Stage1Config(),
            current_phase=ExecutionPhase.HALT,
            should_halt=True,
        )
        assert model.current_phase == ExecutionPhase.HALT
        assert model.should_halt is True

    def test_execution_model_rule_applied_flag(self):
        """rule_applied_in_stage1 tracks reaction application."""
        config = Stage1Config()
        model = ExecutionModel(
            stage1_config=config,
            current_phase=ExecutionPhase.STAGE1,
            rule_applied_in_stage1=True,
        )
        assert model.rule_applied_in_stage1 is True

    def test_execution_model_state_machine_progression(self):
        """Valid state machine progressions."""
        config = Stage1Config()

        # Start in STAGE1, rules applied
        state1 = ExecutionModel(
            stage1_config=config,
            current_phase=ExecutionPhase.STAGE1,
            rule_applied_in_stage1=True,
        )
        assert state1.current_phase == ExecutionPhase.STAGE1
        assert state1.should_halt is False

        # Move to STAGE2
        state2 = ExecutionModel(
            stage1_config=config,
            current_phase=ExecutionPhase.STAGE2,
            rule_applied_in_stage1=True,
            should_halt=False,
        )
        assert state2.current_phase == ExecutionPhase.STAGE2

        # Move to HALT (no more reactions apply)
        state3 = ExecutionModel(
            stage1_config=config,
            current_phase=ExecutionPhase.HALT,
            rule_applied_in_stage1=False,
            should_halt=True,
        )
        assert state3.current_phase == ExecutionPhase.HALT
        assert state3.should_halt is True


class TestContractsIntegration:
    """Integration tests across multiple contract types."""

    def test_full_execution_lifecycle(self):
        """Simulate a complete execution lifecycle with contracts."""
        # Start execution
        model = ExecutionModel.default()
        assert model.current_phase == ExecutionPhase.STAGE1

        # Stage 1: Create dissolution spec
        dissolution = DissolutionParticleSpec(target="m1")
        assert dissolution.target == "m1"

        # Create osmosis spec
        osmosis = OsmosisParticleSpec(payload="x", target="m2")
        assert osmosis.payload == "x"
        assert osmosis.target == "m2"

        # Move to stage 2 (with rule application recorded)
        model_after_stage1 = ExecutionModel(
            stage1_config=model.stage1_config,
            current_phase=ExecutionPhase.STAGE2,
            rule_applied_in_stage1=True,
        )
        assert model_after_stage1.current_phase == ExecutionPhase.STAGE2
        assert model_after_stage1.rule_applied_in_stage1 is True

        # Halt when no more reactions
        model_halted = ExecutionModel(
            stage1_config=model.stage1_config,
            current_phase=ExecutionPhase.HALT,
            rule_applied_in_stage1=False,
            should_halt=True,
        )
        assert model_halted.current_phase == ExecutionPhase.HALT

    def test_membrane_state_with_particle_actions(self):
        """Membranes can transition via particle actions."""
        # Membrane is ACTIVE
        state = MembraneState.ACTIVE
        assert state == MembraneState.ACTIVE

        # Reaction produces DissolveParticle
        dissolution = DissolutionParticleSpec()
        assert dissolution is not None

        # After dissolution in Stage 2, membrane is DISSOLVED
        dissolved_state = MembraneState.DISSOLVED
        assert dissolved_state == MembraneState.DISSOLVED
        assert state != dissolved_state

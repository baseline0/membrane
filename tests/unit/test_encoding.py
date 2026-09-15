"""Unit tests for binary encodings.

Tests verify:
- Bits to values and back (round-trip)
- Multi-bit encoding for multi-dimensional spaces
- Gray code conversions
- Progressive encoding over generations
"""

import pytest

from malta.encoding import BinaryEncoding, MultibitEncoder, ProgressiveEncoding


class TestBinaryEncoding:
    """Tests for single-dimension binary encoding."""

    def test_bits_to_value_all_zeros(self):
        """All zeros maps to lower bound."""
        value = BinaryEncoding.bits_to_value("0000", (-5.0, 5.0))
        assert value == -5.0

    def test_bits_to_value_all_ones(self):
        """All ones maps to upper bound."""
        value = BinaryEncoding.bits_to_value("1111", (-5.0, 5.0))
        assert abs(value - 5.0) < 0.01  # Allow small numerical error

    def test_bits_to_value_midpoint(self):
        """Midpoint bits map near center."""
        # 1000 (binary 8) is midpoint of 0-15
        value = BinaryEncoding.bits_to_value("1000", (-10.0, 10.0))
        assert abs(value - 0.0) < 1.0  # Should be near 0

    def test_value_to_bits_lower(self):
        """Lower bound encodes to all zeros."""
        bits = BinaryEncoding.value_to_bits(-5.0, (-5.0, 5.0), 4)
        assert bits == "0000"

    def test_value_to_bits_upper(self):
        """Upper bound encodes to all ones."""
        bits = BinaryEncoding.value_to_bits(5.0, (-5.0, 5.0), 4)
        assert bits == "1111"

    def test_value_to_bits_center(self):
        """Center value encodes to middle bits."""
        bits = BinaryEncoding.value_to_bits(0.0, (-10.0, 10.0), 4)
        # Should be around 1000 (8 in decimal)
        as_int = int(bits, 2)
        assert 6 <= as_int <= 10  # Close to midpoint

    def test_round_trip(self):
        """Value -> bits -> value preserves value (within quantization)."""
        bounds = (-5.0, 5.0)
        original = 2.5

        bits = BinaryEncoding.value_to_bits(original, bounds, 8)
        recovered = BinaryEncoding.bits_to_value(bits, bounds)

        # Should be close (within quantization error)
        assert abs(original - recovered) < 0.1

    def test_bits_to_value_empty_bits(self):
        """Empty bits defaults to lower bound."""
        value = BinaryEncoding.bits_to_value("", (-5.0, 5.0))
        assert value == -5.0

    def test_gray_to_binary_single_bit(self):
        """Single bit Gray/binary equivalence."""
        assert BinaryEncoding.gray_to_binary("0") == "0"
        assert BinaryEncoding.gray_to_binary("1") == "1"

    def test_gray_to_binary_two_bits(self):
        """Two-bit Gray code conversion."""
        # Gray: 00->0, 01->1, 11->2, 10->3
        # Binary: 00, 01, 10, 11
        assert BinaryEncoding.gray_to_binary("00") == "00"
        assert BinaryEncoding.gray_to_binary("01") == "01"
        assert BinaryEncoding.gray_to_binary("11") == "10"
        assert BinaryEncoding.gray_to_binary("10") == "11"

    def test_binary_to_gray_round_trip(self):
        """Binary -> Gray -> Binary preserves value."""
        binary = "1010"
        gray = BinaryEncoding.binary_to_gray(binary)
        recovered = BinaryEncoding.gray_to_binary(gray)
        assert recovered == binary


class TestMultibitEncoder:
    """Tests for multi-dimensional multi-bit encoding."""

    def test_encoder_initialization(self):
        """Encoder initializes with correct dimensions."""
        encoder = MultibitEncoder(n_dims=3, n_bits_per_dim=4, bounds=(-5.0, 5.0))
        assert encoder.n_dims == 3
        assert encoder.n_bits_per_dim == 4
        assert encoder.total_bits == 12

    def test_basis_state_to_solution_all_zeros(self):
        """All-zero basis state gives lower bounds."""
        encoder = MultibitEncoder(2, 4, (-5.0, 5.0))
        solution = encoder.basis_state_to_solution("00000000")

        assert len(solution) == 2
        assert solution[0] == -5.0
        assert solution[1] == -5.0

    def test_basis_state_to_solution_all_ones(self):
        """All-one basis state gives upper bounds."""
        encoder = MultibitEncoder(2, 4, (-5.0, 5.0))
        solution = encoder.basis_state_to_solution("11111111")

        assert len(solution) == 2
        assert abs(solution[0] - 5.0) < 0.1
        assert abs(solution[1] - 5.0) < 0.1

    def test_solution_to_basis_state_round_trip(self):
        """Solution -> basis -> solution preserves value."""
        encoder = MultibitEncoder(2, 8, (-10.0, 10.0))
        original = [2.5, -3.7]

        basis = encoder.solution_to_basis_state(original)
        recovered = encoder.basis_state_to_solution(basis)

        assert len(recovered) == 2
        assert abs(original[0] - recovered[0]) < 0.2
        assert abs(original[1] - recovered[1]) < 0.2

    def test_basis_state_padding(self):
        """Short basis states are padded with zeros."""
        encoder = MultibitEncoder(2, 4, (-5.0, 5.0))
        solution = encoder.basis_state_to_solution("11")  # Too short

        assert len(solution) == 2
        # First bits "11" should decode to upper, padding makes lower
        assert solution[0] > 0

    def test_basis_state_truncation(self):
        """Long basis states are truncated."""
        encoder = MultibitEncoder(2, 4, (-5.0, 5.0))
        solution = encoder.basis_state_to_solution("1" * 20)  # Too long

        assert len(solution) == 2

    def test_random_basis_state(self):
        """Random basis state has correct length."""
        encoder = MultibitEncoder(5, 4, (-1.0, 1.0))
        basis = encoder.random_basis_state()

        assert len(basis) == 20  # 5 dims × 4 bits
        assert all(b in "01" for b in basis)

    def test_get_basis_dimension(self):
        """Basis dimension is 2^total_bits."""
        encoder = MultibitEncoder(2, 4, (-5.0, 5.0))
        assert encoder.get_basis_dimension() == 2 ** 8

    def test_invalid_solution_length(self):
        """Wrong solution length raises error."""
        encoder = MultibitEncoder(3, 4, (-5.0, 5.0))
        with pytest.raises(ValueError):
            encoder.solution_to_basis_state([1.0, 2.0])  # Only 2, need 3


class TestProgressiveEncoding:
    """Tests for progressive encoding over generations."""

    def test_initialization(self):
        """Progressive encoder initializes correctly."""
        encoder = ProgressiveEncoding(n_dims=5, min_bits_per_dim=1, max_bits_per_dim=8)
        assert encoder.n_dims == 5
        assert encoder.min_bits == 1
        assert encoder.max_bits == 8
        assert encoder.current_bits == 1

    def test_generation_zero(self):
        """Generation 0 uses minimum bits."""
        encoder = ProgressiveEncoding(2, min_bits_per_dim=2, max_bits_per_dim=8)
        encoder.set_generation(0, 100)
        assert encoder.current_bits == 2

    def test_generation_final(self):
        """Final generation uses maximum bits."""
        encoder = ProgressiveEncoding(2, min_bits_per_dim=2, max_bits_per_dim=8)
        encoder.set_generation(100, 100)
        assert encoder.current_bits == 8

    def test_generation_midpoint(self):
        """Midpoint generation uses intermediate bits."""
        encoder = ProgressiveEncoding(2, min_bits_per_dim=2, max_bits_per_dim=10)
        encoder.set_generation(50, 100)
        # Should be around (2 + 10) / 2 = 6
        assert 5 <= encoder.current_bits <= 7

    def test_get_encoder(self):
        """get_encoder returns encoder with current resolution."""
        prog = ProgressiveEncoding(3, min_bits_per_dim=2, max_bits_per_dim=6)
        prog.set_generation(50, 100)

        enc = prog.get_encoder()

        assert isinstance(enc, MultibitEncoder)
        assert enc.n_bits_per_dim == prog.current_bits

    def test_monotonic_increase(self):
        """Bits increase monotonically over generations."""
        encoder = ProgressiveEncoding(2, 1, 8)
        bits_history = []

        for gen in range(0, 101, 10):
            encoder.set_generation(gen, 100)
            bits_history.append(encoder.current_bits)

        # Should be non-decreasing
        for i in range(1, len(bits_history)):
            assert bits_history[i] >= bits_history[i - 1]

    def test_zero_total_gens(self):
        """Zero total generations uses minimum."""
        encoder = ProgressiveEncoding(2, min_bits_per_dim=3, max_bits_per_dim=8)
        encoder.set_generation(5, 0)  # Edge case
        assert encoder.current_bits == 3

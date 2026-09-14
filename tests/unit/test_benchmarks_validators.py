"""Tests for benchmarks.validators: seed, dimension, result validation."""

import pytest

from benchmarks.validators import (
    ValidationError,
    validate_dimension,
    validate_function_id,
    validate_n_seeds,
    validate_result_bounds,
    validate_result_finite,
    validate_seed,
)


class TestSeedValidation:
    """Verify seed validation enforces valid range."""

    def test_valid_seed(self):
        """Valid seeds should not raise."""
        validate_seed(0)
        validate_seed(42)
        validate_seed(2**31 - 1)

    def test_negative_seed_rejected(self):
        """Negative seeds should raise ValidationError."""
        with pytest.raises(ValidationError, match="seed must be in"):
            validate_seed(-1)

    def test_oversized_seed_rejected(self):
        """Seeds > 2^31-1 should raise ValidationError."""
        with pytest.raises(ValidationError, match="seed must be in"):
            validate_seed(2**31)

    def test_non_int_seed_rejected(self):
        """Non-integer seeds should raise ValidationError."""
        with pytest.raises(ValidationError, match="seed must be int"):
            validate_seed(3.14)


class TestDimensionValidation:
    """Verify dimension validation."""

    def test_valid_dimensions(self):
        """Standard CEC2017 dimensions should be valid."""
        for dim in (10, 30, 50, 100):
            validate_dimension(dim)

    def test_invalid_dimension_rejected(self):
        """Unsupported dimensions should raise ValidationError."""
        with pytest.raises(ValidationError, match="not supported"):
            validate_dimension(20)


class TestFunctionIdValidation:
    """Verify function ID validation."""

    def test_valid_function_ids(self):
        """IDs 1-30 (except 2) should be valid."""
        for fid in [1, 3, 4, 29, 30]:
            validate_function_id(fid)

    def test_function_2_rejected(self):
        """F2 was removed from CEC2017."""
        with pytest.raises(ValidationError, match="F2.* removed"):
            validate_function_id(2)

    def test_out_of_range_rejected(self):
        """IDs outside [1, 30] should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be in"):
            validate_function_id(0)
        with pytest.raises(ValidationError, match="must be in"):
            validate_function_id(31)


class TestNSeedsValidation:
    """Verify statistical rigor threshold."""

    def test_adequate_seeds(self):
        """30+ seeds should be valid."""
        validate_n_seeds(30)
        validate_n_seeds(100)

    def test_insufficient_seeds_rejected(self):
        """< 30 seeds should raise ValidationError."""
        with pytest.raises(ValidationError, match="below statistical minimum"):
            validate_n_seeds(29)


class TestResultFiniteValidation:
    """Verify result sanity checks."""

    def test_valid_finite_result(self):
        """Finite numeric results should be valid."""
        validate_result_finite(0.0)
        validate_result_finite(100.5)
        validate_result_finite(-50.2)
        validate_result_finite(1e100)

    def test_non_numeric_rejected(self):
        """Non-numeric results should raise ValidationError."""
        with pytest.raises(ValidationError, match="must be numeric"):
            validate_result_finite("100")

    def test_inf_rejected(self):
        """Infinite results should raise ValidationError."""
        with pytest.raises(ValidationError, match="not finite"):
            validate_result_finite(float("inf"))


class TestResultBoundsValidation:
    """Verify result bounds check."""

    def test_reasonable_result(self):
        """Result near optimum should be valid."""
        func_id = 1
        dim = 10
        optimum = func_id * 100.0
        validate_result_bounds(optimum, func_id, dim)
        validate_result_bounds(optimum * 2, func_id, dim)
        validate_result_bounds(optimum * 0.5, func_id, dim)

    def test_outlier_result_rejected(self):
        """Result far from optimum should raise ValidationError."""
        func_id = 1
        dim = 10
        with pytest.raises(ValidationError, match="far outside expected range"):
            validate_result_bounds(10000.0, func_id, dim)

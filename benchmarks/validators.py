"""Benchmarking validators: ensure reproducibility and result sanity."""

from typing import Tuple


class ValidationError(ValueError):
    """Raised when benchmark parameters or results fail validation."""

    pass


def validate_seed(seed: int) -> None:
    """Ensure seed is a valid 32-bit integer."""
    if not isinstance(seed, int):
        raise ValidationError(f"seed must be int, got {type(seed).__name__}")
    if seed < 0 or seed > 2**31 - 1:
        raise ValidationError(f"seed must be in [0, 2^31-1], got {seed}")


def validate_dimension(dimension: int, supported: Tuple[int, ...] = (10, 30, 50, 100)) -> None:
    """Ensure dimension is supported by the benchmark suite."""
    if dimension not in supported:
        raise ValidationError(f"dimension {dimension} not supported. Choose from {supported}")


def validate_function_id(func_id: int, max_id: int = 30) -> None:
    """Ensure function ID is valid (CEC2017: 1-30, excluding F2)."""
    if func_id < 1 or func_id > max_id:
        raise ValidationError(f"function ID must be in [1, {max_id}], got {func_id}")
    if func_id == 2:
        raise ValidationError("Function 2 (F2) was removed from CEC2017 benchmark")


def validate_n_seeds(n_seeds: int, min_seeds: int = 30) -> None:
    """Ensure n_seeds meets statistical rigor threshold."""
    if n_seeds < min_seeds:
        raise ValidationError(
            f"n_seeds={n_seeds} below statistical minimum ({min_seeds}). "
            f"Wilcoxon tests require >=30 samples for robustness."
        )


def validate_result_finite(result: float, label: str = "result") -> None:
    """Ensure result is finite (not NaN or inf)."""
    if not isinstance(result, (int, float)):
        raise ValidationError(f"{label} must be numeric, got {type(result).__name__}")
    if not (-1e308 < result < 1e308):
        raise ValidationError(f"{label} is not finite: {result}")


def validate_result_bounds(result: float, func_id: int, dimension: int) -> None:
    """
    Sanity check: result should be close to expected optimum value.
    CEC2017 optimum = func_id * 100.
    Allow ±10x for algorithm slack.
    """
    optimum = func_id * 100.0
    lower = optimum * 0.1
    upper = optimum * 10.0

    if result < lower or result > upper:
        raise ValidationError(
            f"Result {result} on F{func_id}/{dimension}D far outside expected range "
            f"[{lower}, {upper}] (optimum={optimum}). "
            f"Check algorithm convergence or function evaluation."
        )

"""CEC2017 Special Session Benchmark Suite wrapper using opfunu library."""

import numpy as np
import numpy.typing as npt
from opfunu.cec_based.cec2017 import (
    F1,
    F3,
    F4,
    F5,
    F6,
    F7,
    F8,
    F9,
    F10,
    F11,
    F12,
    F13,
    F14,
    F15,
    F16,
    F17,
    F18,
    F19,
    F20,
    F21,
    F22,
    F23,
    F24,
    F25,
    F26,
    F27,
    F28,
    F29,
    F30,
)

from benchmarks.suites.base import BenchmarkFunction, BenchmarkSuite

# CEC2017 function names (F1–F30, excluding F2 which was removed)
CEC2017_NAMES: dict[int, str] = {
    1: "Shifted and Rotated Bent Cigar Function",
    3: "Shifted and Rotated Rosenbrock's Function",
    4: "Shifted and Rotated Rastrigin's Function",
    5: "Shifted and Rotated Expanded Scaffer's F6 Function",
    6: "Shifted and Rotated Lunacek Bi-Rastrigin Function",
    7: "Shifted and Rotated Non-Continuous Rastrigin's Function",
    8: "Shifted and Rotated Levy Function",
    9: "Shifted and Rotated Schwefel's Function",
    10: "Shifted and Rotated High Conditioned Elliptic Function",
    11: "Hybrid Function 1 (N=3)",
    12: "Hybrid Function 2 (N=3)",
    13: "Hybrid Function 3 (N=3)",
    14: "Hybrid Function 4 (N=4)",
    15: "Hybrid Function 5 (N=4)",
    16: "Hybrid Function 6 (N=5)",
    17: "Hybrid Function 7 (N=5)",
    18: "Hybrid Function 8 (N=5)",
    19: "Hybrid Function 9 (N=6)",
    20: "Hybrid Function 10 (N=6)",
    21: "Composition Function 1 (N=3)",
    22: "Composition Function 2 (N=3)",
    23: "Composition Function 3 (N=4)",
    24: "Composition Function 4 (N=4)",
    25: "Composition Function 5 (N=5)",
    26: "Composition Function 6 (N=5)",
    27: "Composition Function 7 (N=6)",
    28: "Composition Function 8 (N=6)",
    29: "Composition Function 9 (N=10)",
    30: "Composition Function 10 (N=10)",
}

# Map function IDs to opfunu class constructors
OPFUNU_CLASSES = {
    1: F1,
    3: F3,
    4: F4,
    5: F5,
    6: F6,
    7: F7,
    8: F8,
    9: F9,
    10: F10,
    11: F11,
    12: F12,
    13: F13,
    14: F14,
    15: F15,
    16: F16,
    17: F17,
    18: F18,
    19: F19,
    20: F20,
    21: F21,
    22: F22,
    23: F23,
    24: F24,
    25: F25,
    26: F26,
    27: F27,
    28: F28,
    29: F29,
    30: F30,
}


class CEC2017Suite(BenchmarkSuite):
    """CEC2017 Special Session Benchmark Suite using opfunu library."""

    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "CEC2017"

    @property
    def supported_dimensions(self) -> list[int]:
        return [10, 30, 50, 100]

    def _validate_dimension(self, dimension: int) -> None:
        if dimension not in self.supported_dimensions:
            raise ValueError(
                f"Dimension {dimension} not supported by CEC2017. Must be one of {self.supported_dimensions}."
            )

    def get_function(self, func_id: int | str, dimension: int) -> BenchmarkFunction:
        fid = int(func_id)
        self._validate_dimension(dimension)

        if fid not in OPFUNU_CLASSES:
            raise ValueError(f"Function ID {fid} invalid for CEC2017. (Note: F2 was deleted from official suite).")

        opfunu_obj = OPFUNU_CLASSES[fid](ndim=dimension)

        def eval_wrapper(x: npt.NDArray[np.float64]) -> float:
            return float(opfunu_obj.evaluate(x))

        return BenchmarkFunction(
            id=fid,
            name=f"F{fid}: {CEC2017_NAMES[fid]}",
            dimension=dimension,
            bounds=(-100.0, 100.0),
            optimum_value=float(fid * 100),
            func=eval_wrapper,
        )

    def list_functions(self, dimension: int) -> list[BenchmarkFunction]:
        self._validate_dimension(dimension)
        return [self.get_function(fid, dimension) for fid in sorted(CEC2017_NAMES.keys())]

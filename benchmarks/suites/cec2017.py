"""CEC2017 Special Session Benchmark Suite wrapper with ctypes C binding."""

import ctypes
from pathlib import Path

import numpy as np
import numpy.typing as npt

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


class CEC2017CBinding:
    """Low-level ctypes wrapper around compiled libcec2017 shared library."""

    def __init__(self, lib_path: Path):
        if not lib_path.exists():
            raise FileNotFoundError(
                f"CEC2017 shared library not found at '{lib_path}'. Build it using 'just build-cec2017'."
            )

        self.lib = ctypes.CDLL(str(lib_path.resolve()))

        # C signature: void cec17_test_func(double *x, double *f, int nx, int mx, int func_num)
        self._test_func = self.lib.cec17_test_func
        self._test_func.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self._test_func.restype = None

    def evaluate(self, x: npt.NDArray[np.float64], func_num: int) -> float:
        """Evaluates a single 1D numpy array on function func_num."""
        nx = len(x)
        mx = 1
        f = np.zeros(1, dtype=np.float64)

        x_ptr = x.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        f_ptr = f.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        self._test_func(x_ptr, f_ptr, nx, mx, func_num)
        return float(f[0])


class CEC2017Suite(BenchmarkSuite):
    """Concrete implementation of the CEC2017 Special Session Benchmark Suite."""

    DEFAULT_LIB_DIR = Path("benchmarks/c_src/cec2017")

    def __init__(self, lib_dir: Path | None = None):
        self._lib_dir = lib_dir or self.DEFAULT_LIB_DIR
        lib_file = self._lib_dir / "libcec2017.so"
        self._binding = CEC2017CBinding(lib_file)

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

        if fid not in CEC2017_NAMES:
            raise ValueError(f"Function ID {fid} invalid for CEC2017. (Note: F2 was deleted from official suite).")

        # Theoretical global minimum f(x*) = fid * 100.0
        optimum = float(fid * 100)

        def eval_wrapper(x: npt.NDArray[np.float64]) -> float:
            return self._binding.evaluate(x, fid)

        return BenchmarkFunction(
            id=fid,
            name=f"F{fid}: {CEC2017_NAMES[fid]}",
            dimension=dimension,
            bounds=(-100.0, 100.0),
            optimum_value=optimum,
            func=eval_wrapper,
        )

    def list_functions(self, dimension: int) -> list[BenchmarkFunction]:
        self._validate_dimension(dimension)
        return [self.get_function(fid, dimension) for fid in sorted(CEC2017_NAMES.keys())]

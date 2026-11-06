# CEC2017 Benchmark Library

The repo tracks no CEC2017 source. The committed `cec17_test_func.c` is a stub (a sum of squares plus `func_num * 100`)
that keeps the ctypes wiring buildable and testable. Real CEC2017 values come only from a local build of the upstream
source, which is not redistributable and is never committed.

## Building

```bash
just build-cec2017                                   # the tracked stub: plumbing only
CEC2017_SRC="<path>/codes/C version" just build-cec2017   # the real bound-constrained functions, local use only
```

With `CEC2017_SRC`, the recipe compiles the upstream `cec17_test_func.cpp` with gcc and links `cec17_shim.cpp`, which
supplies the global state the upstream expects and the C-linkage `cec17_test_func` the loader calls. It applies two
Linux fixes the upstream readme names: it drops `<WINDOWS.H>`, and it reads doubles with `%lf`, not `%Lf`. It copies the
upstream `input_data/` next to the library. Both the library and `input_data/` are gitignored.

`benchmarks/suites/cec2017.py` runs each call from the library's directory, because the upstream reads its data
from `input_data/...` relative to the working directory.

## Checks

- The real build evaluates F1 (10-D) to exactly 100.0 at the first shift vector in `shift_data_1.txt`, the function's
  known optimum.
- The stub build returns sum-of-squares-plus-offset values, so it fails that check; the tests still pass on it.

## Licence and use

The upstream source (Noor Awad, NTU; CEC2017 suite by P. N. Suganthan and collaborators) carries no licence text. Without a
licence the author keeps the rights, so:

- Keep the local build for internal research only. Do not commit the source, the `input_data/` matrices, or the
  built library.
- Before a result that uses this suite is published, get the author's permission or confirm the licence, and cite the
  benchmark's authors.

## Troubleshooting

**`gcc: command not found`:** install a C++ compiler (for example `sudo apt install build-essential`), then rerun.

**`CEC2017_SRC has no cec17_test_func.cpp`:** point `CEC2017_SRC` at the `C version` directory, the one that holds
`cec17_test_func.cpp` and `input_data/`.

**Results are inf or implausibly large:** rebuild with `CEC2017_SRC`; the `%Lf` fix is applied by the recipe, and the
stub never reads input data.

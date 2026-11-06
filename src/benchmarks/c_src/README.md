# CEC2017 Benchmark Library

**Status: the tracked source is a stub.** `cec17_test_func.c` in this directory computes a placeholder function
(a sum of squares plus `func_num * 100`), not the CEC2017 test functions. The library builds and the ctypes wiring
works, so the CEC2017 integration tests check the plumbing, not CEC2017 values. Do not report benchmark results from
this library as CEC2017 results until the real source is in place (see "Open decision" below).

## Building the Library

```bash
just build-cec2017
```

This compiles `cec17_test_func.c` with local gcc into `libcec2017.so` in this directory (`gcc -O2 -fPIC -shared ... -lm`).
It fails with a clear message if gcc is missing. The shared library is gitignored.

The former Docker builder (`docker-build-cec2017`, `Dockerfile`) was removed: it copied a sibling source tree
(`CEC2017-BoundConstrained/codes`) that is not in this repository, so it could not build.

## Integration with malta

The **ctypes binding** in `benchmarks/suites/cec2017.py` expects:

```
benchmarks/c_src/cec2017/
├── libcec2017.so          (compiled shared library, from `just build-cec2017`)
└── input_data/            (rotation/shift matrices; needed for the real CEC2017 functions)
```

## Open decision

The real CEC2017 C code is available outside this repository, in the local archive
(`~/projects/ARCHIVE/_third_party/CEC2017-BoundContrained/codes`). Vendoring it, and confirming its licence, is an
owner decision. Until then, `libcec2017.so` built here is the stub.

## Troubleshooting

**Error: "gcc: command not found"**
- Install a C compiler (for example `sudo apt install build-essential`), then run `just build-cec2017`.

**Library builds but results look wrong**
- Expected while the source is a stub: the function values are not CEC2017 values.
- After the real source is vendored, verify `input_data/` was copied (needed for rotations/shifts).

# CEC2017 Benchmark Library

The CEC2017 C++ source code is maintained in a **sibling forked repository** to keep malta clean:

- **Source:** `../CEC2017-BoundConstrained/` (forked from P-N-Suganthan/CEC2017-BoundConstrained)
- **Build:** Docker (reproducible, isolated)
- **Output:** `libcec2017.so` + `input_data/` (rotation/shift matrices)

## Building the Library

### Option 1: Docker (Recommended)
Reproducible build, locked gcc version, no local dependencies:

```bash
just docker-build-cec2017
```

This will:
1. Build `malta-cec2017:latest` Docker image
2. Compile CEC2017 source to `libcec2017.so`
3. Copy library + input data to `benchmarks/c_src/cec2017/`

### Option 2: Direct gcc (Legacy)
Requires local gcc + `cec17_test_func.c` in this directory:

```bash
just build-cec2017
```

## Integration with malta

The **ctypes binding** in `benchmarks/suites/cec2017.py` expects:

```
benchmarks/c_src/cec2017/
├── libcec2017.so          (compiled shared library)
└── input_data/            (rotation/shift matrices)
    ├── M_1_D10.txt
    ├── M_1_D30.txt
    └── ...
```

## Updating CEC2017

To incorporate upstream changes from P-N-Suganthan:

```bash
cd ../CEC2017-BoundConstrained
git fetch origin
git merge origin/master
cd -
just docker-build-cec2017
```

The Docker build will automatically pick up the new source.

## Why Docker?

- **Reproducibility:** gcc version locked, no system dependency drift
- **Isolation:** Build doesn't pollute local environment
- **Clarity:** Dockerfile documents the exact build process
- **Maintenance:** Keep malta repo focused; CEC2017 lives in sibling
- **Portability:** Same build runs on any machine with Docker

## Troubleshooting

**Error: "cannot find CEC2017-BoundConstrained"**
- Ensure you cloned the fork: `cd .. && git clone git@github.com:baseline0/CEC2017-BoundConstrained.git`
- Verify sibling directory exists: `ls ../CEC2017-BoundConstrained/codes`

**Error: "docker: command not found"**
- Install Docker: https://docs.docker.com/get-docker/
- Or use direct gcc build: `just build-cec2017`

**Library works but results seem wrong**
- Verify `input_data/` was copied (needed for rotations/shifts)
- Check file permissions: `ls -lh benchmarks/c_src/cec2017/libcec2017.so`

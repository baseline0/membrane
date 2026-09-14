# CEC2017 C Source

Place the CEC2017 benchmark source code here. The build expects:

```
benchmarks/c_src/cec2017/cec17_test_func.c
```

Download from: http://www.ntu.edu.sg/home/EPNSugan/index_files/CEC2017/

Once the C source is in place, run:

```bash
just build-cec2017
```

This will compile `libcec2017.so` used by `benchmarks/suites/cec2017.py`.

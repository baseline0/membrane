# CEC2017 C Source (Archive)

**Note:** As of Week 1 (commit d585bc6), malta uses [opfunu](https://github.com/thieu1995/opfunu) for CEC2017 benchmark functions. This directory is kept as reference for future custom C binding approaches.

The CEC2017 C source can be obtained from:
- Official: http://www.ntu.edu.sg/home/EPNSugan/index_files/CEC2017/
- GitHub: https://github.com/P-N-Suganthan/CEC2017-BoundConstrained

If you wish to build a custom `libcec2017.so` in the future, place `cec17_test_func.c` here and compile with:

```bash
gcc -shared -fPIC -O3 cec17_test_func.c -o libcec2017.so -lm
```

However, **opfunu is the recommended approach** — it eliminates the C compilation step entirely while maintaining numerical parity with the original CEC2017 suite.

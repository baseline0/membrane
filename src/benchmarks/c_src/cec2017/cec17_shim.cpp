// Fleet code, not upstream code. Used only by `just build-cec2017` with CEC2017_SRC set.
//
// Two things the upstream cec17_test_func.cpp needs that its driver main.cpp would normally provide:
// 1. Its global state (shift, rotation and permutation data, init flags), which it declares extern.
// 2. A C-linkage name for the ctypes loader. The build compiles upstream with -Dcec17_test_func=cec17_upstream_impl,
//    so the upstream function keeps its C++ linkage under that name, and this file exports cec17_test_func.
double *OShift, *M, *y, *z, *x_bound;
int ini_flag = 0, n_flag, func_flag, *SS;

void cec17_upstream_impl(double *x, double *f, int nx, int mx, int func_num);

extern "C" void cec17_test_func(double *x, double *f, int nx, int mx, int func_num) {
    cec17_upstream_impl(x, f, nx, mx, func_num);
}

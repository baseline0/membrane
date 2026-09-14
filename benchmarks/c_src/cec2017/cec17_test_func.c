/* CEC2017 stub: works for framework testing
 * Replace with real libcec2017.so once official source is fully compiled
 */

void cec17_test_func(double *x, double *f, int nx, int mx, int func_num) {
    int i, j;
    for (j = 0; j < mx; j++) {
        double sum = 0.0;
        for (i = 0; i < nx; i++) {
            double xi = x[j * nx + i];
            sum += xi * xi;
        }
        f[j] = sum + (double)(func_num * 100);
    }
}

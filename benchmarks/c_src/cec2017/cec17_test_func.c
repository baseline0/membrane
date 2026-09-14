/* Minimal CEC2017 stub for testing. Replace with official source. */

#include <math.h>
#include <string.h>

/* Placeholder: Official CEC2017 function evaluation.
 * Download from: http://www.ntu.edu.sg/home/EPNSugan/index_files/CEC2017/
 * Replace this file with cec17_test_func.c from official source.
 */

void cec17_test_func(double *x, double *f, int nx, int mx, int func_num) {
    int i, j;

    /* Stub implementation: return sum of squares shifted by function ID
     * This allows the framework to work before official C source is obtained.
     */

    for (j = 0; j < mx; j++) {
        double sum = 0.0;
        for (i = 0; i < nx; i++) {
            double xi = x[j * nx + i];
            sum += xi * xi;
        }
        /* Add function ID as offset (matches optimum = fid * 100) */
        f[j] = sum + (double)(func_num * 100);
    }
}

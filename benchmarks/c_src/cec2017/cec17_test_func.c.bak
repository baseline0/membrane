/* DEPRECATED: This is a minimal stub for testing only.
 *
 * The real CEC2017 library is now built via Docker from the forked repo:
 *   ../CEC2017-BoundConstrained/
 *
 * Build with: just docker-build-cec2017
 *
 * This stub remains for fallback/reference only.
 */

#include <math.h>
#include <string.h>

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

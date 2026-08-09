/* Babel: C — pairwise label agreement lift (dense loops). */
#include "collusion.h"

float collusion_chance(const int *a, const int *b, int n, int nlabels) {
    /* empirical pooled prior chance agreement */
    int *freq = (int*)calloc((size_t)nlabels, sizeof(int));
    if (!freq) return 0.f;
    for (int i = 0; i < n; i++) {
        if (a[i] >= 0 && a[i] < nlabels) freq[a[i]]++;
        if (b[i] >= 0 && b[i] < nlabels) freq[b[i]]++;
    }
    int total = 2 * n;
    float chance = 0.f;
    if (total > 0) {
        for (int i = 0; i < nlabels; i++) {
            float p = (float)freq[i] / (float)total;
            chance += p * p;
        }
    }
    free(freq);
    return chance;
}

int collusion_pair(const int *a, const int *b, int n, int nlabels, float margin,
                   float *agree_out, float *lift_out) {
    if (n <= 0) return 0;
    int agree = 0;
    for (int i = 0; i < n; i++) if (a[i] == b[i]) agree++;
    float agr = (float)agree / (float)n;
    float chance = collusion_chance(a, b, n, nlabels);
    float lift = agr - chance;
    if (agree_out) *agree_out = agr;
    if (lift_out) *lift_out = lift;
    return lift >= margin ? 1 : 0;
}

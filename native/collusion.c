/* Babel: C — pairwise label agreement lift (dense loops). */
#include "collusion.h"

float collusion_chance(const int *a, const int *b, int n, int nlabels) {
    /* Expected agreement under independent annotator-specific marginals. */
    if (!a || !b || n <= 0 || nlabels <= 0) return -1.f;
    int *freq_a = (int*)calloc((size_t)nlabels, sizeof(int));
    int *freq_b = (int*)calloc((size_t)nlabels, sizeof(int));
    if (!freq_a || !freq_b) {
        free(freq_a);
        free(freq_b);
        return -1.f;
    }
    for (int i = 0; i < n; i++) {
        if (a[i] < 0 || a[i] >= nlabels || b[i] < 0 || b[i] >= nlabels) {
            free(freq_a);
            free(freq_b);
            return -1.f;
        }
        freq_a[a[i]]++;
        freq_b[b[i]]++;
    }
    float chance = 0.f;
    for (int i = 0; i < nlabels; i++) {
        float pa = (float)freq_a[i] / (float)n;
        float pb = (float)freq_b[i] / (float)n;
        chance += pa * pb;
    }
    free(freq_a);
    free(freq_b);
    return chance;
}

int collusion_pair(const int *a, const int *b, int n, int nlabels, float margin,
                   float *agree_out, float *lift_out) {
    if (!a || !b || n <= 0 || nlabels <= 0 || margin < 0.f || margin > 1.f) return -1;
    float chance = collusion_chance(a, b, n, nlabels);
    if (chance < 0.f) return -1;
    int agree = 0;
    for (int i = 0; i < n; i++) if (a[i] == b[i]) agree++;
    float agreement = (float)agree / (float)n;
    float lift = agreement - chance;
    if (agree_out) *agree_out = agreement;
    if (lift_out) *lift_out = lift;
    return lift >= margin ? 1 : 0;
}

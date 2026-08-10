#include "collusion.h"
#include "collusion.c"
#include <math.h>
#include <stdio.h>

int main(void) {
    int a[30], b[30];
    for (int i = 0; i < 30; i++) { a[i] = i % 2; b[i] = i % 2; }
    float agreement, lift;
    int flagged = collusion_pair(a, b, 30, 2, 0.2f, &agreement, &lift);
    if (flagged != 1 || agreement < 0.99f) {
        printf("identical: %d %f %f\n", flagged, agreement, lift);
        return 1;
    }

    /* A is always label 0; B is half 0, half 1. Independent-marginal
       expected agreement is exactly 0.5 (the old pooled baseline was 0.625). */
    int c[10], d[10];
    for (int i = 0; i < 10; i++) { c[i] = 0; d[i] = i < 5 ? 0 : 1; }
    float chance = collusion_chance(c, d, 10, 2);
    if (fabsf(chance - 0.5f) > 0.0001f) {
        printf("chance=%f\n", chance);
        return 2;
    }

    int invalid[2] = {0, 3};
    if (collusion_pair(invalid, invalid, 2, 2, 0.2f, NULL, NULL) != -1) {
        printf("invalid label did not refuse\n");
        return 3;
    }
    if (collusion_pair(c, d, 10, 2, -0.1f, NULL, NULL) != -1) {
        printf("invalid margin did not refuse\n");
        return 4;
    }

    printf("ok\n");
    return 0;
}

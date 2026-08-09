#ifndef COLLUSION_H
#define COLLUSION_H
#include <stdlib.h>
float collusion_chance(const int *a, const int *b, int n, int nlabels);
int collusion_pair(const int *a, const int *b, int n, int nlabels, float margin,
                   float *agree_out, float *lift_out);
#endif

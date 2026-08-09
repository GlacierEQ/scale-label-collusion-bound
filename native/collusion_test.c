#include "collusion.h"
#include "collusion.c"
#include <stdio.h>
int main(void) {
    int a[30], b[30];
    for (int i=0;i<30;i++) { a[i]=i%2; b[i]=i%2; }
    float agr, lift;
    int flagged = collusion_pair(a,b,30,2,0.2f,&agr,&lift);
    if (!flagged || agr < 0.99f) { printf("%d %f %f\n", flagged, agr, lift); return 1; }
    printf("ok\n");
    return 0;
}

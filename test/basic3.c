#include "stdio.h"
int main()
{
    double i,j;
    j=2.3;
    scanf("%lf",&i);
    i=i*j+i*(i*j-i*j)/j;
    printf("%lf\n",i);

    return 0;
}
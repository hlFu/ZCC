#include "stdio.h"
int main()
{
    int i,j;
    j=5;
    scanf("%lf",&i);
    i=i*j+i*(i*j-i*j)/j;
    printf("%lf\n",i);

    return 0;
}

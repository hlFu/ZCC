#include "stdio.h"
int main()
{
    int i,j;
    j=5;
    scanf("%d",&i);
    i=i*j+i*(i*j-j*j+i);
    printf("%d\n",i);

    return 0;
}

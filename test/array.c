/*
 * multi-dimension array
 */
#include "stdio.h"
int main(void)
{
    int a[5][5];
    int i,j;
    for(i=0;i<5;++i)
    {
        printf("%d\n",i);
        for (j=0;j<5;++j)
        {
            a[i][j]=i*5+j;
            printf("%02d ",a[i][j]);
        }
        puts("");
    }
    return 0;
}


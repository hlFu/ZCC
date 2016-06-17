#include "stdio.h"
int fib(int n);
int i;
int main()
{
    scanf("%d",&i);
    printf("%d\n",fib(i));

    return 0;
}
int fib(int n)
{
    int i;
    if(n>1)
    {
        return fib(n-1)+fib(n-2);
    }
    else if(n==1)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}

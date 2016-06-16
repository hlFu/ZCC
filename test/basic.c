/*
basic expression:for if while
basic type: int float double char pointer
glibc:scanf printf
constant: string char float
scope: local, global, static local, compound_statement
arithmetic operation; logical operation
priority
declaration definition
array
increment
preprocessing
*/
#include "stdio.h"
#define UPPERCASE_A 'A'
#define LOWERCASE_A 'a'
#define LOWERCASE_Z 'z'
int fib(int n);
int n,i;
int main(int argc,char **argv)
{
    double d,f;
    char *s;                   

    s=argv[1];
    while(*s!=0)
    {
        if(*s<=LOWERCASE_Z&&*s>=LOWERCASE_A)
            *s=*s+UPPERCASE_A-LOWERCASE_A;
        ++s;
    }    
    printf("%s\n",argv[1]);

    scanf("%d",&n);
    printf("%d\n",fib(n));

    f=0.5;
    d=1.5;

    for(i=0;i<n;++i)
    {
        int a;
        a=3;
        f=(f+d*i)/a;
    }
    printf("f=%f\n",f);


    return 0;
}

int fib(int n)
{
    //static count=0;
    //count++;
    //printf("count=%d\n",count);
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

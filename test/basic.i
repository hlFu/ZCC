# 1 "basic.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "basic.c"
# 14 "basic.c"
# 1 "stdio.h" 1


int printf(char *format,...);
int scanf(char *format,...);
int puts(char* s);
# 15 "basic.c" 2



int fib(int n);
int n,i;
int main(int argc,char **argv)
{
    float f;
    double d;
    char *s;

    s=argv[1];
    while(*s!=0)
    {
        if(*s<='z'&&*s>='a')
            *s=*s+'A'-'a';
        s++;
    }
    printf("%s\n",argv[1]);

    scanf("%d",&n);
    printf("%d\n",fib(n));

    f=0.5;
    d=1.5;

    for(i=0;i<n;i++)
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

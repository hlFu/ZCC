/*
 * embedded struct
 * member access: direct pointer
 */
#include "stdio.h"
typedef struct
{
    int a;
    char c;
    struct {
        int b;
        double d;
    }inner;
}myStruct;

void printStruct(myStruct* s)
{
    printf("s.a=%d\ns.c=%c\ns.inner.b=%d\ns.inner.d=%lf\n",s->a,s->c,s->inner.b,s->inner.d);
}

int main(void)
{
    myStruct s;
    s.a=2;
    s.c='a';
    s.inner.b=3;
    s.inner.d=12.3;
    printStruct(&s);

    return 0;
}

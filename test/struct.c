/*
 * embedded struct
 * member access: direct pointer
 * typedef
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

void modifyStruct(myStruct* sp)
{
    sp->a=4;
    sp->c='!';
    sp->inner.b=5;
    sp->inner.d=55.2;
    return;
}

int main(void)
{
    myStruct p;
    myStruct *sp;

    sp=&p;
    p.a=2;
    p.c='a';
    p.inner.b=3;
    p.inner.d=12.3;
    printf("before modified\n");
    printf("p.a=%d\tp.c=%c\tp.inner.b=%d\tp.inner.d=%lf\n",p.a,p.c,p.inner.b,p.inner.d);
    modifyStruct(&p);
    printf("after modified\n");
    printf("p.a=%d\tp.c=%c\tp.inner.b=%d\tp.inner.d=%lf\n",p.a,p.c,p.inner.b,p.inner.d);

    return 0;
}


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
    myStruct p[3];
    myStruct *sp;

    sp=&p[1];
    p[1].a=2;
    p[1].c='a';
    p[1].inner.b=3;
    p[1].inner.d=12.3;
    printf("before modified\n");
    printf("p[1].a=%d\tp[1].c=%c\tp[1].inner.b=%d\tp[1].inner.d=%lf\n",p[1].a,p[1].c,p[1].inner.b,p[1].inner.d);
    modifyStruct(sp);
    printf("after modified\n");
    printf("p[1].a=%d\tp[1].c=%c\tp[1].inner.b=%d\tp[1].inner.d=%lf\n",p[1].a,p[1].c,p[1].inner.b,p[1].inner.d);

    return 0;
}


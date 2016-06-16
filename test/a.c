
int printf(char *s,...);
int foo()
{
    printf("hello\n");

    return 2;
}

int main(void)
{
    double a;
    a=1.2;
//    i=foo();
    printf("%lf\n",a);

    return 0;
}



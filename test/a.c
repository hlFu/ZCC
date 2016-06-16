
int printf(char *s,...);
int foo()
{
    printf("hello\n");

    return 2;
}

int main(void)
{
    int i;
//    i=foo();
    for(i=0;i<4;++i)
    printf("hello\n");

    return 0;
}



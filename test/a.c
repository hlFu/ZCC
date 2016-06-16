
int printf(char *s,...);
int foo()
{
    printf("hello\n");

    return 2;
}

int main(void)
{
    int i[2][2];
    i[1][1]=2;
//    i=foo();
   printf("%d\n",i[1][1]);

    return 0;
}



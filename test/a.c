struct A{
    int a;
    int b;
}a;


int printf(char *s, int i);
int main(void)
{
    int i;

    a.b=2;
    for(i=0;i<4;i=i+1)
    {
        printf("%d\n",a.b);
    }

    return 0;
}


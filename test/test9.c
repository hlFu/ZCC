double a;
struct test{
    char a;
    int b;
    short c;
    double e;
};
int foo(char a, int b, short c, struct test d, char *s){
    d.e=10.5;
    d.c=2;
    if(a=='a')
        return b-c;
    else
        return d.e-d.c;
}

int main(){
    struct test t;
    a=4.5;
    t.a='b';
    t.b=2;
    t.c=3;
    t.e=5.4;
    printf("%lf",t.e);
    return foo('a',10,2,t,"mamsf");
}

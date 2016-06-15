int g_i;
static int ss;
static int sss;

int foo(int n){
    static int x3;
    int x1,x2;
    x1=2;
    x2=3;
    x1=x1+1;
    return n+1;
}


int main(void){
    int l_i,x1,x2,x3;
    l_i=l_i+1;
    x1=1;
    x1=x1+l_i;
    x2=foo(x1);
    return 1;
}
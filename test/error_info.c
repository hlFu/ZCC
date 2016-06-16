
//函数定义声明不一致
int f(int i,...);
int f(int j){
    return 0;
}

int g(int i){
    return 0;
}
typedef struct{
    int n;
} A;
int main(int argc, char const *argv[])
{

    //重复定义
    int k;
    int k;
    //缺少分号
    int i
    int count;
    //类型不匹配
    A a;
    a = 5;
    //未定义变量
    var = 3;
    //操作数类型错误
    1.0 >> 4;
    //打字错误
    cont = 4;
    g(1.0);
    //参数表不匹配
    g(a);
    //返回值不匹配
    return a;
}
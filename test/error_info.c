
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

// Semantic Error at line 4:  'int function(int j,)' is not consistent with old declaration 'int function(int i,...)'
//     int f ( int j ) { return 0 ; }
//
// Syntax error at 'int', at line: 22, column: 5.
// Error type: missing semicolon before int. at line: 22, lex pos: 258 in declaration.
//
// Semantic Error at line 18:  Redeclare k
//     k
//
// Semantic Error at line 23:  'int const' cannot be assigned to 'struct {'n': int}'
//     a = 5
//
// Semantic Error at line 25:  Unknown identifier var
//     var
//
// Semantic Error at line 27:  double const is not or cannot be recognized as integer
//     1.0
//
// Semantic Error at line 29:  Unknown identifier 'cont', do you mean 'count'?
//     cont
//
// Semantic Error at line 32:  'struct {'n': int}' can't convert to 'int'
//     a
//
// Semantic Error at line 34:  'struct {'n': int}' is not consistant with the function return type 'int'
//     return a ;

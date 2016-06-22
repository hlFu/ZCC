int main(int argc, char const *argv[])
{
    int c;
    int flag;
    c = 2 + 3 * 4;//常量压缩
    if ((2 - 2)*9){
        //这个if语句经过常量压缩，死代码消除后，会被剪掉
    }

    if (1){
        c = 2;
        //这个复合语句会替换掉if语句
    }
    else{
        c = 3;
        //这个复合语句会被剪掉
    }

    if(flag){
        return 0;
        c = c + 1;  //return后的语句被删除
    }
    return 0;
}
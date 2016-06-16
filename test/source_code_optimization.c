int main(int argc, char const *argv[])
{
    int c;
    c = 2 + 3 * 4;//常量压缩
    if ((2 - 2)*9)
    {

    }

    if (1)
    {
        //这个复合语句会替换掉if语句
    }
    else{
        //这个复合语句不会出现在代码中
    }
    return 0;

    //这个也会被删除
    c = c + 1;
}
# ZCC
ZJU standard C Compiler

##免责声明
我看大家都没动手，为了美好的明天，必须出来打个底
如果大家觉得定的有什么不对的地方，欢迎修改！！！

##项目分布
请将：  
    lex和yac放在yyparse文件夹  
    symbol table和类型检查放在symbol  
    机器码生成放在generation  
    全局变量放在public  
    优化代码放在各自部分的文件夹下  

##命名规则
为了不出现引用错误，简单的定一下规则，（再次声明觉得不科学的一定要提出来） 
###类名
每个单词的首字母大写
###变量和函数名
从第二个单词开始首字母大写，如treeNode
###常量
全部大写

##合作
1.请务必在需要交互的所有类和函数上面写上注释，必要的话可以写上重要函数的注释  
2.请把你觉得可重用的函数写到public文件夹  
3.因为耦合不是很多，大家基本不会再一个文件里编写，所以不开分支也行，但是push之前一定保证能跑起来  

##关于tree结构和BNF
  实话说，我看了一下总结出：没开始写就想定树结构，简直就是在搞笑，所以我仿照tiny语言擅自定了一个，在编写过程中人人都可以修改，但一定要写注释
那个BNF也是同样的，要出来商量BNF，效率太低，加上我们吹牛的时间，必定雪崩，于是我找了一个，大家每个人都要看一遍，具体为什么其麦学长那天也说了，然可能的话看的过程写下注释，这样后面的人更好理解，也可以揪出你理解的错误，然后发现问题或者要修改请立即提出

##关于wiki
请大家踊跃地写wiki，这是为了整组的效率，比如做过js解释器的李某其麦学长，如果有什么让大家能快速上手py parse的资料，请把链接写到wiki

##遥远的祝福
祝大家大程满分，如果可以的话，希望能在下个星期日之前完成v1.0

## 目前语法分析的能力
对于正确的程序，语法分析，符号表建立，都完成了。
文档写的不多，我会给你熊学长和付学长系统的讲一遍，之后你们有疑问直接问我这个活文档
到时候，我看哪里需要写一下，我再写。
现在不支持
1. enum
2. 定义初始化,如 int i = 3;
3. 常量表达式,如 int i[2*3];
4. 语法检查也比较弱，没有检查运算的操作数的类型合法性。
5. 一些其它的特性也没有。只要你用了不支持的特性，都会报错提醒你。
6. size的维护问题。
目前已经够你们后端写起来了。
你们一定要保证测试样例是正确的，因为我只进行了部分的语法检查。
你们的样例都要先用gcc测一遍正确性，再来跑我们的zcc。
其它的特性，等我把别的作业写一写，再来加。


##Problems
* 错误处理

* typedef 的语法树可能有点问题

* 李学长：根据标准typedef就是这个样子，不过需要我这里在进行一些检查，你们对这个typedef的语法树有疑问来问我。

typedef struct{
    int a;
    double c;
}mytype;

语法树：

```
declaration
    declaration_specifiers
        storage_class_specifier
            typedef
        declaration_specifiers
            type_specifier
                struct_or_union_specifier
                    struct_or_union
                        struct
                    {
                    struct_declaration_list
                        struct_declaration_list
                            struct_declaration
                                specifier_qualifier_list
                                    type_specifier
                                        int
                                struct_declarator_list
                                    struct_declarator
                                        declarator
                                            direct_declarator
                                                a
                                ;
                        struct_declaration
                            specifier_qualifier_list
                                type_specifier
                                    double
                            struct_declarator_list
                                struct_declarator
                                    declarator
                                        direct_declarator
                                            c
                            ;
                    }
    init_declarator_list
        init_declarator
            declarator
                direct_declarator
                    mytype
    ;
```    
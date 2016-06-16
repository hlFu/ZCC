#include "stdio.h"

int main(int argc,char **argv)
{
    char *s;
    s=*argv;

    while(*s!=0)
    {
        if(*s>='a'&&*s<='z')
            *s=*s+(65-97);
        ++s;
    }

    printf("%s",*argv);
    puts("");

    return 0;
}



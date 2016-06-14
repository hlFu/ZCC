#include<stdio.h>
int g_fast;
static int s_g_fast;

int main(void)
{
    int l_fast;
    static int  s_l_fast;
    l_fast=1;
    s_l_fast=2;
    l_fast=foo(s_l_fast);
    printf("%d\n",l_fast);
    return 0;
                }

int foo(int n){
   return n+1; 
}

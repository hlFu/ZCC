/*
 * embedded functional pointer
 */
#include "stdio.h"
int i;

void print_int(){
    printf("%d\n", i);
    return;
}

void (*high_order_func(int n)) (){
    i = n;
    return print_int;
}

int main(){
    void (*(*f)(int n))();
    f = high_order_func;
    f(2)();
    return 0;
}

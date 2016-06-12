#!/usr/bin/python
from yyparse.ZCCparser import parser, printAST
from yyparse.ZCClex import lexer as ZCClexer
from symbol.symtab import c_types
from public.ZCCglobal import global_context, FuncType, error
from generation.generation import generator

if __name__ == '__main__':
    # with open("yyparse/missSEMI.c") as f:
    # with open("yyparse/missRightCurly.c") as f:
    # with open("symbol/test.c") as f:
    # with open("symbol/preprocessed.c") as f:
    with open("test/test9.c") as f:
        # with open("test/test1.c") as f:
        codes = f.read()
        pt = parser.parse(codes, lexer=ZCClexer)
        print "errorCounter=", parser.errorCounter
        printAST(pt)
        # with open("test.s","w") as output:
    print global_context
    print error
    # printAST(global_context.local['main'].compound_statement.ast)
    # gen=generator()
    # gen.generate()
    # gen.output('test/out.txt')

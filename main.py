#!/usr/bin/python
from yyparse.ZCCparser import parser, printAST
from yyparse.ZCClex import lexer as ZCClexer
from symbol.symtab import c_types
from public.ZCCglobal import global_context, FuncType, error, Context
from generation.generation import generator
import os


def preprocess(source):
    stream = os.popen("gcc -E " + source)
    return stream.read()


if __name__ == '__main__':
    codes = preprocess(os.path.abspath("test/pointer.c"))
    pt = parser.parse(codes, lexer=ZCClexer)
    # print "errorCounter=", parser.errorCounter
    printAST(pt)
    # with open("test.s","w") as output:
    print global_context
    # print error
    # printAST(global_context.local['main'].compound_statement.ast)
    gen = generator()
    gen.generate()
    gen.output('test/out.s')

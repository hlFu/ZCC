#!/usr/bin/python
from yyparse.ZCCparser import parser, printAST
from yyparse.ZCClex import lexer as ZCClexer
from symbol.symtab import c_types
from public.ZCCglobal import global_context, FuncType, error, Context
from generation.generation import generator
import os
import sys


def preprocess(source):
    stream = os.popen("gcc -E " + source)
    return stream.read()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python main.py <source_file> <x86asm_file>\nEnvironment: Python2.7, Linux."
        exit(1)
    File = sys.argv[1]
    codes = preprocess(os.path.abspath("test/"+File))
    pt = parser.parse(codes, lexer=ZCClexer)
    # print "errorCounter=", parser.errorCounter
    printAST(pt)
    # with open("test.s","w") as output:
    # print global_context
    # print error
    # printAST(global_context.local['main'].compound_statement.ast)
    if(not error[0]):
        gen = generator()
        gen.generate()
        gen.output(sys.argv[2])

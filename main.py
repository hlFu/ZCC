#!/usr/bin/python
from yyparse.ZCCparser import parser, printAST
from yyparse.ZCClex import lexer as ZCClexer

if __name__ == '__main__':
    # with open("symbol/test.c") as f:
    with open("symbol/preprocessed.c") as f:

        codes = f.read()
        pt = parser.parse(codes, lexer=ZCClexer)
        print "errorCounter=", parser.errorCounter
        printAST(pt)

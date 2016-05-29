#!/usr/bin/python

import ply.lex as lex
import ply.yacc as yacc
from pprint import pprint

lexErrorInfo = []
#column = 0

# Compute column. 
#     input is the input text string
#     token is a token instance
def find_column(input, token):
	last_cr = input.rfind('\n',0,token.lexpos)
	if last_cr < 0:
		last_cr = 0
	column = token.lexpos - last_cr
#	print "lexpos: ", token.lexpos, " last_cr: ", last_cr

	return column
	
	
reserved = {
	"auto"			:'AUTO',
	"break"		 	:'BREAK',
	"case"		 	:'CASE',
	"char"		 	:'CHAR',
	"const"			:'CONST',
	"continue"		:'CONTINUE',
	"default"		:'DEFAULT',
	"do" 			:'DO',
	"double"		:'DOUBLE',
	"else"		    :'ELSE',
	"enum"		 	:'ENUM',
	"extern"		:'EXTERN',
	"float"			:'FLOAT',
	"for"	 		:'FOR',
	"goto"		 	:'GOTO',
	"if" 			:'IF',
	"int"	 		:'INT',
	"long"		 	:'LONG',
	"register"		:'REGISTER',
	"return"		:'RETURN',
	"short"			:'SHORT',
	"signed"		:'SIGNED',
	"sizeof"		:'SIZEOF',
	"static"		:'STATIC',
	"struct"		:'STRUCT',
	"switch"		:'SWITCH',
	"typedef"		:'TYPEDEF',
	"union"			:'UNION',
	"unsigned"		:'UNSIGNED',
	"void"		 	:'VOID',
	"volatile"		:'VOLATILE',
	"while"			:'WHILE',
}

operator = {
	
}

	
tokens = (
	'AUTO',
	'BREAK',
	'CASE',
	'CHAR',
	'CONST',
	'CONTINUE',
	'DEFAULT',
	'DO',
	'DOUBLE',
	'ELSE',
	'ENUM',
	'EXTERN',
	'FLOAT',
	'FOR',
	'GOTO',
	'IF',
	'INT',
	'LONG',
	'REGISTER',
	'RETURN',
	'SHORT',
	'SIGNED',
	'SIZEOF',
	'STATIC',
	'STRUCT',
	'SWITCH',
	'TYPEDEF',
	'UNION',
	'UNSIGNED',
	'VOID',
	'VOLATILE',
	'WHILE',
	"IDENTIFIER", "CONSTANT", "STRING_LITERAL",
	"ELLIPSIS", 
	"RIGHT_ASSIGN", 
	"LEFT_ASSIGN", 
	"ADD_ASSIGN",
	"SUB_ASSIGN",
	"MUL_ASSIGN",
	"DIV_ASSIGN",
	"MOD_ASSIGN",
	"AND_ASSIGN",
	"XOR_ASSIGN",
	"OR_ASSIGN",
	"RIGHT_OP",
	"LEFT_OP",
	"INC_OP",
	"DEC_OP",
	"PTR_OP",
	"AND_OP",
	"OR_OP",
	"LE_OP",
	"GE_OP",
	"EQ_OP",
	"NE_OP"

)

def t_STRING_LITERAL(t):
	r'\"(\\.|[^\\\"])*\"'
	return t
	
def t_ignore_COMMENT(t):
	r'(/\*(.|\n)*?\*/)|(//.*)'
	t.lexer.lineno += t.value.count('\n')
	pass
	
def t_IDENTIFIER(t):
	r"[_A-Za-z][_A-Za-z0-9]*"
	t.type = reserved.get(t.value, 'IDENTIFIER')
	return t

def t_CONSTANT(t):
	r'[0-9]+[Ee][+-]?[0-9]+[fFlL]?|[0-9]*\.[0-9]+([Ee][+-]?[0-9]+)?[fFlL]?|[0-9]+\.[0-9]*([Ee][+-]?[0-9]+)?[fFlL]?|0[xX][a-fA-F0-9]+(u|U)?(l|L){0,2}|((0|[1-9][0-9]*)(u|U)?(l|L){0,2})|\'(\S|\\([abfnrtv\\\'\"0]|[0-7]{3}|x[0-9a-fA-F]{2}))\''
#	r'0[xX][a-fA-F0-9]+(u|U)?(l|L){1,2}|'
#	r'0[0-9]+(u|U)?(l|L){1,2}|'
#	r'[0-9]+(u|U)?(l|L){1,2}|'
#	r'\'\S|\\([abfnrtv\\\'\"0]|[0-7]{3}|x[0-9a-fA-F]{2})\'|'
#	r'[0-9]+[Ee][+-]?[0-9]+[fFlL]?|'
#	r'[0-9]*\.[0-9]+([Ee][+-]?[0-9]+)?[fFlL]?|'
#	r'[0-9]+\.[0-9]*([Ee][+-]?[0-9]+)?[fFlL]?'
	return t



t_ELLIPSIS = r"\.\.\."
t_RIGHT_ASSIGN = r">>="
t_LEFT_ASSIGN = r"<<="
t_ADD_ASSIGN = r"\+="
t_MUL_ASSIGN = r"\*="
t_DIV_ASSIGN = r"/="
t_MOD_ASSIGN = r"%="
t_AND_ASSIGN = r"&="
t_XOR_ASSIGN = r"^="
t_OR_ASSIGN = r"\|="
t_RIGHT_OP = r">>"
t_LEFT_OP = r"<<"
t_INC_OP = r"\+\+"
t_DEC_OP = r"--"
t_PTR_OP = r"->"
t_AND_OP = r"&&"
t_OR_OP = r"\|\|"
t_LE_OP = r"<="
t_GE_OP = r">="
t_EQ_OP = r"=="
t_NE_OP = r"!="

literals = '()[]{};.,&*+-~!/%<>^|?:='


# Define a rule so we can track line numbers
def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
	

t_ignore  = ' \t'
	
def t_error(t):
	error_column = find_column(t.lexer.lexdata, t)
	print("Unknown text '%s' at line: %d, column: %d" % (t.value, t.lexer.lineno, error_column))
	lexErrorInfo.append({
		'pos':t.lexer.lexpos, 
		'lineno':t.lexer.lineno, 
		'column':error_column,
		'value': t.value
	})
	t.lexer.skip(1)
	

lexer = lex.lex()
#pprint(lexer.__dict__) 

def test_lex():
#data = raw_input()

#	c_file_name = raw_input('c file name: ')
	c_file_name = "test1.c"
	c_file = open(c_file_name, "r")
	contents = "".join(c_file.readlines())


	lexer.input(contents)

	while True:
		tok = lexer.token()
		if not tok:
			break
		print tok.value, find_column(lexer.lexdata, tok)

#test_lex()
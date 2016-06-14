#!/usr/bin/python

import ply.lex as lex
# import ply.yacc as yacc
# from pprint import pprint
from symbol.symtab import is_type
from public.ZCCglobal import TreeNode
lexErrorInfo = []


# column = 0

# Compute column. 
#     input is the input text string
#     token is a token instance
def find_column(input, token):
    last_cr = input.rfind('\n', 0, token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = token.lexpos - last_cr
    #	print "lexpos: ", token.lexpos, " last_cr: ", last_cr
    return column


reserved_dict = {
    #	"auto"			:'AUTO',
    "break": 'BREAK',
    "case": 'CASE',
    "char": 'CHAR',
    "const": 'CONST',
    "continue": 'CONTINUE',
    "default": 'DEFAULT',
    "do": 'DO',
    "double": 'DOUBLE',
    "else": 'ELSE',
    "enum": 'ENUM',
    "extern": 'EXTERN',
    "float": 'FLOAT',
    "for": 'FOR',
    #	"goto"		 	:'GOTO',
    "if": 'IF',
    "int": 'INT',
    "long": 'LONG',
    #	"register"		:'REGISTER',
    "return": 'RETURN',
    "short": 'SHORT',
    "signed": 'SIGNED',
    "sizeof": 'SIZEOF',
    "static": 'STATIC',
    "struct": 'STRUCT',
    "switch": 'SWITCH',
    "typedef": 'TYPEDEF',
    "union": 'UNION',
    "unsigned": 'UNSIGNED',
    "void": 'VOID',
    # "volatile": 'VOLATILE',
    "while": 'WHILE',
}

literal_dict = {
    '(': 'LBRACKET',
    ')': 'RBRACKET',
    '[': 'LSQUAREBRACKET',
    ']': 'RSQUAREBRACKET',
    '{': 'LCURLYBRACKET',
    '}': 'RCURLYBRACKET',
    ';': 'SEMICOLON',
    '.': 'PERIOD',
    ',': 'COMMA',
    '&': 'AND',
    '*': 'STAR',
    '+': 'PLUS',
    '-': 'MINUS',
    '~': 'UNOT',
    '!': 'NOT',
    '/': 'DIVIDE',
    '%': 'MOD',
    '<': 'LT',
    '>': 'GT',
    '^': 'XOR',
    '|': 'OR',
    '?': 'QUESTIONMARK',
    ':': 'COLON',
    '=': 'ASSIGN'
}

tokens = (
    # 'AUTO',
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
    # 'GOTO',
    'IF',
    'INT',
    'LONG',
    # 'REGISTER',
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
    #	'VOLATILE',
    'WHILE',
    "IDENTIFIER",
    "TYPE_NAME",
    "STRING_LITERAL",
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
    "NE_OP",
    'LBRACKET',
    'RBRACKET',
    'LSQUAREBRACKET',
    'RSQUAREBRACKET',
    'LCURLYBRACKET',
    'RCURLYBRACKET',
    'SEMICOLON',
    'PERIOD',
    'COMMA',
    'AND',
    'STAR',
    'PLUS',
    'MINUS',
    'UNOT',
    'NOT',
    'DIVIDE',
    'MOD',
    'LT',
    'GT',
    'XOR',
    'OR',
    'QUESTIONMARK',
    'COLON',
    'ASSIGN',
    "ERRORID",
    "NUMBER_CONSTANT",
    "CHARACTER_CONSTANT",
    "EOF"
)


def t_STRING_LITERAL(t):
    r'\"(\\.|[^\\\"])*\"'
    value = t.value
    t.value = TreeNode()
    t.value.lineno = t.lexer.lineno
    t.value.append('STRING')
    t.value.append(value)
    return t


def t_ignore_COMMENT(t):
    r'(/\*(.|\n)*?\*/)|(//.*)|(^\#.*)|(\n\#.*)|(\r\n\#.*)'
    t.lexer.lineno += t.value.count('\n')
    pass


def t_IDENTIFIER(t):
    r"""[_A-Za-z][_A-Za-z0-9]*"""
    t.type = reserved_dict.get(t.value, 'IDENTIFIER')
    if t.type == 'IDENTIFIER' and is_type(t.value):
        t.type = "TYPE_NAME"
    if t.type == 'IDENTIFIER':
        value = t.value
        t.value = TreeNode()
        t.value.lineno = t.lexer.lineno
        t.value.append('IDENTIFIER')
        t.value.append(value)
    return t


def t_NUMBER_CONSTANT(t):
    r"""([0-9]*\.[0-9]+|[0-9]+\.)([eE][+\-]?[0-9]+)?[flFL]?|[0-9]+([eE][+\-]?[0-9]+)[flFL]?|[1-9][0-9]*[uU]?[lL]{,2}|0[0-7]*[uU]?[lL]{,2}|0[xX][0-9a-fA-F]+[uU]?[lL]{,2}"""
    val = eval(t.value)
    if isinstance(val, float):
        value = t.value
        t.value = TreeNode()
        t.value.lineno = t.lexer.lineno
        t.value.append('DOUBLE')
        t.value.append(value)
    else:
        value = t.value
        t.value = TreeNode()
        t.value.lineno = t.lexer.lineno
        t.value.append('INTEGER')
        t.value.append(value)
    return t


def t_CHARACTER_CONSTANT(t):
    r"\'([^\'\\\n]|(\\[\'\"?\\abfnrtv]|[0-7]{1,3}|x[0-9a-fA-F]{1,2}))\'"
    value = t.value
    t.value = TreeNode()
    t.value.lineno = t.lexer.lineno
    t.value.append('INTEGER')
    t.value.append(str(ord(eval(value))))
    return t


# def t_CONSTANT(t):
# 	r'[1-9][0-9]*[Ee][+-]?[1-9][0-9]*[fFlL]?|[0-9]*\.[0-9]+([Ee][+-]?[0-9]+)?[fFlL]?|[0-9]+\.[0-9]*([Ee][+-]?[0-9]+)?[fFlL]?|0[xX][a-fA-F0-9]+(u|U)?(l|L){,2}|((0|[1-9][0-9]*)(u|U)?(l|L){,2})|\'(\S|\\([abfnrtv\\\'\"0]|[0-7]{3}|x[0-9a-fA-F]{2}))\''
# #	r'0[xX][a-fA-F0-9]+(u|U)?(l|L){1,2}|'
# #	r'0[0-9]+(u|U)?(l|L){1,2}|'
# #	r'[0-9]+(u|U)?(l|L){1,2}|'
# #	r'\'\S|\\([abfnrtv\\\'\"0]|[0-7]{3}|x[0-9a-fA-F]{2})\'|'
# #	r'[0-9]+[Ee][+-]?[0-9]+[fFlL]?|'
# #	r'[0-9]*\.[0-9]+([Ee][+-]?[0-9]+)?[fFlL]?|'
# #	r'[0-9]+\.[0-9]*([Ee][+-]?[0-9]+)?[fFlL]?'
#
# 	return t



def t_ELLIPSIS(t):
    r"\.\.\."
    return t


def t_RIGHT_ASSIGN(t):
    r">>="
    return t


def t_LEFT_ASSIGN(t):
    r"<<="
    return t


def t_ADD_ASSIGN(t):
    r"\+="
    return t


def t_MUL_ASSIGN(t):
    r"\*="
    return t


def t_DIV_ASSIGN(t):
    r"/="
    return t


def t_MOD_ASSIGN(t):
    r"%="
    return t


def t_AND_ASSIGN(t):
    r"&="
    return t


def t_XOR_ASSIGN(t):
    r"^="
    return t


def t_OR_ASSIGN(t):
    r"\|="
    return t


def t_RIGHT_OP(t):
    r">>"
    return t


def t_LEFT_OP(t):
    r"<<"
    return t


def t_INC_OP(t):
    r"\+\+"
    return t


def t_DEC_OP(t):
    r"--"
    return t


def t_PTR_OP(t):
    r"->"
    return t


def t_AND_OP(t):
    r"&&"
    return t


def t_OR_OP(t):
    r"\|\|"
    return t


def t_LE_OP(t):
    r"<="
    return t


def t_GE_OP(t):
    r">="
    return t


def t_EQ_OP(t):
    r"=="
    return t


def t_NE_OP(t):
    r"!="
    return t


def t_LITERAL(t):
    r"[()\[\]{};.,&*+\-~!/%<>\^|?:=]"
    t.type = literal_dict.get(t.value)
    if t.value == '{':
        t.lexer.curlyBalance += 1
    elif t.value == '}':
        t.lexer.curlyBalance -= 1
    return t


# literals = '()[]{};.,&*+-~!/%<>^|?:='

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n'
    t.lexer.lineno += 1 # len(t.value)


t_ignore = ' \t'


def t_ERRORID(t):
    r"[^\s;}]+"
    t.value = (t.value, "ERRORID")
    return t


def t_error(t):
    error_column = find_column(t.lexer.lexdata, t)
    print("Unknown text '%s' at line: %d, column: %d" % (t.value, t.lexer.lineno, error_column))
    lexErrorInfo.append({
        'pos': t.lexer.lexpos,
        'lineno': t.lexer.lineno,
        'column': error_column,
        'value': t.value
    })
    t.lexer.skip(1)


orig_lexer = lex.lex()


# pprint(lexer.__dict__)

class ProxyLexer(object):
    def __init__(self, lexer, eoftoken):
        self.end = False
        self.lexer = lexer
        self.eof = eoftoken

    def token(self):
        tok = self.lexer.token()
        if tok is None:
            if self.end:
                self.end = False
            else:
                self.end = True
                tok = lex.LexToken()
                tok.type = self.eof
                tok.value = None
                tok.lexpos = self.lexer.lexpos
                tok.lineno = self.lexer.lineno
        # print ('custom', tok)
        return tok

    def __getattr__(self, name):
        return getattr(self.lexer, name)


lexer = ProxyLexer(orig_lexer, 'EOF')
lexer.lexer.curlyBalance = 0


def test_lex():
    # data = raw_input()

    #	c_file_name = raw_input('c file name: ')
    c_file_name = "test1.c"
    c_file = open(c_file_name, "r")
    contents = "".join(c_file.readlines())

    lexer.input(contents)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print tok  # .value, find_column(lexer.lexdata, tok)

# test_lex()

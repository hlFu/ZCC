#!/usr/bin/python
from __future__ import print_function
import ply.lex as lex
import ply.yacc as yacc
import ZCClex
from ZCClex import tokens

def construct_node(p, parent_name):
	p[0] = 	parent_name
	p[0] = list(p)


#def p_error_unit(p):
#	"""
#	error_unit : error
#	"""
#	print("error_unit")
#	construct_node(p, "error_unit")
	
def p_translation_unit(p):
	"""
	translation_unit : external_declaration
	translation_unit : translation_unit external_declaration
	"""
	construct_node(p, "translation_unit")
	
def p_external_declaration(p):
	"""
	external_declaration : declaration
	external_declaration : function_definition
	"""
#	external_declaration : error_unit
	construct_node(p, "external_declaration")

def p_declaration(p):
	"""
	declaration : declaration_specifiers ';'
	declaration : declaration_specifiers init_declarator_list ';'
	"""
#	| declaration_specifiers error
#	| declaration_specifiers init_declarator_list error
#	last_idx = len(p) - 1
#	if p[last_idx] != ';':
#		print("Error type: Missing semicolon after %s." % (p[last_idx]))
	construct_node(p, "declaration")
		


def p_declaration_specifiers(p):
	"""
	declaration_specifiers : storage_class_specifier
	| storage_class_specifier declaration_specifiers
	| type_specifier
	| type_specifier declaration_specifiers
	| type_qualifier
	| type_qualifier declaration_specifiers
	"""
	construct_node(p, "declaration_specifiers")	


def p_primary_expression(p):
	"""
	primary_expression : IDENTIFIER
		| CONSTANT
		| STRING_LITERAL
		| '(' expression ')'
	"""
	construct_node(p, "primary_expression")	
	
def p_postfix_expression(p):
	"""
	postfix_expression : primary_expression
		| postfix_expression '[' expression ']'
		| postfix_expression '(' ')'
		| postfix_expression '(' argument_expression_list ')'
		| postfix_expression '.' IDENTIFIER
		| postfix_expression PTR_OP IDENTIFIER
		| postfix_expression INC_OP
		| postfix_expression DEC_OP
	"""
	construct_node(p, "postfix_expression")

def p_argument_expression_list(p):
	"""
	argument_expression_list : assignment_expression
		| argument_expression_list ',' assignment_expression
	"""
	construct_node(p, "argument_expression_list")
	
def p_unary_expression(p):
	"""
unary_expression : postfix_expression
	| INC_OP unary_expression
	| DEC_OP unary_expression
	| unary_operator cast_expression
	| SIZEOF unary_expression
	| SIZEOF '(' type_name ')'
	"""
	construct_node(p, "unary_expression")	
	

def p_unary_operator(p):
	"""
unary_operator : '&'
	| '*'
	| '+'
	| '-'
	| '~'
	| '!'
	"""
	construct_node(p, "unary_operator")
	
def p_cast_expression(p):
	"""	
cast_expression : unary_expression
	| '(' type_name ')' cast_expression
	"""
	construct_node(p, "cast_expression")	

def p_multiplicative_expression(p):
	"""
multiplicative_expression : cast_expression
	| multiplicative_expression '*' cast_expression
	| multiplicative_expression '/' cast_expression
	| multiplicative_expression '%' cast_expression
	"""
	construct_node(p, "multiplicative_expression")

def p_additive_expression(p):
	"""
additive_expression : multiplicative_expression
	| additive_expression '+' multiplicative_expression
	| additive_expression '-' multiplicative_expression	
	"""

	construct_node(p, "additive_expression")

def p_shift_expression(p):
	"""
shift_expression : additive_expression
	| shift_expression LEFT_OP additive_expression
	| shift_expression RIGHT_OP additive_expression
	"""
	construct_node(p, "shift_expression")
	
def p_relational_expression(p):
	"""
relational_expression : shift_expression
	| relational_expression '<' shift_expression
	| relational_expression '>' shift_expression
	| relational_expression LE_OP shift_expression
	| relational_expression GE_OP shift_expression
	"""
	construct_node(p, "relational_expression")

def p_equality_expression(p):
	"""
equality_expression : relational_expression
	| equality_expression EQ_OP relational_expression
	| equality_expression NE_OP relational_expression
	"""
	construct_node(p, "equality_expression")

def p_and_expression(p):
	"""
and_expression : equality_expression
	| and_expression '&' equality_expression
	"""
	construct_node(p, "and_expression")

def p_exclusive_or_expression(p):
	"""
exclusive_or_expression : and_expression
	| exclusive_or_expression '^' and_expression
	"""
	construct_node(p, "exclusive_or_expression")
	
def p_inclusive_or_expression(p):
	"""	
inclusive_or_expression : exclusive_or_expression
	| inclusive_or_expression '|' exclusive_or_expression
	"""
	construct_node(p, "inclusive_or_expression")

def p_logical_and_expression(p):
	"""
logical_and_expression : inclusive_or_expression
	| logical_and_expression AND_OP inclusive_or_expression
	"""
	construct_node(p, "logical_and_expression")
	
def p_logical_or_expression(p):
	"""
logical_or_expression : logical_and_expression
	| logical_or_expression OR_OP logical_and_expression
	"""
	construct_node(p, "logical_or_expression")

def p_conditional_expression(p):
	"""
conditional_expression : logical_or_expression
	| logical_or_expression '?' expression ':' conditional_expression
	"""
	construct_node(p, "cnditional_expression")

def p_assignment_expression(p):
	"""
assignment_expression : conditional_expression
	| unary_expression assignment_operator assignment_expression
	"""
	construct_node(p, "assignment_expression")

def p_assignment_operator(p):
	"""
assignment_operator : '='
	| MUL_ASSIGN
	| DIV_ASSIGN
	| MOD_ASSIGN
	| ADD_ASSIGN
	| SUB_ASSIGN
	| LEFT_ASSIGN
	| RIGHT_ASSIGN
	| AND_ASSIGN
	| XOR_ASSIGN
	| OR_ASSIGN
	"""
	construct_node(p, "assignment_operator")
	
def p_expression(p):
	"""
expression : assignment_expression
	| expression ',' assignment_expression
	"""
	construct_node(p, "expression")

def p_constant_expression(p):
	"""
constant_expression : conditional_expression
	"""
	construct_node(p, "constant_expression")
	
def p_init_declarator_list(p):
	"""
init_declarator_list : init_declarator
	| init_declarator_list ',' init_declarator
	"""
	construct_node(p, "init_declarator_list")

def p_init_declarator(p):
	"""
init_declarator : declarator
	| declarator '=' initializer
	"""
	construct_node(p, "init_declarator")

def p_storage_class_specifier(p):
	"""
storage_class_specifier : TYPEDEF
	| EXTERN
	| STATIC
	| AUTO
	| REGISTER
	"""
	construct_node(p, "storage_class_specifier")

def p_type_specifier(p):
	"""
type_specifier : VOID
	| CHAR
	| SHORT
	| INT
	| LONG
	| FLOAT
	| DOUBLE
	| SIGNED
	| UNSIGNED
	| struct_or_union_specifier
	| enum_specifier
	"""
#	| TYPE_NAME
	construct_node(p, "type_specifier")

def p_struct_or_union_specifier(p):
	"""
struct_or_union_specifier : struct_or_union IDENTIFIER '{' struct_declaration_list '}'
	| struct_or_union '{' struct_declaration_list '}'
	| struct_or_union IDENTIFIER
	"""
	construct_node(p, "struct_or_union_specifier")

def p_struct_or_union(p):
	"""
struct_or_union : STRUCT
	| UNION
	"""
	construct_node(p, "struct_or_union")

def p_struct_declaration_list(p):
	"""
struct_declaration_list : struct_declaration
	| struct_declaration_list struct_declaration
	"""
	construct_node(p, "struct_declaration_list")

def p_struct_declaration(p):
	"""
struct_declaration : specifier_qualifier_list struct_declarator_list ';'
	"""
#	| specifier_qualifier_list struct_declarator_list error
#	last_idx = len(p) - 1
#	if p[last_idx] != ';':
#		print("Error type: Missing semicolon after %s." % (p[last_idx]))
	construct_node(p, "struct_declaration")



def p_specifier_qualifier_list(p):
	"""
specifier_qualifier_list : type_specifier specifier_qualifier_list
	| type_specifier
	| type_qualifier specifier_qualifier_list
	| type_qualifier
	"""
	construct_node(p, "specifier_qualifier_list")

def p_struct_declarator_list(p):
	"""
struct_declarator_list : struct_declarator
	| struct_declarator_list ',' struct_declarator
	"""
	construct_node(p, "struct_declarator_list")

def p_struct_declarator(p):
	"""
struct_declarator : declarator
	| ':' constant_expression
	| declarator ':' constant_expression
	"""
	construct_node(p, "struct_declarator")

def p_enum_specifier(p):
	"""
enum_specifier : ENUM '{' enumerator_list '}'
	| ENUM IDENTIFIER '{' enumerator_list '}'
	| ENUM IDENTIFIER
	"""
	construct_node(p, "enum_specifier")

def p_enumerator_list(p):
	"""
enumerator_list : enumerator
	| enumerator_list ',' enumerator
	"""
	construct_node(p, "enumerator_list")

def p_enumerator(p):
	"""
enumerator : IDENTIFIER
	| IDENTIFIER '=' constant_expression
	"""
	construct_node(p, "enumerator")

def p_type_qualifier(p):
	"""
type_qualifier : CONST
	| VOLATILE
	"""
	construct_node(p, "type_qualifier")

def p_declarator(p):
	"""
declarator : pointer direct_declarator
	| direct_declarator
	"""
	construct_node(p, "declarator")

def p_direct_declarator(p):
	"""
direct_declarator : IDENTIFIER
	| '(' declarator ')'
	| direct_declarator '[' constant_expression ']'
	| direct_declarator '[' ']'
	| direct_declarator '(' parameter_type_list ')'
	| direct_declarator '(' identifier_list ')'
	| direct_declarator '(' ')'
	"""
	construct_node(p, "direct_declarator")

def p_pointer(p):
	"""
pointer : '*'
	| '*' type_qualifier_list
	| '*' pointer
	| '*' type_qualifier_list pointer
	"""
	construct_node(p, "pointer")

def p_type_qualifier_list(p):
	"""
type_qualifier_list : type_qualifier
	| type_qualifier_list type_qualifier
	"""
	construct_node(p, "type_qualifier_list")

def p_parameter_type_list(p):
	"""
parameter_type_list : parameter_list
	| parameter_list ',' ELLIPSIS
	"""
	construct_node(p, "parameter_type_list")
	
def p_parameter_list(p):
	"""
parameter_list : parameter_declaration
	| parameter_list ',' parameter_declaration
	"""
	construct_node(p, "parameter_list")

def p_parameter_declaration(p):
	"""
parameter_declaration : declaration_specifiers declarator
	| declaration_specifiers abstract_declarator
	| declaration_specifiers
	"""
	construct_node(p, "parameter_declaration")

def p_identifier_list(p):
	"""
identifier_list : IDENTIFIER
	| identifier_list ',' IDENTIFIER
	"""
	construct_node(p, "identifier_list")

def p_type_name(p):
	"""
type_name : specifier_qualifier_list
	| specifier_qualifier_list abstract_declarator
	"""
	construct_node(p, "type_name")

def p_abstract_declarator(p):
	"""
abstract_declarator : pointer
	| direct_abstract_declarator
	| pointer direct_abstract_declarator
	"""
	construct_node(p, "abstract_declarator")

def p_direct_abstract_declarator(p):
	"""
direct_abstract_declarator : '(' abstract_declarator ')'
	| '[' ']'
	| '[' constant_expression ']'
	| direct_abstract_declarator '[' ']'
	| direct_abstract_declarator '[' constant_expression ']'
	| '(' ')'
	| '(' parameter_type_list ')'
	| direct_abstract_declarator '(' ')'
	| direct_abstract_declarator '(' parameter_type_list ')'
	"""
	construct_node(p, "direct_abstract_declarator")

def p_initializer(p):
	"""
initializer : assignment_expression
	| '{' initializer_list '}'
	| '{' initializer_list ',' '}'
	"""
	construct_node(p, "initializer")

def p_initiazer_list(p):
	"""
initializer_list : initializer
	| initializer_list ',' initializer
	"""
	construct_node(p, "initializer_list")

def p_statement(p):
	"""
statement : labeled_statement
	| compound_statement
	| expression_statement
	| selection_statement
	| iteration_statement
	| jump_statement
	"""
	construct_node(p, "statement")

def p_labeled_statement(p):
	"""
labeled_statement : IDENTIFIER ':' statement
	| CASE constant_expression ':' statement
	| DEFAULT ':' statement
	"""
	construct_node(p, "labeled_statement")

def p_compound_statement(p):
	"""
compound_statement : '{' '}'
	| '{' statement_list '}'
	| '{' declaration_list '}'
	| '{' declaration_list statement_list '}'
	"""
	construct_node(p, "compound_statement")

def p_declaration_list(p):
	"""
declaration_list : declaration
	| declaration_list declaration
	"""
	construct_node(p, "declaration_list")

def p_statement_list(p):
	"""
statement_list : statement
	| statement_list statement
	"""
	construct_node(p, "statement_list")

def p_expression_statement(p):
	"""
expression_statement : ';'
	| expression ';'
	"""
#	| expression error
#	| error
#	last_idx = len(p) - 1
#	if p[last_idx] != ';':
#		print("Error type: Missing semicolon after %s." % (p[last_idx]))
	construct_node(p, "expression_statement")	
	

def p_selection_statement(p):
	"""
selection_statement : IF '(' expression ')' statement
	| IF '(' expression ')' statement ELSE statement
	| SWITCH '(' expression ')' statement
	"""
	construct_node(p, "selection_statement")
	
def p_iteration_statement(p):
	"""
iteration_statement : WHILE '(' expression ')' statement
	| DO statement WHILE '(' expression ')' ';'
	| FOR '(' expression_statement expression_statement ')' statement
	| FOR '(' expression_statement expression_statement expression ')' statement
	"""
#	last_idx = len(p) - 1
#	if p[last_idx] != ';':
#		print("Error type: Missing semicolon after %s." % (p[last_idx]))
	construct_node(p, "iteration_statement")

def p_jump_statement(p):
	"""
jump_statement : GOTO IDENTIFIER ';'
	| CONTINUE ';'
	| BREAK ';'
	| RETURN ';'
	| RETURN expression ';'
	"""
#	last_idx = len(p) - 1
#	if p[last_idx] != ';':
#		print("Error type: Missing semicolon after %s." % (p[last_idx]))
	construct_node(p, "jump_statement")

def p_function_definition(p):
	"""
function_definition : declaration_specifiers declarator declaration_list compound_statement
	| declaration_specifiers declarator compound_statement
	"""
	construct_node(p, "function_definition")

		
def p_error(p):
	print("Syntax error at %r, at line: %d, column: %d." % (p.value, p.lexer.lineno, ZCClex.find_column(p.lexer.lexdata, p)))

	if not p:
		print("End of file.")
		return
	
	while True:
		tok = parser.token()
		if not tok or tok.type == '}' or tok.type == ';':
			break	
	parser.restart()
	
parser = yacc.yacc(start = 'translation_unit')


def printAST(p, n=0):
	if p is not None:
		print('  ' * n, end='')
		if type(p) is list:
			print(p[0])
			for node in p[1:]:
				printAST(node, n + 1)
		else:
			print(p)


#if __name__ == "__main__":
#while True:
#try:
#	   c_file_name = raw_input('c file name: ')
c_file_name = "missSEMI.c"
c_file = open(c_file_name, "r")
   
contents = "".join(c_file.readlines())
#except EOFError:
#   break
#if not contents: continue
result = parser.parse(contents)
printAST(result)
#!/usr/bin/python
from __future__ import print_function
import ply.lex as lex
import ply.yacc as yacc
import ZCClex
from symbol.symtab import symtab_declaration, symtab_function_definition
from public.ZCCglobal import global_context
from ZCClex import tokens
from pprint import pprint

aTuple = (1, 2)


def handleMissingSEMI(p, parentname="", checkPair=()):
    last_idx = len(p) - 1
    if (len(checkPair) == 0 or (len(checkPair) > 0 and p[
            checkPair[0]] == checkPair[1])) and p[last_idx] != ';':
        print(
            "Error type: missing semicolon before %s. at line: %d, lex pos: %d in %s.\n" %
            (p[last_idx], p.lineno(last_idx), p.lexpos(last_idx), parentname))
        p[last_idx] = ';'
        parser.errorCounter = 0
        parser.errok()
        return [last_idx]
    else:
        return []


def handleMissingRCURLYBRACKET(p):
    last_idx = len(p) - 1
    if p[last_idx] != '}':
        print(
            "Error type: missing right curly bracket before %s. at line: %d, lex pos: %d.\n" %
            (p[last_idx], p.lineno(last_idx), p.lexpos(last_idx)))
        p[last_idx] = '}'
        parser.errorCounter = 0
        parser.errok()


def handleErrorID(p, idx):
    if len(p) > idx and isinstance(p[idx],
                                   type(aTuple)) and p[idx][1] == "ERRORID":
        print("Syntax error at %r, at line: %d, lex pos: %d." %
              (p[idx][0], p.lineno(idx), p.lexpos(idx)))
        print("Error type: wrong IDENTIFIER format.\n")
        p[idx] = p[idx][0]
        parser.errorCounter = 0


def construct_node(p, parent_name, del_list=[]):
    p[0] = [parent_name]
    #    print("%s's del_list: " % (parent_name))
    #    print(del_list)
    for i in range(1, len(p)):
        if i not in del_list:
            p[0].append(p[i])


def p_outer_translation_unit(p):
    """
    outer_translation_unit : translation_unit EOF
    """
    p[0] = p[1]
    # construct_node(p, "outer_translation_unit")


def p_translation_unit(p):
    """
    translation_unit : external_declaration
    | translation_unit external_declaration
    """
    if len(p) == 2:
        construct_node(p, "translation_unit")
    elif len(p) == 3:
        # printAST(p[1])
        p[1].append(p[2])
        p[0] = p[1]
    else:
        raise Exception("translation_unit just has two children")


def p_external_declaration(p):
    """
    external_declaration : function_definition
    | declaration
    """
    p[0] = p[1]
    if p[0][0] == 'declaration':
        symtab_declaration(p[0], global_context)
    elif p[0][0] == 'function_definition':
        symtab_function_definition(p[0], global_context)
    # construct_node(p, "external_declaration")


def p_declaration(p):
    """
    declaration : declaration_specifiers SEMICOLON
    | declaration_specifiers init_declarator_list SEMICOLON
    | declaration_specifiers error
    | declaration_specifiers init_declarator_list error
    """
    del_list = handleMissingSEMI(p, "declaration")
    construct_node(p, "declaration", del_list)


#    print(p[0])

# def p_constant(p):
#     """
#     constant : NUMBER_CONSTANT
#     | CHARACTER_CONSTANT
#     """
#     construct_node(p, "constant")


def p_declaration_specifiers(p):
    """
    declaration_specifiers : type_specifier
    | type_specifier type_qualifier
    | type_qualifier type_specifier
    | storage_class_specifier type_specifier
    | storage_class_specifier type_specifier type_qualifier
    | storage_class_specifier type_qualifier type_specifier
    """
    # """
    # declaration_specifiers : storage_class_specifier
    # | storage_class_specifier declaration_specifiers
    # | type_specifier
    # | type_specifier declaration_specifiers
    # | type_qualifier
    # | type_qualifier declaration_specifiers
    # """
    construct_node(p, "declaration_specifiers")
    # printAST(p[0], 0)
    # pass


def p_primary_expression(p):
    """
    primary_expression : IDENTIFIER
        | ERRORID
        | NUMBER_CONSTANT
        | CHARACTER_CONSTANT
        | STRING_LITERAL
        | LBRACKET expression RBRACKET
    """
    handleErrorID(p, 1)
    if len(p) == 4:
        p[0] = p[2]
    else:
        construct_node(p, "primary_expression")


def p_postfix_expression(p):
    """
    postfix_expression : primary_expression
        | postfix_expression LSQUAREBRACKET expression RSQUAREBRACKET
        | postfix_expression LBRACKET RBRACKET
        | postfix_expression LBRACKET argument_expression_list RBRACKET
        | postfix_expression PERIOD IDENTIFIER
        | postfix_expression PTR_OP IDENTIFIER
        | postfix_expression PERIOD ERRORID
        | postfix_expression PTR_OP ERRORID
        | postfix_expression INC_OP
        | postfix_expression DEC_OP
    """
    handleErrorID(p, 3)
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "postfix_expression")


def p_argument_expression_list(p):
    """
    argument_expression_list : assignment_expression
        | argument_expression_list COMMA assignment_expression
    """
    if len(p) == 2:
        construct_node(p, "argument_expression_list")
    else:
        p[1].append(p[2:])
        p[0] = p[1]


def p_unary_expression(p):
    """
unary_expression : postfix_expression
    | INC_OP unary_expression
    | DEC_OP unary_expression
    | unary_operator cast_expression
    | SIZEOF unary_expression
    | SIZEOF LBRACKET type_name RBRACKET
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "unary_expression")


def p_unary_operator(p):
    """
unary_operator : AND
    | STAR
    | PLUS
    | MINUS
    | UNOT
    | NOT
    """
    construct_node(p, "unary_operator")


def p_cast_expression(p):
    """
cast_expression : unary_expression
    | LBRACKET type_name RBRACKET cast_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "cast_expression")
        # printAST(p[0], 0)


def p_multiplicative_expression(p):
    """
multiplicative_expression : cast_expression
    | multiplicative_expression STAR cast_expression
    | multiplicative_expression DIVIDE cast_expression
    | multiplicative_expression MOD cast_expression
    | multiplicative_expression STAR error cast_expression
    | multiplicative_expression DIVIDE error cast_expression
    | multiplicative_expression MOD error cast_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "multiplicative_expression", del_list)


def p_additive_expression(p):
    """
additive_expression : multiplicative_expression
    | additive_expression PLUS multiplicative_expression
    | additive_expression MINUS multiplicative_expression
    | additive_expression PLUS error multiplicative_expression
    | additive_expression MINUS error multiplicative_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "additive_expression", del_list)


def p_shift_expression(p):
    """
shift_expression : additive_expression
    | shift_expression LEFT_OP additive_expression
    | shift_expression RIGHT_OP additive_expression
    | shift_expression LEFT_OP error additive_expression
    | shift_expression RIGHT_OP error additive_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "shift_expression", del_list)


def p_relational_expression(p):
    """
relational_expression : shift_expression
    | relational_expression LT shift_expression
    | relational_expression GT shift_expression
    | relational_expression LE_OP shift_expression
    | relational_expression GE_OP shift_expression
    | relational_expression LT error shift_expression
    | relational_expression GT error shift_expression
    | relational_expression LE_OP error shift_expression
    | relational_expression GE_OP error shift_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0

    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "relational_expression", del_list)


def p_equality_expression(p):
    """
equality_expression : relational_expression
    | equality_expression EQ_OP relational_expression
    | equality_expression NE_OP relational_expression
    | equality_expression EQ_OP error relational_expression
    | equality_expression NE_OP error relational_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "equality_expression", del_list)


def p_and_expression(p):
    """
and_expression : equality_expression
    | and_expression AND equality_expression
    | and_expression AND error equality_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0

    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "and_expression", del_list)


def p_exclusive_or_expression(p):
    """
exclusive_or_expression : and_expression
    | exclusive_or_expression XOR and_expression
    | exclusive_or_expression XOR error and_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0

    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "exclusive_or_expression", del_list)


def p_inclusive_or_expression(p):
    """
inclusive_or_expression : exclusive_or_expression
    | inclusive_or_expression OR exclusive_or_expression
    | inclusive_or_expression OR error exclusive_or_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0

    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "inclusive_or_expression", del_list)


def p_logical_and_expression(p):
    """
logical_and_expression : inclusive_or_expression
    | logical_and_expression AND_OP inclusive_or_expression
    | logical_and_expression AND_OP error inclusive_or_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0

    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "logical_and_expression", del_list)


def p_logical_or_expression(p):
    """
logical_or_expression : logical_and_expression
    | logical_or_expression OR_OP logical_and_expression
    | logical_or_expression OR_OP error logical_and_expression
    """
    del_list = []
    if len(p) == 5:
        print(
            "Error type: error token after %s. at line: %d.\n" %
            (p[2], p.lineno(2)))
        del_list.append(3)
        parser.errorCounter = 0

    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "logical_or_expression", del_list)


def p_conditional_expression(p):
    """
conditional_expression : logical_or_expression
    | logical_or_expression QUESTIONMARK expression COLON conditional_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "cnditional_expression")


def p_assignment_expression(p):
    """
assignment_expression : conditional_expression
    | unary_expression assignment_operator assignment_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "assignment_expression")


def p_assignment_operator(p):
    """
assignment_operator : ASSIGN
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
    | expression COMMA assignment_expression
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        construct_node(p, "expression")
        # if len(p) == 2:
        #     construct_node(p, "expression")
        # elif len(p) == 4:
        #     # printAST(p[1])
        #     p[1].append(p[3])
        #     p[0] = p[1]
        # else:
        #     raise Exception("expression just has 2 or 4 children")


def p_constant_expression(p):
    """
constant_expression : conditional_expression
    """
    construct_node(p, "constant_expression")


def p_init_declarator_list(p):
    """
init_declarator_list : init_declarator
    | init_declarator_list COMMA init_declarator
    """
    if len(p) == 2:
        construct_node(p, "init_declarator_list")
    else:
        p[1].append(p[2])
        p[1].append(p[3])
        p[0] = p[1]


def p_init_declarator(p):
    """
init_declarator : declarator
    | declarator ASSIGN initializer
    """
    construct_node(p, "init_declarator")


def p_storage_class_specifier(p):
    """
storage_class_specifier : TYPEDEF
    | EXTERN
    | STATIC
    """
    construct_node(p, "storage_class_specifier")


def p_integer_type(p):
    """
    integer_type : CHAR
    | SHORT
    | INT
    | LONG
    | UNSIGNED integer_type
    | SIGNED integer_type
    | SHORT integer_type
    | LONG integer_type
    """
    if len(p) == 2:
        construct_node(p, "integer_type")
    else:
        p[2].insert(1, p[1])
        p[0] = p[2]
        # print(p[0])


def p_type_specifier(p):
    """type_specifier : VOID
    | integer_type
    | FLOAT
    | DOUBLE
    | struct_or_union_specifier
    | enum_specifier
    | TYPE_NAME
    """
    #    | TYPE_NAME
    construct_node(p, "type_specifier")


def p_struct_or_union_specifier(p):
    """
struct_or_union_specifier : struct_or_union IDENTIFIER LCURLYBRACKET struct_declaration_list RCURLYBRACKET
    | struct_or_union TYPE_NAME LCURLYBRACKET struct_declaration_list RCURLYBRACKET
    | struct_or_union ERRORID LCURLYBRACKET struct_declaration_list RCURLYBRACKET
    | struct_or_union LCURLYBRACKET struct_declaration_list RCURLYBRACKET
    | struct_or_union IDENTIFIER
    | struct_or_union TYPE_NAME
    | struct_or_union ERRORID
    """
    handleErrorID(p, 2)
    construct_node(p, "struct_or_union_specifier")


def p_struct_or_union(p):
    """
struct_or_union : STRUCT
    | UNION
    """
    construct_node(p, "struct_or_union")


def p_struct_declaration_list(p):
    """struct_declaration_list : struct_declaration
    | struct_declaration_list struct_declaration
    """
    if len(p) == 2:
        construct_node(p, "struct_declaration_list")
    elif len(p) == 3:
        p[1].append(p[2])
        p[0] = p[1]


def p_struct_declaration(p):
    """struct_declaration : specifier_qualifier_list struct_declarator_list SEMICOLON
    | specifier_qualifier_list struct_declarator_list error
    """
    del_list = []
    last_idx = len(p) - 1
    if p[last_idx] != ';':
        print("struct_declaration")
        del_list.append(last_idx)
        parser.errorCounter = 0
    construct_node(p, "struct_declaration", del_list)


#    print(p[0])


def p_specifier_qualifier_list(p):
    """
specifier_qualifier_list : type_specifier
    | type_specifier type_qualifier
    | type_qualifier type_specifier
    """
    construct_node(p, "specifier_qualifier_list")


def p_struct_declarator_list(p):
    """
struct_declarator_list : declarator
    | struct_declarator_list COMMA declarator
    """
    if len(p) == 2:
        construct_node(p, "struct_declarator_list")
    else:
        p[1].append(p[2])
        p[1].append(p[3])
        p[0] = p[1]


# def p_struct_declarator(p):
#     """
# struct_declarator : declarator
#     | COLON constant_expression
#     | declarator COLON constant_expression
#     """
#     construct_node(p, "struct_declarator")


def p_enum_specifier(p):
    """
enum_specifier : ENUM LCURLYBRACKET enumerator_list RCURLYBRACKET
    | ENUM IDENTIFIER LCURLYBRACKET enumerator_list RCURLYBRACKET
    | ENUM IDENTIFIER
    | ENUM ERRORID LCURLYBRACKET enumerator_list RCURLYBRACKET
    | ENUM ERRORID
    """
    handleErrorID(p, 2)
    construct_node(p, "enum_specifier")


def p_enumerator_list(p):
    """
enumerator_list : enumerator
    | enumerator_list COMMA enumerator
    """
    if len(p) == 2:
        construct_node(p, "enumerator_list")
    else:
        p[1].append(p[2])
        p[1].append(p[3])
        p[0] = p[1]


def p_enumerator(p):
    """
enumerator : IDENTIFIER
    | IDENTIFIER ASSIGN constant_expression
    | ERRORID
    | ERRORID ASSIGN constant_expression
    """
    handleErrorID(p, 1)
    construct_node(p, "enumerator")


def p_type_qualifier(p):
    """
type_qualifier : CONST
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
direct_declarator : direct_declarator LSQUAREBRACKET constant_expression RSQUAREBRACKET
    | direct_declarator LSQUAREBRACKET RSQUAREBRACKET
    | direct_declarator LBRACKET parameter_type_list RBRACKET
    | direct_declarator LBRACKET RBRACKET
    | IDENTIFIER
    | LBRACKET declarator RBRACKET
    | ERRORID
    """
    handleErrorID(p, 1)
    construct_node(p, "direct_declarator")


def p_pointer(p):
    """
pointer : STAR
    | STAR CONST
    | pointer STAR
    | pointer STAR CONST
    """
    if p[1][0] != 'pointer':
        construct_node(p, "pointer")
    else:
        p[1].append(p[2])
        if len(p) == 4:
            p[1].append(p[3])
        p[0] = p[1]


def p_type_qualifier_list(p):
    """
type_qualifier_list : type_qualifier
    | type_qualifier_list type_qualifier
    """
    construct_node(p, "type_qualifier_list")


def p_parameter_type_list(p):
    """
parameter_type_list : parameter_list
    | parameter_list COMMA ELLIPSIS
    """
    construct_node(p, "parameter_type_list")


def p_parameter_list(p):
    """
parameter_list : parameter_declaration
    | parameter_list COMMA parameter_declaration
    """
    if len(p) == 2:
        construct_node(p, "parameter_list")
    else:
        p[1].append(p[2])
        p[1].append(p[3])
        p[0] = p[1]


def p_parameter_declaration(p):
    """
parameter_declaration : declaration_specifiers declarator
    | declaration_specifiers abstract_declarator
    | declaration_specifiers
    """
    construct_node(p, "parameter_declaration")


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
direct_abstract_declarator : LBRACKET abstract_declarator RBRACKET
    | LSQUAREBRACKET RSQUAREBRACKET
    | LSQUAREBRACKET constant_expression RSQUAREBRACKET
    | direct_abstract_declarator LSQUAREBRACKET RSQUAREBRACKET
    | direct_abstract_declarator LSQUAREBRACKET constant_expression RSQUAREBRACKET
    | LBRACKET RBRACKET
    | LBRACKET parameter_type_list RBRACKET
    | direct_abstract_declarator LBRACKET RBRACKET
    | direct_abstract_declarator LBRACKET parameter_type_list RBRACKET
    """
    construct_node(p, "direct_abstract_declarator")


def p_initializer(p):
    """
initializer : assignment_expression
    | LCURLYBRACKET initializer_list RCURLYBRACKET
    | LCURLYBRACKET initializer_list COMMA RCURLYBRACKET
    """
    construct_node(p, "initializer")


def p_initiazer_list(p):
    """
initializer_list : initializer
    | initializer_list COMMA initializer
    """
    if len(p) == 2:
        construct_node(p, "initializer_list")
    else:
        p[1].append(p[2])
        p[1].append(p[3])
        p[0] = p[1]


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
labeled_statement : CASE constant_expression COLON statement
    | DEFAULT COLON statement
    """
    #    | IDENTIFIER COLON statement
    #    | ERRORID COLON statement
    #    handleErrorID(p, 1)
    construct_node(p, "labeled_statement")


def p_compound_statement(p):
    """
compound_statement : LCURLYBRACKET RCURLYBRACKET
    | LCURLYBRACKET statement_list RCURLYBRACKET
    | LCURLYBRACKET declaration_list RCURLYBRACKET
    | LCURLYBRACKET declaration_list statement_list RCURLYBRACKET
    | LCURLYBRACKET error
    | LCURLYBRACKET statement_list error
    | LCURLYBRACKET declaration_list error
    | LCURLYBRACKET declaration_list statement_list error
    """
    handleMissingRCURLYBRACKET(p)
    construct_node(p, "compound_statement")


def p_declaration_list(p):
    """
declaration_list : declaration
    | declaration_list declaration
    """
    if len(p) == 2:
        construct_node(p, "declaration_list")
    elif len(p) == 3:
        p[1].append(p[2])
        p[0] = p[1]


def p_statement_list(p):
    """
statement_list : statement
    | statement_list statement
    """
    if len(p) == 2:
        construct_node(p, "statement_list")
    if len(p) == 3:
        p[1].append(p[2])
        p[0] = p[1]


def p_expression_statement(p):
    """
expression_statement : SEMICOLON
    | expression SEMICOLON
    | expression error
    """

    #    del_list = []
    #    last_idx = len(p) - 1
    #    if p[last_idx] != ';':
    #        print("expression_statement")
    #        print("Error type: Missing semicolon before %s. at line: %d, lex pos: %d.\n" % (p[last_idx], p.lineno(last_idx), p.lexpos(last_idx)))
    #        del_list.append(last_idx)
    #        parser.errorCounter = 0
    del_list = handleMissingSEMI(p, "expression_statement")
    construct_node(p, "expression_statement", del_list)


def p_selection_statement(p):
    """
selection_statement : IF LBRACKET expression RBRACKET statement
    | IF LBRACKET expression RBRACKET statement ELSE statement
    | SWITCH LBRACKET expression RBRACKET statement
    """
    construct_node(p, "selection_statement")


def p_iteration_statement(p):
    """
iteration_statement : WHILE LBRACKET expression RBRACKET statement
    | DO statement WHILE LBRACKET expression RBRACKET SEMICOLON
    | DO statement WHILE LBRACKET expression RBRACKET error
    | FOR LBRACKET expression_statement expression_statement RBRACKET statement
    | FOR LBRACKET expression_statement expression_statement expression RBRACKET statement
    """
    #    del_list = []
    #    last_idx = len(p) - 1
    #    if p[1] == 'do' and p[last_idx] != ';':
    #        print("iteration statement")
    #        print("Error type: Missing semicolon before %s. at line: %d, lex pos: %d.\n" % (p[last_idx], p.lineno(last_idx), p.lexpos(last_idx)))
    #        del_list.append(last_idx)
    #        parser.errorCounter = 0
    del_list = handleMissingSEMI(p, "iteration_statement", (1, 'do'))
    construct_node(p, "iteration_statement", del_list)


#    print(p[0])

def p_jump_statement(p):
    """
jump_statement : CONTINUE SEMICOLON
    | BREAK SEMICOLON
    | RETURN SEMICOLON
    | RETURN expression SEMICOLON
    | CONTINUE error
    | BREAK error
    | RETURN error
    | RETURN expression error
    """
    #    del_list = []
    #    last_idx = len(p) - 1
    #    if p[last_idx] != ';':
    #        print("jump statement")
    #        print("Error type: Missing semicolon before %s. at line: %d, lex pos: %d.\n" % (p[last_idx], p.lineno(last_idx), p.lexpos(last_idx)))
    #        del_list.append(last_idx)
    #        parser.errorCounter = 0
    del_list = handleMissingSEMI(p, "jump_statement")
    construct_node(p, "jump_statement", del_list)


#    print(p[0])

def p_function_definition(p):
    """
function_definition : declaration_specifiers declarator compound_statement
    """
    construct_node(p, "function_definition")


def p_error(p):
    if not p:
        print("End of file.")
        return

    if p.type == 'EOF':
        if ZCClex.lexer.lexer.curlyBalance > 0:
            parser.errok()
            return lex.LexToken(
                'RCURCLYBRACKET',
                '}',
                p.lexer.lineno,
                p.lexer.lexpos)
        else:
            return

    print("Syntax error at %r, at line: %d, column: %d." % (
        p.value, p.lexer.lineno, ZCClex.find_column(p.lexer.lexdata, p)))
    if p.type == 'IDENTIFIER':
        print("Undefined Type " + p.value)

    if parser.errorCounter > 0:
        print("In panic mode\n")
        while True:
            tok = parser.token()
            if not tok or tok.type == 'SEMICOLON' or tok.type == 'RCURLYBRACKET':
                break
        parser.restart()
    else:
        parser.errorCounter += 1
    return p


def printAST(p, n=0):
    if p is not None:
        print(' |' * n, end='-')
        # if type(p) is list:
        if isinstance(p, list):
            print(p[0])
            for node in p[1:]:
                printAST(node, n + 1)
        else:
            print(p)


parser = yacc.yacc(start='outer_translation_unit', debug=True)
parser.errorCounter = 0

if __name__ == "__main__":
    # pprint(parser.__dict__)
    # while True:
    # try:
    #       c_file_name = raw_input('c file name: ')
    c_file_name = "test1.c"
    c_file = open(c_file_name, "r")

    contents = "".join(c_file.readlines())
    # except EOFError:
    #   break
    # if not contents: continue
    # result = parser.parse(contents, lexer = ZCClex.orig_lexer)
    result = parser.parse(contents, lexer=ZCClex.lexer)
    printAST(result)

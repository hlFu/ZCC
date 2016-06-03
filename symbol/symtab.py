#!/usr/bin/python
ctypes = []


def children_are(ast, children):
    if len(ast) != len(children) + 1:
        return False
    for i in xrange(1, len(children)):
        if ast[1 + i][0] != children[i]:
            return False
    return True


def is_type(s):
    return s in ctypes


def get_IDENTIFER(ast):
    if ast[0] == 'declarator':
        if children_are(ast, ['pointer', 'direct_declarator']):
            return get_IDENTIFER(ast[2])
        elif children_are(ast, ['direct_declarator']):
            return get_IDENTIFER(ast[1])
    if ast[0] == 'direct_declarator':
        if children_are(ast, ['(', 'declarator', ')']):
            return get_IDENTIFER(ast[2])
        elif ast[1][0] == 'direct_declarator':
            return get_IDENTIFER(ast[1])
        else:
            return ast[1]


def symtab_declaration(declaration):
    if is_typedef(declaration[1]) \
            and children_are(
                    declaration,
                    ['declaration_specifiers',
                     'init_declarator_list',
                     ';']):
        for init_declarator in declaration[2]:
            if init_declarator != ';':
                if children_are(init_declarator, ['declarator']):
                    ctypes.append(get_IDENTIFER(init_declarator[1]))
                else:
                    raise Exception("Initialization is not permit after typedef.")


def is_typedef(declaration_specifiers):
    return declaration_specifiers[1][1] == 'typedef'

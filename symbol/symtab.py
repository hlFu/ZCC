#!/usr/bin/python
from public.ZCCglobal import CType, FuncType, StructType, UnionType, EnumType, ArrayType, Context
from copy import deepcopy

c_types = {
    'char': CType('char', is_signed=True, size=1),
    'short': CType('short', is_signed=True, size=2),
    'int': CType('int', is_signed=True, size=4),
    'long': CType('long', is_signed=True, size=4),
    'long long': CType('long', is_signed=True, size=8),

    'signed char': CType('signed char', is_signed=True, size=1),
    'signed short': CType('signed short', is_signed=True, size=2),
    'signed int': CType('signed int', is_signed=True, size=4),
    'signed long': CType('signed long', is_signed=True, size=4),
    'signed long long': CType('signed long', is_signed=True, size=8),

    'unsigned char': CType('unsigned char', is_signed=False, size=1),
    'unsigned short': CType('unsigned short', is_signed=False, size=2),
    'unsigned int': CType('unsigned int', is_signed=False, size=4),
    'unsigned long': CType('unsigned long', is_signed=False, size=4),
    'unsigned long long': CType('unsigned long', is_signed=False, size=8),

    'double': CType('double', size=8),
    'float': CType('float', size=4),
    'void': CType('void', size=0),

    # 'char const': CBaseType('char', is_signed=True, size=1, is_const=True),
    # 'short const': CBaseType('short', is_signed=True, size=2, is_const=True),
    # 'int const': CBaseType('int', is_signed=True, size=4, is_const=True),
    # 'long const': CBaseType('long', is_signed=True, size=4, is_const=True),
    # 'long long const': CBaseType('long', is_signed=True, size=8, is_const=True),
    #
    # 'signed char const': CBaseType('char', is_signed=True, size=1, is_const=True),
    # 'signed short const': CBaseType('short', is_signed=True, size=2, is_const=True),
    # 'signed int const': CBaseType('int', is_signed=True, size=4, is_const=True),
    # 'signed long const': CBaseType('long', is_signed=True, size=4, is_const=True),
    # 'signed long long const': CBaseType('long', is_signed=True, size=8, is_const=True),
    #
    # 'unsigned char const': CBaseType('char', is_signed=False, size=1, is_const=True),
    # 'unsigned short const': CBaseType('short', is_signed=False, size=2, is_const=True),
    # 'unsigned int const': CBaseType('int', is_signed=False, size=4, is_const=True),
    # 'unsigned long const': CBaseType('long', is_signed=False, size=4, is_const=True),
    # 'unsigned long long const': CBaseType('long', is_signed=False, size=8, is_const=True),
    #
    # 'double const': CBaseType('double', size=8, is_const=True),
    # 'float const': CBaseType('float', size=4, is_const=True),
}


# "int","char","long","short","double","float","void",
# "struct","union","enum","function"


def children_are(ast, children):
    if len(ast) != len(children) + 1:
        return False
    for i in xrange(1, len(children)):
        if ast[1 + i][0] != children[i]:
            return False
    return True


def is_type(s):
    return s in c_types


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
    # if ast[0] == 'init_declarator':
    #     return get_IDENTIFER(ast[1])


def symtab_type_specifier(type_specifier):
    child_name = type_specifier[1][0]
    if child_name == 'void':
        return c_types['void']

    elif child_name == 'float':
        return c_types['float']

    elif child_name == 'double':
        return c_types['double']

    elif child_name == 'integer_type':
        return symtab_integer_type(type_specifier[1])

    elif child_name == 'struct_or_union_specifier':
        return symtab_struct_or_union_specifier(type_specifier[1])

    elif child_name == 'enum_specifier':
        return symtab_enum_specifier(type_specifier[1])

    else:
        return c_types[type_specifier[1]]

def symtab_integer_type(integer_type):
    type_name = integer_type[-1]
    is_short = False
    is_long = False
    is_signed = False
    is_unsigned = False
    for child in integer_type[1:-1]:
        if child == 'long':
            is_long = True
        if child == 'short':
            is_short = True
        if child == 'signed':
            is_signed = True
        if child == 'unsigned':
            is_unsigned = True
    if is_short and is_long:
        raise Exception("short and long are conflict")
    if is_signed and is_unsigned:
        raise Exception("signed and unsigned are conflict")

    if type_name == 'char':
        if is_short or is_long:
            raise Exception("Char can't be short or long")

    if type_name == 'int':
        if is_short:
            type_name = 'short'
        if is_long:
            type_name = 'int'
    if is_signed:
        type_name = 'signed ' + type_name

    if is_unsigned:
        type_name = 'unsigned ' + type_name

    return c_types[type_name]


def symtab_struct_or_union_specifier(struct_or_union_specifier):
    type_name = ''
    c_type_class = None
    if struct_or_union_specifier[1][1] == 'struct':
        type_name = 'struct '
        c_type_class = StructType
    elif struct_or_union_specifier[1][1] == 'union':
        type_name = 'union '
        c_type_class = UnionType

    if len(struct_or_union_specifier) == 3:
        name = type_name + struct_or_union_specifier[2]
        if name not in c_types:
            c_types[name] = CType('Incomplete')
        print 'Add to type record:', name, ':', c_types[name]
        return c_types[name]
    elif len(struct_or_union_specifier) == 5:
        return c_type_class(
                members=symtab_struct_declaration_list(
                        struct_or_union_specifier[3]
                )
        )
    elif len(struct_or_union_specifier) == 6:
        name = type_name + struct_or_union_specifier[2]
        if name in c_types:
            raise Exception("Redefine " + struct_or_union_specifier[2])
        c_types[name] = c_type_class(members=symtab_struct_declaration_list(struct_or_union_specifier[4]))
        print 'Add to type record:', name, ':', c_types[name]
        return c_types[name]


def symtab_struct_declaration_list(struct_declaration_list):
    rval = []
    for struct_declaration in struct_declaration_list[1:]:
        for member in symtab_struct_declaration(struct_declaration):
            rval.append(member)
    return rval


def symtab_struct_declaration(struct_declaration):
    """
    :param struct_declaration: list
    :return: [(str, CType),...]
    """
    rval = []
    storage_class_specifier, type_qualifier, c_type = \
        symtab_declaration_specifiers(struct_declaration[1])
    if type_qualifier == 'const':
        c_type = deepcopy(c_type)
        c_type.is_const[-1] = True
    for declarator in struct_declaration[2][1:]:
        if declarator != ',':
            rval.append(
                    (get_IDENTIFER(declarator), symtab_declarator(declarator, c_type))  # this is a tuple
            )
    return rval


def symtab_enum_specifier(enum_specifier):
    raise Exception('Not support enum')


def symtab_declaration_specifiers(declaration_specifiers):
    storage_class_specifier = None
    c_type = None
    type_qualifier = None
    for child in declaration_specifiers[1:]:
        if child[0] == "type_specifier":
            c_type = symtab_type_specifier(child)
        elif child[0] == "storage_class_specifier":
            storage_class_specifier = child[1]
        elif child[0] == 'type_qualifier':
            type_qualifier = child[1]
    return storage_class_specifier, type_qualifier, c_type


def symtab_declaration(declaration, context):
    """
    :type declaration: list[list]
    :type context: Context
    :return: None
    """
    storage_class_specifier, type_qualifier, c_type = \
        symtab_declaration_specifiers(declaration[1])  # type:
    if type_qualifier == 'const':
        c_type = deepcopy(c_type)
        c_type.is_const[-1] = True
    if storage_class_specifier == 'typedef':
        if children_are(declaration,
                        ['declaration_specifiers',
                         'init_declarator_list', ';']):
            for init_declarator in declaration[2][1:]:
                if init_declarator != ';':
                    if children_are(init_declarator, ['declarator']):
                        name = get_IDENTIFER(init_declarator[1])
                        if name in c_types:
                            raise Exception('Redefine ' + name)
                        c_type = symtab_declarator(init_declarator[1], c_type)
                        if c_type.type == 'Incomplete':
                            raise Exception('Typedef Incomplete type as ' + name)
                        print 'Add to type record:', name, ':', c_type
                        c_types[name] = c_type
                        return
                    else:
                        raise Exception("Initialization is not permit after typedef.")
    elif storage_class_specifier == 'static' \
            or storage_class_specifier == 'extern':
        c_type = deepcopy(c_type)  # type: CType
        c_type.storage_class = storage_class_specifier

    if children_are(declaration,
                    ['declaration_specifiers',
                     'init_declarator_list', ';']):
        symtab_init_declarator_list(declaration[2], c_type, context)


def symtab_init_declarator_list(init_declarator_list, c_type, context):
    """
    :type init_declarator_list: list[list]
    :type c_type: CType
    :type context: Context
    :return: None
    """
    for init_declarator in init_declarator_list[1:]:
        if init_declarator != ',':
            if children_are(init_declarator, ['declarator']):
                context.local[get_IDENTIFER(init_declarator[1])] =\
                    symtab_declarator(init_declarator[1], c_type)
            else:
                raise Exception('Not support initializer in declarator')


def symtab_declarator(declarator, c_type):
    """
    :type declarator:
    :type c_type: CType
    :return: CType
    """
    if children_are(declarator, ['direct_declarator']):
        return symtab_direct_declarator(declarator[1], c_type)
    elif children_are(declarator, ['pointer', 'direct_declarator']):
        return symtab_direct_declarator(declarator[2], symtab_pointer(declarator[1], c_type))


def symtab_pointer(poiner, c_type):
    """
    :type poiner:
    :type c_type: CType
    :return: CType
    """
    c_type = deepcopy(c_type)
    for child in poiner[1:]:
        if child == '*':
            c_type.is_const.append(False)
        elif child == 'const':
            c_type.is_const[-1] = True
    return c_type


def symtab_direct_declarator(direct_declarator, c_type):
    """
    :type direct_declarator:
    :type c_type: CType
    :return: CType
    """
    if children_are(direct_declarator, ['(', 'declarator', ')']):
        return symtab_declarator(
                direct_declarator[2],
                c_type)
    elif children_are(direct_declarator, ['direct_declarator', '(', 'parameter_type_list', ')']):
        return symtab_direct_declarator(
                direct_declarator[1],
                FuncType(
                        c_type,
                        parameter_list=symtab_parameter_type_list(direct_declarator[3]),
                        parameter_list_is_extendable=(len(direct_declarator[3]) == 4)
                ))
    elif children_are(direct_declarator, ['direct_declarator', '(', ')']):
        return symtab_direct_declarator(
                direct_declarator[1], FuncType(c_type))
    elif children_are(direct_declarator, ['direct_declarator', '[', 'constant_expression', ']']):
        return symtab_direct_declarator(
                direct_declarator[1],
                ArrayType(
                        c_type,
                        symtab_constant_expression(direct_declarator[3])
                )
        )
    elif children_are(direct_declarator, ['direct_declarator', '[', ']']):
        c_type = deepcopy(c_type)
        c_type.is_const.append(False)
        return symtab_direct_declarator(
                direct_declarator[1],
                c_type
        )
    elif len(direct_declarator) == 2:
        return c_type


def symtab_constant_expression(constant_expression):
    """
    :type constant_expression: list
    :return: int
    """
    if constant_expression[1][0] == 'primary_expression' \
            and constant_expression[1][1][0] == 'constant':
        return int(constant_expression[1][1][1][0])
    else:
        raise Exception('Just support immediate number.')


def symtab_parameter_type_list(parameter_type_list):
    """
    :param parameter_type_list:
    :return:list(('identifier', CType)),[('id',CType),...]
    """
    return symtab_parameter_list(parameter_type_list[1])


def symtab_parameter_list(parameter_list):
    """
    :param parameter_list:
    :return: list(('identifier', CType)),[('id',CType),...]
    """
    rval = []
    for child in parameter_list[1:]:
        if child[0] == 'parameter_declaration':
            rval.append(symtab_parameter_declaration(child))
    return rval


def symtab_parameter_declaration(parameter_declaration):
    """
    :type parameter_declaration: list
    :return: tuple('id',CType)
    """
    storage_class_specifier, type_qualifier, c_type = \
        symtab_declaration_specifiers(parameter_declaration[1])
    if storage_class_specifier is not None:
        raise Exception('Storage class specifier ' +
                        storage_class_specifier +
                        'is not permitted in parameter list')
    if type_qualifier == 'const':
        c_type = deepcopy(c_type)
        c_type.is_const[-1] = True
    if children_are(parameter_declaration, ['declaration_specifiers']):
        return '', c_type
    elif children_are(parameter_declaration, ['declaration_specifiers', 'declarator']):
        return get_IDENTIFER(parameter_declaration[2]), \
               symtab_declarator(parameter_declaration[2], c_type)
    elif children_are(parameter_declaration, ['declaration_specifiers', 'abstract_declarator']):
        raise Exception("Not support abstract_declarator, parameter must be assigned to an identifier")

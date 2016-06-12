#!/usr/bin/python
from public.ZCCglobal import CType, FuncType, StructType, UnionType, \
    EnumType, ArrayType, Context, TreeNode, LiteralType, error
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
}


def children_are(ast, children):
    if len(ast) != len(children) + 1:
        return False
    for i in xrange(0, len(children)):
        if isinstance(ast[1 + i], str):
            if ast[1 + i] != children[i]:
                return False
        else:
            if children[i] == 'expression':
                if ast[1 + i][0] not in expression_handler:
                    return False
            else:
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
            return ast[1][1]
            # if ast[0] == 'init_declarator':
            #     return get_IDENTIFER(ast[1])


def symtab_type_specifier(type_specifier):
    child_name = type_specifier[1][0]
    if child_name == 'void':
        return deepcopy(c_types['void'])

    elif child_name == 'float':
        return deepcopy(c_types['float'])

    elif child_name == 'double':
        return deepcopy(c_types['double'])

    elif child_name == 'integer_type':
        return deepcopy(symtab_integer_type(type_specifier[1]))

    elif child_name == 'struct_or_union_specifier':
        return deepcopy(symtab_struct_or_union_specifier(type_specifier[1]))

    elif child_name == 'enum_specifier':
        return deepcopy(symtab_enum_specifier(type_specifier[1]))

    else:
        return deepcopy(c_types[type_specifier[1]])


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
                name = get_IDENTIFER(init_declarator[1])
                if name in context.local:
                    raise Exception('Redefine ' + name)
                context.local[name] = symtab_declarator(init_declarator[1], c_type)
            else:
                raise Exception('Not support initializer in declarator now')


def symtab_declarator(declarator, c_type):
    """
    :type declarator:
    :type c_type: CType
    :return: CType
    """
    c_type = deepcopy(c_type)
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
            and constant_expression[1][1][0] == 'INTEGER':
        return int(constant_expression[1][1][1])
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
        c_type.is_const[-1] = True
    if children_are(parameter_declaration, ['declaration_specifiers']):
        return '', c_type
    elif children_are(parameter_declaration, ['declaration_specifiers', 'declarator']):
        return get_IDENTIFER(parameter_declaration[2]), \
               symtab_declarator(parameter_declaration[2], c_type)
    elif children_are(parameter_declaration, ['declaration_specifiers', 'abstract_declarator']):
        raise Exception("Not support abstract_declarator, parameter must be assigned an identifier")


def symtab_function_definition(function_definition, context):
    """
    :type function_definition: list[list]
    :type context: Context
    :return:
    """
    storage_class_specifier, type_qualifier, c_type = \
        symtab_declaration_specifiers(function_definition[1])
    if storage_class_specifier == 'typedef':
        raise Exception('Function definition cannot be typedef')
    if storage_class_specifier == 'static':
        c_type.storage_class = storage_class_specifier
    if type_qualifier == 'const':
        c_type.is_const[-1] = True
    c_type = symtab_declarator(function_definition[2], c_type)
    name = get_IDENTIFER(function_definition[2])
    if not isinstance(c_type, FuncType):
        raise Exception(name + " lack parameter list")

    if name in context.local:
        old_type = context.local[name]
        if not isinstance(old_type, FuncType):
            raise Exception('Redefine ' + name)
        else:
            if not c_type == old_type:
                print_error(repr(c_type) + "is not consistent with old declaration " + repr(old_type))
            # print('We do not perform parameter check and return value check on function ' + name)
            c_type = old_type
    compound_statement = c_type.compound_statement = \
        TreeNode(function_definition[3],
                 context=Context(outer_context=context, func_type=c_type))
    context.local[name] = c_type
    symtab_compound_statement(compound_statement, compound_statement.context)


def symtab_compound_statement(compound_statement, context):
    if children_are(compound_statement, ['{', 'statement_list', '}']):
        symtab_statement_list(compound_statement[2], context)
    elif children_are(compound_statement, ['{', 'declaration_list', '}']):
        symtab_declaration_list(compound_statement[2], context)
    elif children_are(compound_statement, ['{', 'declaration_list', 'statement_list', '}']):
        symtab_declaration_list(compound_statement[2], context)
        symtab_statement_list(compound_statement[3], context)


#

def symtab_declaration_list(declaration_list, context):
    for declaration in declaration_list[1:]:
        symtab_declaration(declaration, context)


def symtab_statement_list(statement_list, context):
    """
    :type statement_list: list[list]
    :type context: Context
    :return: None
    """
    for statement in statement_list[1:]:
        symtab_statement(statement, context)


def symtab_statement(statement, context):
    """
    :type statement: list[list]
    :type context: Context
    :return: None
    """
    if statement[1][0] == 'labeled_statement':
        raise Exception('Not support label.')
    if statement[1][0] == 'compound_statment':
        compound_statement = \
            TreeNode(statement[1],
                     context=Context(outer_context=context))
        symtab_compound_statement(compound_statement, compound_statement.context)

    if statement[1][0] == 'expression_statement':
        symtab_expression_statement(statement[1], context)
    if statement[1][0] == 'selection_statement':
        symtab_selection_statement(statement[1], context)
    if statement[1][0] == 'iteration_statement':
        symtab_iteration_statement(statement[1], context)
    if statement[1][0] == 'jump_statement':
        symtab_jump_statement(statement[1], context)


def symtab_expression_statement(expression_statement, context):
    if children_are(expression_statement, ['expression', ';']):
        symtab_expression(expression_statement[1], context)


def symtab_selection_statement(selection_statement, context):
    if children_are(selection_statement, ['SWITCH', '(', 'expression', ')', 'statement']):
        raise Exception('Not support switch statement')

    if len(selection_statement) >= 6:
        expression_rtype_check(selection_statement[3], context, 'bool')
        symtab_statement(selection_statement[5], context)

    if children_are(selection_statement, ['if', '(', 'expression', ')', 'statement', 'else', 'statement']):
        symtab_statement(selection_statement[7], context)


def symtab_iteration_statement(iteration_statement, context):
    if children_are(iteration_statement, ['while', '(', 'expression', ')', 'statement']):
        expression_rtype_check(iteration_statement[3], context, 'bool')
        symtab_statement(iteration_statement[5], context)

    if children_are(iteration_statement, ['do', 'statement', 'while', '(', 'expression', ')', ';']):
        symtab_statement(iteration_statement[2], context)
        expression_rtype_check(iteration_statement[5], context, 'bool')

    if children_are(iteration_statement,
                    ['for', '(', 'expression_statement', 'expression_statement', ')', 'statement']):
        symtab_expression_statement(iteration_statement[3], context)
        if iteration_statement[4][1] != ';':
            expression_rtype_check(iteration_statement[4][1], context, 'bool')
        symtab_statement(iteration_statement[6], context)

    if children_are(iteration_statement,
                    ['for', '(', 'expression_statement', 'expression_statement', 'expression', ')', 'statement']):
        symtab_expression_statement(iteration_statement[3], context)
        if iteration_statement[4][1] != ';':
            expression_rtype_check(iteration_statement[4][1], context, 'bool')
        symtab_expression(iteration_statement[5], context)
        symtab_statement(iteration_statement[7], context)


def symtab_jump_statement(jump_statement, context):
    """
    :type jump_statement: list[list]
    :type context: Context
    """
    if jump_statement[1][0] == 'continue':
        pass
    elif jump_statement[1][0] == 'break':
        pass
    elif children_are(jump_statement, ['return', 'expression', ';']):
        c_type = symtab_expression(jump_statement[2], context)
        r_type = context.get_return_type()
        if r_type is None:
            raise Exception('return statement out of a function')
        if not c_type == r_type:
            print_error(repr(c_type) + ' is not consistant with the function return type ' + repr(r_type))
    elif children_are(jump_statement, ['return', ';']):
        c_type = c_types['void']
        r_type = context.get_return_type()
        if r_type is None:
            raise Exception('return statement out of a function')
        if not c_type == r_type:
            print_error(repr(c_type) + ' is not consistant with the function return type ' + repr(r_type))
    else:
        raise Exception('Unknow child list for jump_statement')


def expression_rtype_check(expression, context, type_name):
    """
    :type expression: list[list]
    :type context: Context
    :type type_name: str
    :rtype: CType
    """
    rtype = symtab_expression(expression, context)
    if type_name == 'bool':
        right_type = rtype.is_integer()
    elif type_name == 'integer':
        right_type = rtype.is_integer()
    elif type_name == 'number':
        right_type = rtype.is_number()
    elif type_name == 'callable':
        if not isinstance(rtype, FuncType) or \
                (rtype.pointer_count() != 0 and rtype.pointer_count() != 1):
            print_error(repr(rtype) + " is not callable.")
        return rtype
    else:
        raise Exception('Illegal type in expression_rtype_check')
    if not right_type:
        print_error(repr(rtype) + ' is not or cannot be recognized as ' + type_name)
    return rtype


expression_handler = {}


def symtab_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    if expression[0] == 'expression':
        symtab_expression(expression[1], context)
        return symtab_expression(expression[3], context)
    else:
        return expression_handler[expression[0]](expression, context)


# def symtab_constant(expression, context):
#     """
#     :type expression: list
#     :type context: Context
#     :rtype: CType
#     """
#     if expression[1][0] == "'":
#         val = ord(eval(expression[1]))
#     else:
#         val = eval(expression[1])
#     return LiteralType(val)


def symtab_primary_expression(expression, context):
    """
    :type expression: list
    :type context: Context
    :rtype: CType
    """
    if children_are(expression, ['(', 'expression', ')']):
        return symtab_expression(expression[2], context)
    elif children_are(expression, ['IDENTIFIER']):
        name = expression[1][1]
        c_type = context.get_type_by_id(name)
        if c_type is None:
            print_error('Unknown identifier ' + name)
            # todo: type_error check
        return c_type
    elif children_are(expression, ['INTEGER']):
        c_type = LiteralType(eval(expression[1][1]))
        # context.add_literal(expression[1][1], c_type)
        return c_type
    elif children_are(expression, ['DOUBLE']):
        c_type = LiteralType(eval(expression[1][1]))
        context.add_literal(expression[1][1], c_type)
        return c_type
    elif children_are(expression, ['STRING']):
        c_type = LiteralType(eval(expression[1][1]))
        context.add_literal(expression[1][1], c_type)
        return c_type
        # elif children_are(expression, ['constant']):
        #     # return symtab_constant(expression[1], context)
        # elif expression[1][0] == '"':
        #     val = eval(expression[1])
        #     return LiteralType(val)
        # else:
        #     name = expression[1]
        #     c_type = context.get_type_by_id(name)
        #     if c_type is None:
        #         print_error('Unknown identifier ' + name)
        #     return c_type


def symtab_argument_expression_list(argument_expression_list, context, func):
    """
    :type argument_expression_list: list[str]
    :type context: Context
    :type func: FuncType
    """
    for argument_expression in argument_expression_list[1:]:
        if argument_expression != ',':
            symtab_expression(argument_expression, context)
    # todo: parameter type check
    pass


def symtab_postfix_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    if children_are(expression, ['expression', '[', 'expression', ']']):
        index = expression_rtype_check(expression[3], context, 'integer')
        base = symtab_expression(expression[1], context)
        if base.pointer_count() > 0:
            rtype = deepcopy(base)
            rtype.is_const.pop()
            return rtype
        if isinstance(base, ArrayType):
            return base.member_type
        print_error(repr(base) + " is not pointer or array, cannot apply [] operation.")
        return c_types['void']
    elif children_are(expression, ['expression', '(', ')']):
        c_type = expression_rtype_check(expression[1], context, 'callable')
        if not isinstance(c_type, FuncType):
            return c_types['void']
        symtab_argument_expression_list(['argument_expression_list'], context, c_type)
        return c_type.return_type

    elif children_are(expression, ['expression', '(', 'argument_expression_list', ')']):
        c_type = expression_rtype_check(expression[1], context, 'callable')
        if not isinstance(c_type, FuncType):
            return c_types['void']
        symtab_argument_expression_list(expression[3], context, c_type)
        return c_type.return_type

    elif children_are(expression, ['expression', '.', 'IDENTIFIER']):
        pass
    elif children_are(expression, ['expression', '->', 'IDENTIFIER']):
        pass
    elif children_are(expression, ['expression', '++']):
        pass
    elif children_are(expression, ['expression', '--']):
        pass
    # todo
    pass


def symtab_unary_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    if children_are(expression, ["unary_operator", 'expression']):
        c_type = symtab_expression(expression[2], context)
        return symtab_unary_operator(expression[1], context, c_type)
    # todo
    pass

def symtab_unary_operator(unary_operator, context, c_type):
    """
    :type expression: list[str]
    :type context: Context
    :type c_type: CType
    :rtype: CType
    """
    if unary_operator[1] == '*':
        if c_type.pointer_count() > 0:
            rtype = deepcopy(c_type)
            rtype.is_const.pop()
            return rtype
        if isinstance(c_type, ArrayType):
            return c_type.member_type
        print_error(repr(c_type) + " is not pointer or array, cannot apply [] operation.")
        return c_types['void']
    elif unary_operator[1] == '&':
        rtype = deepcopy(c_type)
        rtype.is_const.append(True)
        return rtype
    # todo

def symtab_cast_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    # todo
    pass


def symtab_multiplicative_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_number_operation_expression(expression, context)


def symtab_additive_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_number_operation_expression(expression, context)


def symtab_shift_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_number_operation_expression(expression, context)


def symtab_relational_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_number_operation_expression(expression, context)


def symtab_equality_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_number_operation_expression(expression, context)


def symtab_number_operation_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    c_type1 = expression_rtype_check(expression[1], context, 'number')
    c_type2 = expression_rtype_check(expression[3], context, 'number')
    if c_type1.type == 'double' and c_type1.pointer_count() == 0 \
            or c_type2.type == 'double' and c_type2.pointer_count() == 0:
        return c_types['double']
    elif c_type1.type == 'float' and c_type1.pointer_count() == 0 \
            or c_type2.type == 'float' and c_type2.pointer_count() == 0:
        return c_types['float']
    else:
        return c_types['int']


def symtab_and_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_integer_operation_expression(expression, context)


def symtab_exclusive_or_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_integer_operation_expression(expression, context)


def symtab_inclusive_or_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_integer_operation_expression(expression, context)


def symtab_integer_operation_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    expression_rtype_check(expression[1], context, 'integer')
    expression_rtype_check(expression[3], context, 'integer')
    return c_types['int']


def symtab_logical_and_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_bool_operation_expression(expression, context)


def symtab_logical_or_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    return symtab_bool_operation_expression(expression, context)


def symtab_bool_operation_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    expression_rtype_check(expression[1], context, 'bool')
    expression_rtype_check(expression[3], context, 'bool')
    return c_types['int']


def symtab_conditional_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    expression_rtype_check(expression[1], context, 'bool')
    c_type1 = symtab_expression(expression[3], context)
    c_type2 = symtab_expression(expression[5], context)
    if c_type1 != c_type2:
        print_error("'%s' and '%s' are not the same type in condition expression."
                    % (repr(c_type1), repr(c_type2)))
    return c_type1


def symtab_assignment_expression(expression, context):
    """
    :type expression: list[list]
    :type context: Context
    :rtype: CType
    """
    if expression[2][1] in ['*=', '/=', '+=', '-=']:
        expression_rtype_check(expression[3], context, 'number')
        return expression_rtype_check(expression[1], context, 'number')
    elif expression[2][1] in ['%=', '<<=', '>>=', '&=', '^=', '|=']:
        expression_rtype_check(expression[3], context, 'integer')
        return expression_rtype_check(expression[1], context, 'integer')
    elif expression[2][1] == '=':
        c_type1 = symtab_expression(expression[1], context)
        c_type2 = symtab_expression(expression[3], context)
        if (not c_type1.is_number() or not c_type2.is_number()) and \
                not c_type1 == c_type2:
            print_error(repr(c_type2) + ' cannot be assigned to ' + repr(c_type1))
        return c_type1


expression_handler = {'primary_expression': symtab_primary_expression,
                      'postfix_expression': symtab_postfix_expression,
                      'unary_expression': symtab_unary_expression,
                      'cast_expression': symtab_cast_expression,
                      'multiplicative_expression': symtab_multiplicative_expression,
                      'additive_expression': symtab_additive_expression,
                      'shift_expression': symtab_shift_expression,
                      'relational_expression': symtab_relational_expression,
                      'equality_expression': symtab_equality_expression,
                      'and_expression': symtab_and_expression,
                      'exclusive_or_expression': symtab_exclusive_or_expression,
                      'inclusive_or_expression': symtab_inclusive_or_expression,
                      'logical_and_expression': symtab_logical_and_expression,
                      'logical_or_expression': symtab_logical_or_expression,
                      'conditional_expression': symtab_conditional_expression,
                      'assignment_expression': symtab_assignment_expression,
                      'expression': symtab_expression}


def print_error(error_info):
    print error_info
    error[0] = True

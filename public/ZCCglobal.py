#!/usr/bin/python
# -*- coding: utf-8 -*-


class CType(object):
    def __init__(self, type_name, size=0, **kwargs):
        """
        :type type_name:str
        :type size: int
        :type kwargs: dict
        :return: None
        """
        # "int","char","double","float","long","short","void",
        # "struct","union","enum","function", "array"
        # 'Incomplete'
        self.type = type_name  # type: str
        # sizeof
        self.size = size  # type: int
        self.is_const = [False]  # type: list[bool]
        self.storage_class = None  # type: str
        # "static", "extern"

        for key in kwargs:
            self.__setattr__(key, kwargs[key])

    def pointer_count(self):
        """
        :return: int
        """
        return len(self.is_const) - 1

    def Size(self):
        """
        Must get size by this function!!!
        :rtype: int
        """
        if self.pointer_count() == 0:
            return self.size
        else:
            return 4

    def __repr__(self):
        return self.__add_star__(self.type)

    def __add_star__(self, base_type_repr):
        rval = base_type_repr
        if self.storage_class:
            rval = self.storage_class + " " + rval
        for i in xrange(0, len(self.is_const)):
            if i > 0:
                rval += " *"
            if self.is_const[i]:
                rval += " const"
        return rval

    def __eq__(self, other):
        """
        :type self: CType
        :type other: CType
        :rtype: bool
        """
        if self.pointer_count() != other.pointer_count():
            return False
        if self.type != other.type:
            return False
        return True

    def is_integer(self):
        """
        :rtype: bool
        """
        return self.pointer_count() > 0 or self.type in \
                                           ['char', 'short', 'int', 'long', 'long long',
                                            'signed char', 'signed short', 'signed int', 'signed long',
                                            'signed long long',
                                            'unsigned char', 'unsigned short', 'unsigned int', 'unsigned long',
                                            'unsigned long long']

    def is_number(self):
        """
        :rtype: bool
        """
        return self.pointer_count() > 0 or self.type in \
                                           ['char', 'short', 'int', 'long', 'long long',
                                            'signed char', 'signed short', 'signed int', 'signed long',
                                            'signed long long',
                                            'unsigned char', 'unsigned short', 'unsigned int', 'unsigned long',
                                            'unsigned long long',
                                            'float', 'double']


class StructType(CType):
    def __init__(self, members=list()):
        """
        :type members: list[(str,CType)]
        :return:
        """
        CType.__init__(self, 'struct')
        self.members = {}  # type: dict[str,CType]
        self.offset = {}
        self.size = 0
        for member in members:
            self.members[member[0]] = member[1]
            self.offset[member[0]] = self.size
            self.size += member[1].size
            self.size = ((self.size - 1) / 4 + 1) * 4

    def __repr__(self):
        return self.__add_star__('struct ' + repr(self.members))

    def __eq__(self, other):
        return CType.__eq__(self, other) and has_same_members(self, other)


class UnionType(CType):
    def __init__(self, members=list()):
        """
        :type members: list[(str,CType)]
        :return:
        """
        CType.__init__(self, 'union')
        self.members = {}  # type: dict[str,CType]
        self.size = 0  # type: int
        for member in members:
            self.members[member[0]] = member[1]
            if member[1].size > self.size:
                self.size = member[1].size

    def __repr__(self):

        return self.__add_star__('union ' + repr(self.members))

    def __eq__(self, other):
        return CType.__eq__(self, other) and has_same_members(self, other)


class EnumType(CType):
    def __init__(self, values):
        """
        :type values: dict[(str,int)]
        :return:
        """
        CType.__init__(self, 'enum')
        self.values = values
        self.size = 4

    def __repr__(self):
        return self.__add_star__('enum ' + repr(self.values))

    def __eq__(self, other):
        raise Exception('Not support enum')


class FuncType(CType):
    def __init__(self, return_type,
                 parameter_list=list(),
                 parameter_list_is_extendable=False,
                 compound_statement=None):
        """
        :type return_type: CType
        :type parameter_list: list[(str,CType)]
        :type parameter_list_is_extendable: bool
        :type compound_statement: TreeNode
        """
        CType.__init__(self, 'function')
        self.return_type = return_type  # type: CType
        self.storage_class = return_type.storage_class
        return_type.storage_class = None
        self.parameter_list = parameter_list  # type: list[(str,CType)]
        self.parameter_list_is_extendable = \
            parameter_list_is_extendable  # type: bool
        self.compound_statement = compound_statement  # type: TreeNode

    def __repr__(self):
        rval = repr(self.return_type) + " function("
        for parameter in self.parameter_list:
            rval += repr(parameter[1]) + ' ' + parameter[0] + ','
        if self.parameter_list_is_extendable:
            rval += '...'
        rval += ')'
        if self.compound_statement is not None:
            rval += repr(self.compound_statement.context)
        return self.__add_star__(rval)

    def __eq__(self, other):
        """
        :type other: FuncType
        :rtype: bool
        """
        if self.type != other.type:
            return False
        if self.pointer_count() + other.pointer_count() > 1:
            if self.pointer_count() != other.pointer_count():
                return False
        if not self.return_type == other.return_type:
            return False
        if not self.parameter_list_is_extendable == other.parameter_list_is_extendable:
            return False
        if not len(self.parameter_list) == len(other.parameter_list):
            return False
        for i in xrange(len(self.parameter_list)):
            if not self.parameter_list[i][1] == other.parameter_list[i][1]:
                return False
        return True


class ArrayType(CType):
    def __init__(self, c_type, length):
        """
        :type c_type: CType
        :type length: int
        :return:
        """
        CType.__init__(self, 'array', size=length * c_type.Size())
        self.length = length
        self.member_type = c_type
        self.storage_class = c_type.storage_class
        c_type.storage_class = None

    def __repr__(self):
        return self.__add_star__(repr(self.member_type) + "[%d]" % self.length)

    def __eq__(self, other):
        """
        :type other: ArrayType
        :rtype: bool
        """
        if not CType.__eq__(self, other):
            return False
        return self.length == other.length and \
               self.member_type == other.member_type


class LiteralType(CType):
    def __init__(self, val):
        """
        :type c_type: CType
        :return:
        """
        CType.__init__(self, '')
        self.val = val
        if isinstance(val, str):
            self.type = 'char'
            self.size = 1
            self.is_const = [True, False]
        elif isinstance(val, int):
            self.type = 'int'
            self.size = 4
            self.is_const = [True]
        elif isinstance(val, float):
            self.type = 'double'
            self.size = 8
            self.is_const = [True]


class Context:
    outer_context = None  # type: Context
    func_type = None  # type: FuncType
    local = None  # type: dict[str,CType]

    def __init__(self, outer_context=None, func_type=None):
        self.outer_context = outer_context  # type: Context
        self.func_type = func_type  # type: FuncType
        self.local = {}

    def __repr__(self):
        return " local: " + repr(self.local)

    def get_return_type(self):
        """
        :rtype: CType
        """
        if self.func_type is None:
            if self.outer_context is None:
                return  # global_context has no return type
            else:
                return self.outer_context.get_return_type()
        else:
            return self.func_type.return_type

    def get_type_by_id(self, identifier):
        """
        :type identifier: str
        :rtype: CType
        """
        if identifier in self.local:
            return self.local[identifier]
        if self.func_type is not None:
            for parameter in self.func_type.parameter_list:
                if identifier == parameter[0]:
                    return parameter[1]
        if self.outer_context is not None:
            return self.outer_context.get_type_by_id(identifier)
        return None  # if not find

    def add_literal(self, name, literal):
        """
        :type name: str
        :type literal: LiteralType
        """
        context = self
        while context.outer_context is not None:
            context = context.outer_context
        context.literal[name] = literal


class GlobalContext(Context):
    def __init__(self):
        Context.__init__(self)
        self.literal = {}  # type: dict[str,LiteralType]

    def __repr__(self):
        return 'literals:' + repr(self.literal) + '\n' + Context.__repr__(self)


global_context = GlobalContext()
error = [False]


class TreeNode(list):
    def __init__(self, lineno=-1):
        """
        :return:
        """
        self.lineno = lineno  # type: int
        # self.ast = self  # type: # list[list]


# class LeafNode(str):
#     def __init__(self, lineno=-1):
#         """
#         :return:
#         """
#         self.lineno = lineno  # type: int


# self.ast = ast  # type: list[list]
#     for key in kwargs:
#         self.__setattr__(key, kwargs[key])
#
# def __getitem__(self, item):
#     return self.ast.__getitem__(item)
#
# def __setitem__(self, key, value):
#     self.ast.__setitem__(key, value)
#
# def __len__(self):
#     return self.ast.__len__()


def has_same_members(struct_type1, struct_type2):
    """
    :type struct_type1: StructType
    :type struct_type2: StructType
    :rtype: bool
    """
    for member in struct_type1.members:
        if member not in struct_type2.members \
                or not struct_type1.members[member] == struct_type2.members[member]:
            return False

    for member in struct_type2.members:
        if member not in struct_type1.members \
                or not struct_type2.members[member] == \
                        struct_type1.members[member]:
            return False
    return True

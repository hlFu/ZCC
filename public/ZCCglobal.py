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

    # def __repr__(self):
    #     return self.type
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


class StructType(CType):
    def __init__(self, members=[]):
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

    def __repr__(self):
        return self.__add_star__('struct ' + repr(self.members))


class UnionType(CType):
    def __init__(self, members=[]):
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
        self.return_type = return_type
        self.storage_class = return_type.storage_class
        return_type.storage_class = None
        self.parameter_list = parameter_list
        self.parameter_list_is_extendable = \
            parameter_list_is_extendable  # printf(char* format,...)
        self.compound_statement = compound_statement

    def __repr__(self):
        rval = repr(self.return_type) + " function("
        for parameter in self.parameter_list:
            rval += repr(parameter[1]) + ' ' + parameter[0] + ','
        if self.parameter_list_is_extendable:
            rval += '...'
        rval += ')'
        rval += repr(self.compound_statement.context)
        return self.__add_star__(rval)


class ArrayType(CType):
    def __init__(self, c_type, length):
        """
        :type c_type: CType
        :type length: int
        :return:
        """
        CType.__init__(self, 'array', size=length * c_type.size)
        self.length = length
        self.member_type = c_type
        self.storage_class = c_type.storage_class
        c_type.storage_class = None

    def __repr__(self):
        return self.__add_star__(repr(self.member_type) + "[%d]" % self.length)


class Context:
    outer_context = None  # type: Context
    func_type = None  # type: FuncType
    local = None  # type: dict[str,CType]

    def __init__(self, outer_context=None, func_type=None):
        self.outer_context = outer_context
        self.func_type = func_type
        self.local = {}

    def __repr__(self):
        return " local: " + repr(self.local)


global_context = Context()
error = False

class TreeNode(object):
    def __init__(self, ast, **kwargs):
        """
        :type ast: list[list]
        :return:
        """
        self.ast = ast  # type: list[list]
        for key in kwargs:
            self.__setattr__(key, kwargs[key])

    def __getitem__(self, item):
        return self.ast.__getitem__(item)

    def __setitem__(self, key, value):
        self.ast.__setitem__(key, value)

    def __len__(self):
        return self.ast.__len__()

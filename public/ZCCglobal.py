# common structure put here
from const import *


# class TreeNode(object):
#     kind = str()  #
#     children = list()  # TreeNode
#     attr = Attr()
#
#
# class Attr(object):
#     # IDENTIFIER
#     value = str()  # i,j
#     type = Ctype()
#
#     is_global=bool()
#     is_static=bool()
#     addVariableTable=list() # compound_statment
#
# class Struct(object):
#     member = {"IDENTIFIER":(ctype, offset = int())}

# class CType(object):
#     def __init__(self, c_base_type):
#         """
#         @type c_base_type: CBaseType
#         """
#         self.c_base_type = c_base_type
#         self.is_const = [c_base_type.is_const]
#         self.storage_class = None
#
#     def pointer_count(self):
#         """
#         :return: int
#         """
#         return len(self.is_const) - 1
#


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
        self.members = {}
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
    """
    :type return_type: CType
    :type parameter_list: list[(str,CType)]
    :type parameter_list_is_extendable: bool
    """

    def __init__(self, return_type,
                 parameter_list=list(),
                 parameter_list_is_extendable=False):
        CType.__init__(self, 'function')
        self.return_type = return_type
        self.parameter_list = parameter_list
        self.parameter_list_is_extendable = \
            parameter_list_is_extendable  # printf(char* format,...)

    def __repr__(self):
        rval = repr(self.return_type) + " function("
        for parameter in self.parameter_list:
            rval += repr(parameter[1]) + ' ' + parameter[0] + ','
        if self.parameter_list_is_extendable:
            rval += '...'
        rval += ')'
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

    def __repr__(self):
        return self.__add_star__(repr(self.member_type) + "[%d]" % self.length)


class Context:
    outer_context = None  # type: Context
    func_type = None  # type: FuncType
    local = {}  # type: dict[str,CType]

    def __init__(self, outer_context=None, func_type=None):
        self.outer_context = outer_context
        self.func_type = func_type

    def __repr__(self):
        return repr(self.func_type) + " local: " + repr(self.local)

global_context = Context()
current_context = global_context

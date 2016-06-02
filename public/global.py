#common structure put here
from const import *

class TreeNode(object):
    kind = str()  #
    children = list()  # TreeNode
    attr = Attr()


class Attr(object):
    # IDENTIFIER
    value = str()  # i,j
    type = Ctype()

    is_global=bool()
    is_static=bool()
    addVariableTable=list() # compound_statment

class Struct(object):
    member = {"IDENTIFIER":(ctype, offset = int())}

class Ctype(object):
    def __init__(self):
        self.type = str()
        # "int","char","double","float","long","short","void",
        # "struct","union","enum","function"
        self.is_signed = bool()
        self.is_const = [False]  #
        self.pointer_count = lambda: (len(self.is_const) - 1)
        self.struct = Struct()
        self.size = int()

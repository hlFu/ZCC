# coding=utf-8
# produce machine code
import sys
sys.path.append('c:\\zcc\\zcc')
from public.ZCCglobal import *
from utility import utility
from copy import deepcopy
from data import Data


class generator:

    def __init__(self):
        # asm output list
        self.asm = []
        self.tools = utility(self)
        self.expression_handler = {
            'primary_expression': self.gen_primary_expression,
            'postfix_expression': self.gen_postfix_expression,
            'unary_expression': self.gen_unary_expression,
            'cast_expression': self.gen_cast_expression,
            'multiplicative_expression': self.gen_multiplicative_expression,
            'additive_expression': self.gen_additive_expression,
            'shift_expression': self.gen_shift_expression,
            'relational_expression': self.gen_relational_expression,
            'equality_expression': self.gen_equality_expression,
            'and_expression': self.gen_and_expression,
            'exclusive_or_expression': self.gen_exclusive_or_expression,
            'inclusive_or_expression': self.gen_inclusive_or_expression,
            'logical_and_expression': self.gen_logical_and_expression,
            'logical_or_expression': self.gen_logical_or_expression,
            'conditional_expression': self.gen_conditional_expression,
            'assignment_expression': self.gen_assignment_expression,
            'expression': self.gen_expression}

    def generate(self):
        ###########################################
        # 程序结构
        # self.tools.globalInitialize()                  :初始化环境
        #   for key in global_context.local:            :找到每个函数
        #       self.tools.newFunc(funcName)            :初始化函数
        #       ...                                     :解析树
        #       ...                                     :调用self.tools函数，完成翻译
        #       self.tools.ret(funcName,returnValue)    :退出函数体
        # self.tools.end()                               :退出程序
        ###########################################

        # 一个例子
        self.tools.globalInitialize()
        for funcName in global_context.local:
            value = global_context.local[funcName]
            if(value.type == 'function'):
                if global_context.local[
                        funcName].compound_statement is not None:
                    # self.tools.newFunc(funcName)
                    self.gen_compound_statement(
                        global_context.local[funcName].compound_statement)
                    # self.tools.endFunc()
        self.tools.end()

    def output(self, fileName):
        with open(fileName, 'w') as out:
            for line in self.asm:
                out.write(line)

    def gen_statement_list(self, node):
        """
        :type node:TreeNode
        """
        for subnode in node[1:]:
            if isinstance(subnode, TreeNode):
                if subnode[0] == "statement":
                    self.gen_statement(subnode)

    def gen_statement(self, node):
        """
        :type node:TreeNode
        """
        for subnode in node[1:]:
            if isinstance(subnode, TreeNode):
                if subnode[0] == "expression_statement":
                    self.gen_expression_statement(subnode)
                elif subnode[0] == "compound_statement":
                    # self.tools.newScope(subnode.context)
                    self.gen_compound_statement(subnode)
                    # self.tools.endScope()
                elif subnode[0] == "selection_statement":
                    self.gen_selection_statement(subnode)
                elif subnode[0]=="jump_statement":
                    self.gen_jump_statement(subnode)
                elif subnode[0]=="iteration_statement":
                    self.gen_iteration_statement(subnode)

    def gen_expression_statement(self, node):
        """
        :type node:TreeNode
        :rtype :str
        """
        if isinstance(node[1],TreeNode):
            ret=self.expression_handler[node[1][0]](node[1])
        else:
            # ret=self.tools.getTrue()
            pass
        return ret

    def gen_compound_statement(self, node):
        """
        :type node:TreeNode
        """
        for subnode in node[1:]:
            if isinstance(subnode, TreeNode):
                if subnode[0] == "statement_list":
                    self.gen_statement_list(subnode)

    def gen_selection_statement(self, node):
        """
        :type node:TreeNode
        """
        # node[3]:expression
        # node[5]:statement
        # node[7]:statement
        self.expression_handler[node[3][0]](node[3])
        if node[1] == "if":
            if len(node) == 6:
                pass
            elif len(node) == 8:
                pass

    def gen_jump_statement(self,node):
        """
        :type node:TreeNode
        """
        pass

    def gen_iteration_statement(self,node):
        """
        :type node:TreeNode
        """
        pass


    def gen_additive_expression(self, node):
        """
        :type node:TreeNode
        :rtype: str
        """
        op1=self.expression_handler[node[1][0]](node[1])
        tmp=self.tools.allocateNewReg()
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3])
        if node[2]=="+":
            ret=self.tools.add(tmp,op2)
        else:
            ret=self.tools.sub(tmp,op2)
        self.tools.unlock(tmp)
        return ret

    def gen_primary_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_postfix_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_unary_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_cast_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_multiplicative_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        op1=self.expression_handler[node[1][0]](node[1])
        tmp=self.tools.allocateNewReg()
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3])
        if node[2]=="*":
            ret=self.tools.mul(tmp,op2)
        elif node[2]=="/":
            ret=self.tools.div(tmp,op2)
        self.tools.unclock(tmp)
        return ret


    def gen_shift_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        op1=self.expression_handler[node[1][0]](node[1])
        self.tools.lock(op1)
        op2=self.expression_handler[node[3][0]](node[3])
        self.tools.unlock(op1)
        ret=self.tools.add(op1,op2)

    def gen_relational_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_equality_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_and_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_exclusive_or_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_inclusive_or_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_logical_and_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_logical_or_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_conditional_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_assignment_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

    def gen_expression(self,node):
        """
        :type node:TreeNode
        :rtype: str
        """
        pass

#coding=utf-8
#produce machine code
import sys
sys.path.append('c:\\zcc\\zcc')
from public.ZCCglobal import *
from utility import utility

class generator:
    def __init__ (self):
        #asm output list
        self.asm=[]
        self.tools=utility(self)
        self.expression_handler={

        }

    def generate(self):
        ###########################################
        #程序结构
        #self.tools.globalInitialize()                  :初始化环境
        #   for key in global_context.local:            :找到每个函数
        #       self.tools.newFunc(funcName)            :初始化函数
        #       ...                                     :解析树
        #       ...                                     :调用self.tools函数，完成翻译
        #       self.tools.ret(funcName,returnValue)    :退出函数体
        #self.tools.end()                               :退出程序
        ###########################################
        
        #一个例子
        self.tools.globalInitialize()
        for funcName in global_context.local:
            value = global_context.local[funcName]
            if(value.type=='function'):
                if global_context.local[funcName].compound_statement is not None:
                    # self.tools.newFunc(global_context.local[funcName].compound_statement.context)
                    self.gen_compound_statement(global_context.local[funcName].compound_statement)
                    # self.tools.endFunc()
        self.tools.end()

    def output(self,fileName):
        with open(fileName,'w') as out:
            for line in self.asm:
                out.write(line)

    def gen_statement_list(self,node):
        """
        :type node:TreeNode
        """
        for subnode in node[1:]:
            if isinstance(subnode,TreeNode):
                if subnode[0]=="statement":
                    self.gen_statement(subnode)

    def gen_statement(self,node):
        """
        :type node:TreeNode
        """
        for subnode in node[1:]:
            if isinstance(subnode,TreeNode):
                if subnode[0]=="expression_statement":
                    self.gen_expression_statement(subnode)
                elif subnode[0]=="compound_statement":
                    # self.tools.newScope()
                    self.gen_compound_statement(subnode)
                    # self.tools.endScope()
                elif subnode[0]=="selection_statement":
                    self.gen_selection_statement(subnode)


    def gen_expression_statement(self,node):
        """
        :type node:TreeNode
        """
        pass

    def gen_compound_statement(self,node):
        """
        :type node:TreeNode
        """
        for subnode in node[1:]:
            if isinstance(subnode,TreeNode):
                if subnode[0]=="statement_list":
                    self.gen_statement_list(subnode)

    def gen_selection_statement(self,node):
        """
        :type node:TreeNode
        """
        # node[3]:expression
        # node[5]:statement
        # node[7]:statement
        if node[1]=="if":
            if len(node)==6:
                pass
            elif len(node)==8:
                pass





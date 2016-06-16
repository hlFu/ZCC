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
        self.exp2=[2**x for x in range(32)]
        print(self.exp2)
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
        self.tools.globalInitialize()
        for funcName in global_context.local:
            value = global_context.local[funcName]
            if(value.type == 'function'):
                if global_context.local[
                        funcName].compound_statement is not None:
                    self.tools.newFunc(funcName)
                    self.gen_compound_statement(
                        global_context.local[funcName].compound_statement,global_context.local[funcName].compound_statement.context)
                    self.tools.endFunc()
        self.tools.end()

    def output(self, fileName):
        with open(fileName, 'w') as out:
            for line in self.asm:
                out.write(line)

    def gen_statement_list(self, node,context):
        """
        :type node:TreeNode
        :type context:Context
        """
        for subnode in node[1:]:
            if isinstance(subnode, TreeNode):
                if subnode[0] == "statement":
                    self.gen_statement(subnode,context)


    def gen_statement(self, node,context):
        """
        :type node:TreeNode
        :type context:Context
        """
        for subnode in node[1:]:
            if isinstance(subnode, TreeNode):
                if subnode[0] == "expression_statement":
                    self.gen_expression_statement(subnode,context)
                elif subnode[0] == "compound_statement":
                    self.tools.newScope(subnode.context)
                    self.gen_compound_statement(subnode,subnode.context)
                    self.tools.endScope()
                elif subnode[0] == "selection_statement":
                    self.gen_selection_statement(subnode,context)
                elif subnode[0]=="jump_statement":
                    self.gen_jump_statement(subnode,context)
                elif subnode[0]=="iteration_statement":
                    self.gen_iteration_statement(subnode,context)

    def gen_expression_statement(self, node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype :str
        """
        if isinstance(node[1],TreeNode):
            ret=self.expression_handler[node[1][0]](node[1],context)
        else:
            ret=self.tools.getTrue()
        return ret

    def gen_compound_statement(self, node,context):
        """
        :type node:TreeNode
        :type context:Context
        """
        for subnode in node[1:]:
            if isinstance(subnode, TreeNode):
                if subnode[0] == "statement_list":
                    self.gen_statement_list(subnode,context)

    def gen_selection_statement(self, node,context):
        """
        :type node:TreeNode
        :type context:Context
        """
        # node[3]:expression
        # node[5]:statement
        # node[7]:statement
        if node[1] == "if":
            ret=self.expression_handler[node[3][0]](node[3],context)
            if len(node) == 6:
                label1=self.tools.allocateLabel()
                self.tools.cmp(ret,self.tools.getFalse())
                self.tools.je(label1)
                self.gen_statement(node[5],context)
                self.tools.markLabel(label1)
            elif len(node) == 8:
                label1=self.tools.allocateLabel()
                label2=self.tools.allocateLabel()
                self.tools.cmp(ret,self.tools.getFalse())
                self.tools.je(label1)
                self.gen_statement(node[5],context)
                self.tools.jmp(label2)
                self.tools.markLabel(label1)
                self.gen_statement(node[7],context)
                self.tools.markLabel(label2)

    def gen_jump_statement(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        """
        if isinstance(node[2],TreeNode):
            ret=self.expression_handler[node[2][0]](node[2],context)
            self.tools.mov(self.tools.getEax(),ret)
        self.tools.ret()

    def gen_iteration_statement(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        """
        if node[1]=="for":
            if isinstance(node[5],TreeNode):
                label1=self.tools.allocateLabel()
                label2=self.tools.allocateLabel()
                label3=self.tools.allocateLabel()
                self.gen_expression_statement(node[3],context)
                self.tools.jmp(label2)
                self.tools.markLabel(label1)
                self.expression_handler[node[5][0]](node[5],context)
                self.tools.markLabel(label2)
                ret=self.gen_expression_statement(node[4],context)
                self.tools.cmp(ret,self.tools.getFalse())
                self.tools.je(label3)
                self.gen_statement(node[7],context)
                self.tools.jmp(label1)
                self.tools.markLabel(label3)
            else:
                label1=self.tools.allocateLabel()
                label2=self.tools.allocateLabel()
                self.gen_expression_statement(node[3],context)
                self.tools.markLabel(label1)
                ret=self.gen_expression_statement(node[4],context)
                self.tools.cmp(ret,self.tools.getFalse())
                self.gen_statement(node[6],context)
                self.tools.jmp(label1)
                self.tools.markLabel(label2)
        elif node[1]=="while":
            label1=self.tools.allocateLabel()
            label2=self.tools.allocateLabel()
            self.tools.markLabel(label1)
            ret=self.expression_handler[node[3][0]](node[3],context)
            self.tools.cmp(ret,self.tools.getFalse())
            self.tools.je(label2)
            self.gen_statement(node[5],context)
            self.tools.jmp(label1)
            self.tools.markLabel(label2)



    def gen_additive_expression(self, node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        op1=self.expression_handler[node[1][0]](node[1],context)
        tmp=self.tools.allocateNewReg(op1)
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3],context)
        if node[2]=="+":
            ret=self.tools.add(tmp,op2)
        else:
            ret=self.tools.sub(tmp,op2)
        self.tools.unLock(tmp)
        return ret

    def gen_primary_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: Data
        """
        if isinstance(node[1],TreeNode):
            if node[1][0]=="IDENTIFIER":
                name=node[1][1]
                offset=False
                type=deepcopy(context.get_type_by_id(name))
                return Data(name,offset,type)
            else:
                if node[1][0]=="INTEGER":
                    return int(node[1][1])
                elif node[1][0]=="DOUBLE":
                    return float(node[1][1])
                elif node[1][0]=="STRING":
                    return str(node[1][1]) 


    def gen_postfix_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        operand=self.expression_handler[node[1][0]](node[1],context)
        if node[2]=="[":
            if operand.offset==False:
                self.tools.mov(self.tools.getEax(),0)
            index=self.expression_handler[node[3][0]](node[3],context)
            self.tools.mul(index,operand.type.member_type.Size())
            operand.offset=True
            operand.type=operand.type.member_type
            return operand
        elif node[2]=="(":
            if isinstance(node[3],TreeNode):
                argument_expression_list=node[3]
                real_arg_list=[]
                for argument_expression in argument_expression_list[1:]:
                    if isinstance(argument_expression,TreeNode):
                        argument=self.expression_handler[argument_expression[0]](argument_expression,context)
                        if argument==self.tools.getEax():
                            tmp=self.tools.allocateNewReg(self.tools.getEax())
                            self.tools.lock(tmp)
                            self.tools.mov(tmp,self.tools.getEax())
                            real_arg_list.append([tmp,0])
                        elif isinstance(argument,Data) and argument.offset:
                            tmp=self.tools.allocateNewReg(self.tools.getEax())
                            self.tools.lock(tmp)
                            self.tools.mov(tmp,self.tools.getEax())
                            real_arg_list.append([argument,1,tmp])
                        else:
                            real_arg_list.append([argument,2])
                for list in real_arg_list:
                    if list[1]==1:
                        self.tools.mov(self.tools.getEax(),list[2])
                    self.tools.passPara(list[0])
                    if list[1]==0:
                        self.tools.unLock(list[0])
                    if list[1]==1:
                        self.tools.unLock(list[2])
            ret=self.tools.call(operand)
            return ret
        elif node[2]==".":
            if operand.offset==False:
                self.tools.mov(self.tools.getEax(),0)
            member=node[3][1]
            self.tools.add(self.tools.getEax(),operand.type.offset[member])
            operand.type=operand.type.members[member]
            operand.offset=True
            return operand
        elif node[2]=="->":
            if operand.offset==False:
                self.tools.mov(self.tools.getEax(),0)
            self.tools.mov(self.tools.getEax(),operand)
            member=node[3][1]
            self.tools.add(self.tools.getEax(),operand.type.offset[member])
            operand.name=self.tools.getNull()
            operand.type=operand.type.members[member]
            operand.offset=True
            return operand


    def gen_unary_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        operand=self.expression_handler[node[2][0]](node[2],context)
        if isinstance(node[1],TreeNode):
            operator=self.gen_unary_operator(node[1],context)
            if operator=="&":
                if isinstance(operand,Data):
                    ret=self.tools.lea(operand)
                    operand.type.is_const.append(False)
                    return ret
            elif operator=="*":
                if isinstance(operand,Data):
                    self.tools.mov(self.tools.getEax(),operand)
                    operand.name=self.tools.getNull()
                    operand.offset=True
                    operand.type.is_const.pop()
                    return operand
        else:
            if node[1]=="++":
                self.tools.add(operand,1)
                return operand
            elif node[1]=="--":
                self.tools.sub(operand,1)
                return operand


    def gen_cast_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        pass

    def gen_multiplicative_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        op1=self.expression_handler[node[1][0]](node[1],context)
        tmp=self.tools.allocateNewReg(op1)
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3],context)
        if node[2]=="*":
            if isinstance(op2,str):
                try:
                    num=int(op2)
                    if num in self.exp2:
                        ret=self.tools.sal(tmp,str(self.exp2.index(num)))
                    else:
                        ret=self.tools.mul(tmp,op2)
                except TypeError:
                    ret=self.tools.mul(tmp,op2)
            else:
                ret=self.tools.mul(tmp,op2)
        elif node[2]=="/":
            if isinstance(op2,str):
                try:
                    num=int(op2)
                    if num in self.exp2:
                        ret=self.tools.sar(tmp,str(self.exp2.index(num)))
                    else:
                        ret=self.tools.div(tmp,op2)
                except TypeError:
                    ret=self.tools.div(tmp,op2)
            else:
                ret=self.tools.div(tmp,op2)
        self.tools.unLock(tmp)
        return ret


    def gen_shift_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        pass

    def gen_relational_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        label1=self.tools.allocateLabel()
        label2=self.tools.allocateLabel()
        op1=self.expression_handler[node[1][0]](node[1],context)
        tmp=self.tools.allocateNewReg(op1)
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3],context)
        self.tools.cmp(tmp,op2)
        if node[2]=="<":
            self.tools.jl(label1)
        elif node[2]=="<=":
            self.tools.jle(label1)
        elif node[2]==">":
            self.tools.jg(label1)
        elif node[2]==">=":
            self.tools.jge(label1)
        self.tools.mov(self.tools.getEax(),0)
        self.tools.jmp(label2)
        self.tools.markLabel(label1)
        self.tools.mov(self.tools.getEax(),1)
        self.tools.markLabel()
        return self.tools.getEax()

    def gen_equality_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        label1=self.tools.allocateLabel()
        label2=self.tools.allocateLabel()
        op1=self.expression_handler[node[1][0]](node[1],context)
        tmp=self.tools.allocateNewReg(op1)
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3],context)
        self.tools.cmp(tmp,op2)
        if node[2]=="==":
            self.tools.je(label1)
        elif node[2]=="!=":
            self.tools.jne(label1)
        self.tools.mov(self.tools.getEax(),0)
        self.tools.jmp(label2)
        self.tools.markLabel(label1)
        self.tools.mov(self.tools.getEax(),1)
        self.tools.markLabel()
        return self.tools.getEax()


    def gen_and_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        op1=self.expression_handler[node[1][0]](node[1],context)
        tmp=self.tools.allocateNewReg(op1)
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3],context)
        ret=self.tools.And(tmp,op2)
        self.tools.unLock(tmp)
        return ret

    def gen_exclusive_or_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        pass
        # op1=self.expression_handler[node[1][0]](node[1],context)
        # tmp=self.tools.allocateNewReg()
        # self.tools.lock(tmp)
        # self.tools.mov(tmp,op1)
        # op2=self.expression_handler[node[3][0]](node[3],context)
        # ret=self.tools.xor(tmp,op2)
        # self.tools.unLock(tmp)
        # return ret

    def gen_inclusive_or_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        op1=self.expression_handler[node[1][0]](node[1],context)
        tmp=self.tools.allocateNewReg(op1)
        self.tools.lock(tmp)
        self.tools.mov(tmp,op1)
        op2=self.expression_handler[node[3][0]](node[3],context)
        ret=self.tools.Or(tmp,op2)
        self.tools.unLock(tmp)
        return ret

    def gen_logical_and_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        label_out=self.tools.allocateLabel()
        op1=self.expression_handler[node[1][0]](node[1],context)
        left=self.tools.cmp(op1,self.tools.getFalse())
        self.tools.je(label_out)

        op2=self.expression_handler[node[3][0]](node[3],context)
        right=self.tools.cmp(op2,self.tools.getFalse())

        self.tools.markLabel(label_out)
        return right

    def gen_logical_or_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        label_out=self.tools.allocateLabel()
        op1=self.expression_handler[node[1][0]](node[1],context)
        left=self.tools.cmp(op1,self.tools.getFalse())
        self.tools.jne(label_out)

        op2=self.expression_handler[node[3][0]](node[3],context)
        right=self.tools.cmp(op2,self.tools.getFalse())

        self.tools.markLabel(label_out)
        return right

    def gen_conditional_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        pass

    def gen_assignment_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        operator=self.gen_assignment_operator(node[2],context)
        right=self.expression_handler[node[3][0]](node[3],context)
        tmp=self.tools.allocateNewReg(right)
        self.tools.lock(tmp)
        self.tools.mov(tmp,right)
        left=self.expression_handler[node[1][0]](node[1],context)
        print(left)
        if operator=="=":
            self.tools.mov(left,tmp)
        self.tools.unLock(tmp)
        return left

    def gen_expression(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        pass

    def gen_assignment_operator(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        return node[1]

    def gen_unary_operator(self,node,context):
        """
        :type node:TreeNode
        :type context:Context
        :rtype: str
        """
        return node[1]

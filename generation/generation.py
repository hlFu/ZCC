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
                self.tools.newFunc(funcName)
                #这部分就是要解析树并调用tools函数翻译
                #下面是我乱加的
                '''if(funcName=='main'):
                    self.tools.add('l_i',1)
                    self.tools.mov('x1',2)
                    self.tools.sub('l_i','x1')
                    self.tools.mov('x2',3)
                    self.tools.mov('x3',4)
                    self.tools.call('foo')
                    returnV='l_i'
                    self.tools.ret(funcName,returnV)
                else:
                    self.tools.mov('x1',2)
                    self.tools.mov('x2',3)
                    self.tools.add('x1',1)
                    self.tools.ret(funcName)'''
                self.tools.showMap()
                self.tools.ret(funcName)
        self.tools.end()
    
    def output(self,fileName):
        with open(fileName,'w') as out:
            for line in self.asm:
                out.write(line)
#!/usr/bin/python
import sys
sys.path.append('c:\\zcc\\zcc')
from public.ZCCglobal import *

class utility:
    def __init__(self,Gen):
        self.gen=Gen
        self.currentMap={}
        # global record for register uses
        self.registers={'eax':0,'edx':0,'esi':0,'edi':0}
        # all global v
        self.globalV={}
        # all statics v
        self.statics={}
        # static in current context
        self.currentStatic={}
        # strings record addr of const strings
        # is a tuple
        # has form of (string, label)
        self.strings={}
        # record float or double num
        # has form of {num, label}
        self.doubles={}
        # postfix of statics
        self.magicNum=1234
        # record whether reg is modified by func
        self.dirty={'edx':0,'esi':0,'edi':0}
        #use for mark the next reg which will be alternate
        self.randomReg='edx'
        
    def globalInitialize(self):
        self.gen.asm.append('\t.intel_syntax noprefix\n')
        for key in global_context.local:
            value = global_context.local[key]
            if(value.type!='function'):
                if(value.type=='struct'):
                    st=self.__parseStruct(key,value)
                    size=0
                    for member in st:
                        if(st[member].type!='double'):
                            size+=4
                        else:
                            size+=8
                    self.globalV.update(st)
                    self.gen.asm.append('\t.comm '+key+',%d,4\n' %(size))
                self.globalV.update({key:value})
                if(value.storage_class=='static'):
                    self.gen.asm.append('\t.local '+key+'\n')
                self.gen.asm.append('\t.comm '+key+',%.d,4\n' %(value.size))
        self.gen.asm.append('\t.section .rodata\n')
        self.gen.asm.append('\t.text\n')
    
    def __parseStruct(self,structName,Struct):
        V={}
        for member in Struct.members:
            if(isinstance(member,StructType)):
                V.update(self.__parseStruct(member,Struct.members[member]))
            else:
                V.update({structName+'.'+member:Struct.members[member]})
        return V

    def end(self):
        self.gen.asm.append('\t.ident	\"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2\"\n')
        self.gen.asm.append('\t.section	.note.GNU-stack,"",@progbits\n')
    
    def showMap(self):
        print(self.currentMap)

    def newMap(self,funcName,space=32,reserve=0):
        offset=space-reserve
        map={}
        for v in global_context.local[funcName].compound_statement.context.local:
            value=global_context.local[funcName].compound_statement.context.local[v]
            s_class=value.storage_class
            Type=value.type
            size=value.size
            if(Type == 'struct'):
                st=self.__parseStruct(v,value)
                for member in st:
                    Type = st[member].type
                    if(Type == 'double'):
                        size=8
                    else:
                        size=4
                    map.update({member:{'reg':0,'type':Type,'addr':'[esp+%.d]'%(offset-size)}})
                    offset-=size
                continue
            if(s_class == 'static'):
                v=v+'%.d' % self.magicNum
                self.magicNum+=4
                map.update({v:{'reg':0,'type':Type,'addr':v}})
                self.currentStatic.update({v:Type})
                self.statics.update({v:Type})
                continue
            map.update({v:{'reg':0,'type':Type,'addr':'[esp+%.d]'%(offset-size)}})
            offset-=size
        for v in self.globalV:
            map.update({v:{'reg':0,'type':self.globalV[v],'addr':v}})
        self.dirty={'edx':0,'esi':0,'edi':0}
        return map
    
    def newFunc(self,funcName):
        space=32
        self.gen.asm.append('\t.globl '+funcName+'\n')
        self.gen.asm.append('\t.type '+funcName+', @function\n')
        self.gen.asm.append(funcName+':\n')
        self.gen.asm.append('\tpush ebp\n')
        self.gen.asm.append('\tmov ebp, esp\n')
        self.gen.asm.append('\tsub esp, %.d\n' % space)
        self.currentMap=self.newMap(funcName)
    
    def ret(self,funcName,returnV=None):
        for v in self.currentStatic:
            if(self.currentMap[v]['reg']!=0):
                self.gen.asm.append('\tmov '+v+', '+self.currentMap[v]['reg'])
        for v in self.globalV:
            if(self.currentMap[v]['reg']!=0):
                self.gen.asm.append('\tmov '+v+', '+self.currentMap[v]['reg'])
        if(returnV!=None and self.currentMap[returnV]['reg']!='eax' and self.currentMap[returnV]['reg']!=0):
            self.gen.asm.append('\tmov eax, '+self.currentMap[returnV]['reg'])
        if(funcName=='main'):
            self.gen.asm.append('\tleave\n')
        else:
            index=self.findLast(self.gen.asm,'\tpush ebp\n')
            for reg in self.dirty:
                if(self.dirty[reg]!=0):
                    self.gen.asm.insert(index,'\tpush '+reg+'\n')
                    self.gen.asm.append('\tpop '+reg+'\n')
            self.gen.asm.append('\tleave\n')
        self.gen.asm.append('\tret\n')
        self.gen.asm.append('\t.size '+funcName+', .-'+funcName+'\n')
    
    def findLast(self,text,word):
        for i in range(0,len(text)):
            index=len(text)-i-1
            if(text[index]==word):
                return index+2
        raise NameError(word + ' is not in the list')
    
    def checkIn(self,vName):
        """
            check if veriable is in reg
            allocate a new free one
            if no free, push back one
            @vName veriable name
        """
        try:
            if(self.currentMap[vName]['reg']==0):
                reg=self.checkFull()
                if(reg==-1):
                    reg=self.allocateNewReg()
                if(self.registers[reg]==1):
                    self.dirty[reg]=1
                self.currentMap[vName]['reg']=reg
                self.registers[reg]=1
        except Exception,e:
            print e
            print vName
            print self.currentMap
    
    def checkFull(self):
        """
            check if reg is full
            if: return one free
            if not: return -1
        """
        for reg in self.registers:
            if(self.registers[reg]==0):
                return reg
        return -1
    
    def allocateNewReg(self):
        """
            push back one reg to get a free space
        """
        self.randomReg=self.findOneReg()
        for vName in self.currentMap:
            if(self.currentMap[vName]['reg']==self.randomReg):
                self.gen.asm.append('\tmov '+vName+', '+self.randomReg+'\n')
        return self.randomReg
    
    def findOneReg(self):
        flag=0
        for reg in self.registers:
            if(flag==1):
                return reg
            else:
                if(reg==self.randomReg):
                    flag=1
        return 'eax'
    
    def add(self,x1,x2):
        self.checkIn(x1)
        #x2 is not a imm
        if(isinstance(x2,str)):
            self.checkIn(x2)
            self.gen.asm.append('\tadd '+self.currentMap[x1]['reg']+', '+self.currentMap[x2]['reg']+'\n')
        else:
            self.gen.asm.append('\tadd '+self.currentMap[x1]['reg']+', %.d'%x2+'\n')
    
    def addTmp(self):
        '''
        perform bx=bx+ax
        bx is a tmp reg
        deal with assignment like a=func(b)+func(c)+...
        '''
        self.gen.asm.append('\tadd ebx eax\n')
    
    def sub(self,x1,x2):
        self.checkIn(x1)
        if(isinstance(x2,str)):
            self.checkIn(x2)
            self.gen.asm.append('\tsub '+self.currentMap[x1]['reg']+', '+self.currentMap[x2]['reg']+'\n')
        else:
            self.gen.asm.append('\tsub '+self.currentMap[x1]['reg']+', %.d' % x2+'\n')
    
    def subTmp(self):
        '''
        perform bx=bx-ax
        bx is a tmp reg
        deal with assignment like a=func(b)-func(c)-...
        '''
        self.gen.asm.append('\tsub ebx eax\n')
    
    def mov(self,x1,x2):
        self.checkIn(x1)
        if(isinstance(x2,str)):
            self.checkIn(x2)
            self.gen.asm.append('\tmov '+self.currentMap[x1]['reg']+', '+self.currentMap[x2]['reg']+'\n')
        else:
            try:
                self.gen.asm.append('\tmov '+self.currentMap[x1]['reg']+', %.d' % x2+'\n')
            except Exception,e:
                print '!!!'
                print self.currentMap[x1]['reg']
        
    def call(self,funcName,parameters=None):
        '''
        @funcName: function
        @parameters: a dict like{parameter1 name: type, parameter2 ...}
        '''
        offset=0
        for para in parameters:
            source=None
            Type=parameters[para]
            if(Type=='char'):
                self.gen.asm.append('\tmov BYTE PTR ')
                offset+=4
            elif(Type=='short'):
                self.gen.asm.append('\tmov WORD PTR ')
                offset+=4
            elif(Type=='int'):
                self.gen.asm.append('\tmov DWORD PTR ')
                offset+=4
            elif(Type=='const int'):
                source=int(para)
                offset+=4
            elif(Type=='const char'):
                source=char(para)
            elif(Type=='struct'):
                for member in self.currentMap:
                    if(member.find(para)!=-1):
                        self.checkIn(para)
                        if(offset==0):
                            self.gen.asm.append('[esp], ')
                        else:
                            self.gen.asm.append('[esp+%.d], '%offset)
                        self.gen.asm.append(self.currentMap[member]['reg'])
                        if(self.currentMap[Type] == 'double'):
                            offset+=8
                        else:
                            offset+=4
            if(offset==0):
                self.gen.asm.append('[esp], ')
            else:
                self.gen.asm.append('[esp+%.d], '%offset)
            if(source==None):
                checkIn(para)
                source=self.currentMap[para]['reg']
            self.gen.asm.append(source+'\n')
            
        for vName in self.currentMap:
            if(self.currentMap[vName]['reg']=='eax'):
                self.currentMap[vName]['reg']=0
                self.registers['eax']=0
                self.gen.asm.append('\tmov '+self.currentMap[vName]['addr']+', eax\n')
        self.gen.asm.append('\tcall '+funcName+'\n')
    
    def And(self,x1,x2):
        self.checkIn(x1)
        if(isinstance(x2,str)):
            self.checkIn(x2)
            self.gen.asm.append('\tand '+self.currentMap[x1]['reg']+', '+self.currentMap[x2]['reg']+'\n')
        else:
            self.gen.asm.append('\tand '+self.currentMap[x1]['reg']+', %.d' % x2+'\n')
        
    def Or(self,x1,x2):
        self.checkIn(x1)
        if(isinstance(x2,str)):
            self.checkIn(x2)
            self.gen.asm.append('\tor '+self.currentMap[x1]['reg']+', '+self.currentMap[x2]['reg']+'\n')
        else:
            self.gen.asm.append('\tor '+self.currentMap[x1]['reg']+', %.d' % x2+'\n')
        
    def nor(self,x1,x2):
        self.checkIn(x1)
        if(isinstance(x2,str)):
            self.checkIn(x2)
            self.gen.asm.append('\tnor '+self.currentMap[x1]['reg']+', '+self.currentMap[x2]['reg']+'\n')
        else:
            self.gen.asm.append('\tnor '+self.currentMap[x1]['reg']+', %.d' % x2+'\n')
        
    def Not(self,x1,x2):
        self.checkIn(x1)
        self.checkIn(x2)
        self.gen.asm.append('\tnot '+self.currentMap[x1]['reg']+', '+self.currentMap[x2]['reg']+'\n')
    
    def markLabel(self,label):
        """
        give a label at current place
        mostly use at loop
        """
        self.gen.asm.append(label+':\n')
    
    def cmp(self,x1,x2):
        if(isinstance(x1,str)):
            v1=self.currentMap[x1]['reg']
        if(isinstance(x2,str)):
            v2=self.currentMap[x2]['reg']
        if(v1==0):
            v1=x1
        if(v2==0):
            v2=x2
        self.gen.asm.append('\tcmp '+v1+', '+v2+'\n')
    
    def jg(self,label):
        self.gen.asm.append('\tjg '+label+'\n')
    
    def jge(self,label):
        self.gen.asm.append('\tjge '+label+'\n')
    
    def jl(self,label):
        self.gen.asm.append('\tjgl '+label+'\n')
    
    def jle(self,label):
        self.gen.asm.append('\tjle '+label+'\n')
        
    def je(self,label):
        self.gen.asm.append('\tje '+label+'\n')
        
    def jne(self,label):
        self.gen.asm.append('\tjne '+label+'\n')
    
    def loop(self,label):
        self.gen.asm.append('\tloop '+label+'\n')
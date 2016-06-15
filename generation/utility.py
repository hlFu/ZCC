#!/usr/bin/python
import sys
sys.path.append('c:\\zcc\\zcc')
from public.ZCCglobal import *

class utility:
    def __init__(self,Gen):
        self.gen=Gen
        self.currentMap={}
        # record all map of scope
        self.mapStack=[]
        # global record for register uses
        self.registers={'ebx':0,'ecx':0,'edx':0,'esi':0,'edi':0}
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
        self.dirty={'ebx':0,'ecx':0,'edx':0,'esi':0,'edi':0}
        # point to the tmp stack top
        self.tmpSP=0
        #use for mark the next reg which will be alternate
        self.randomReg='edx'
        #tmp Name
        self.tmpName='__tmp'
        self.tmpNum=1
        self.callOffset=0

        
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
    
    # def __parseStruct(self,structName,Struct):
    #     V={}
    #     for member in Struct.members:
    #         if(isinstance(member,StructType)):
    #             V.update(self.__parseStruct(member,Struct.members[member]))
    #         else:
    #             V.update({structName+'.'+member:Struct.members[member]})
    #     return V

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
            size=value.size()
            # if(Type == 'struct'):
            #     st=self.__parseStruct(v,value)
            #     for member in st:
            #         Type = st[member].type
            #         if(Type == 'double'):
            #             size=8
            #         else:
            #             size=4
            #         map.update({member:{'reg':0,'type':Type,'addr':'[esp+%.d]'%(offset-size)}})
            #         offset-=size
            #     continue
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
        self.dirty={'ebx':0,'ecx':0,'edx':0,'esi':0,'edi':0}
        return map
    
    def newFunc(self,funcName):
        space=64
        self.gen.asm.append('\t.globl '+funcName+'\n')
        self.gen.asm.append('\t.type '+funcName+', @function\n')
        self.gen.asm.append(funcName+':\n')
        self.gen.asm.append('\tpush ebp\n')
        self.gen.asm.append('\tmov ebp, esp\n')
        self.gen.asm.append('\tsub esp, %.d\n' % space)
        self.currentMap=self.newMap(funcName)
        self.tmpSP=4
    
    def endFunc(self,funcName):
        self.gen.asm.append('\t.size '+funcName+', .-'+funcName+'\n')
        pass
    
    def newScope(self,scope):
        self.mapStack.append(self.currentMap)
        if(isinstance(scope,Context)):
            for V in scope.local:
                value=scope.local[v]
                s_class=value.storage_class
                Type=value.type
                size=value.size()
                if(s_class == 'static'):
                    v=v+'%.d' % self.magicNum
                    self.magicNum+=4
                    map.update({v:{'reg':0,'type':Type,'addr':v}})
                    self.currentStatic.update({v:Type})
                    self.statics.update({v:Type})
                    continue
                map.update({v:{'reg':0,'type':Type,'addr':'[esp+%.d]'%(offset-size)}})
                offset-=size
        return

        raise TypeError("error in newScope!\n")
    
    def endScope(self):
        self.currentMap=self.mapStack.pop()
        
        return

    def getTrue():
        return 'true'
    
    def getFalse():
        return 'false'

    def ret(self,funcName,returnV=None):
        # for v in self.currentStatic:
        #     if(self.currentMap[v]['reg']!=0):
        #         self.gen.asm.append('\tmov '+v+', '+self.currentMap[v]['reg'])
        # for v in self.globalV:
        #     if(self.currentMap[v]['reg']!=0):
        #         self.gen.asm.append('\tmov '+v+', '+self.currentMap[v]['reg'])
        # if(returnV!=None and self.currentMap[returnV]['reg']!='eax' and self.currentMap[returnV]['reg']!=0):
        #     self.gen.asm.append('\tmov eax, '+self.currentMap[returnV]['reg'])
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
        # try:
        #     if(self.currentMap[vName]['reg']==0):
        #         reg=self.allocateNewReg()
        #         if(self.registers[reg]==1):
        #             self.dirty[reg]=1
        #         self.currentMap[vName]['reg']=reg
        #         self.registers[reg]=1
        # except Exception,e:
        #     print e
        #     print vName
        #     print self.currentMap
        if(self.currentMap[vName]['reg']!=0):
            return True
        
        return False
    
    def checkFull(self):
        """
            check if reg is full
            if: return one free
            if not: return -1
        """
        for reg in self.registers:
            if(self.registers['reg']==0):
                return reg
        return -1
    
    def allocateNewReg(self,Type):
        """
            get a new free reg, if full get a mem address
        """
        if(Type=='double'):
            return
        
        newTmp=self.tmpName+str(self.tmpNum)
        self.tmpNum+=1
        reg=checkFull()
        if(reg!=-1):
            self.currentMap.update({newTmp:{'reg':reg,'type':Type,'addr':0}})
            return reg
        else:
            self.currentMap.update({newTmp:{'reg':0,'type':Type,'addr':'[esp-%.d]'%(self.tmpSP)}})
            return newTmp
        


    def lock(self,name):
        if(name in self.registers):
            self.registers[name]=1
            return

        if(self.currentMap[name]['type']=='double'):
            self.tmpSP+=8
        else:
            self.tmpSP+=4
        
        return
    
    def unLock(self,name):
        if(name in self.registers):
            self.registers[name]=0
            return

        if(self.currentMap[name]['type']=='double'):
            self.tmpSP-=8
        else:
            self.tmpSP-=4
        
        self.currentMap.pop(name)
        
        return
    
    # def findOneReg(self):
    #     flag=0
    #     for reg in self.registers:
    #         if(flag==1):
    #             return reg
    #         else:
    #             if(reg==self.randomReg):
    #                 flag=1
    #     return 'eax'
    
    def add(self,x1,x2):
        if(isinstance(x1,Data)):
            x1=x1.name
        if(isinstance(x2,Data)):
            x2=x2.name
        #x2 is not a imm
        if(x2=='eax'):
            y1=x2
            y2=x1
        if(y1 in self.currentMap and y2 on self.currentMap):
            self.gen.asm.append("\tmov eax, "+self.currentMap[y1]['addr']+'\n')
            self.gen.asm.append("\tadd eax, "+self.currentMap[y2]['addr']+'\n')
        elif(isinstance(y2,str)):
            if(y2 in self.currentMap):
                self.gen.asm.append('\tadd eax, '+self.currentMap[y2]['addr']+'\n')
            else:
                self.gen.asm.append('\tadd eax, '+y2+'\n')
        else:
            if(y2 in self.currentMap):
                self.gen.asm.append("\tmov eax, "+self.currentMap[y1]['addr']+'\n')
            self.gen.asm.append("\tadd eax, "+str(y2)+'\n')
        return 'eax'
    
    # def addToTmp(self):
    #     '''
    #     perform bx=bx+ax
    #     bx is a tmp reg
    #     deal with assignment like a=func(b)+func(c)+...
    #     '''
    #     self.gen.asm.append('\tadd ebx eax\n')
    
    def sub(self,x1,x2):
        if(isinstance(x1,Data)):
            x1=x1.name
        if(isinstance(x2,Data)):
            x2=x2.name
        #x2 is not a imm
        if(x2=='eax'):
            self.gen.asm.append("\tsub "+x1+', '+'eax'+'\n')
            self.gen.asm.append('\tmov eax, '+x1+'\n')
        if(x1 in self.currentMap and x2 on self.currentMap):
            self.gen.asm.append("\tmov eax, "+self.currentMap[x1]['addr']+'\n')
            self.gen.asm.append("\tsub eax, "+self.currentMap[x2]['addr']+'\n')
        elif(isinstance(x2,str)):
            if(x2 in self.currentMap):
                self.gen.asm.append('\tsub eax, '+self.currentMap[x2]['addr']+'\n')
            else:
                self.gen.asm.append('\tsub eax, '+x2+'\n')
        else:
            if(x2 in self.currentMap):
                self.gen.asm.append("\tmov eax, "+self.currentMap[x1]['addr']+'\n')
            self.gen.asm.append("\tsub eax, "+str(x2)+'\n')
        return 'eax'
    
    # def subTmp(self):
    #     '''
    #     perform bx=bx-ax
    #     bx is a tmp reg
    #     deal with assignment like a=func(b)-func(c)-...
    #     '''
    #     self.gen.asm.append('\tsub ebx eax\n')
    
    def mul(self,x1,x2,returnSpace):
        if(isinstance(x1,Data)):
            x1=x1.name
        if(isinstance(x2,Data)):
            x2=x2.name

        #mem mem
        if(x1 in self.currentMap):
            # returnSpace is reg
            if(returnSpace in self.registers):
                self.gen.asm.append("\tmov "+newSpace+", "+self.currentMap[x1]['addr']+'\n')
                self.gen.asm.append("\tmul "+newSpace+", "+self.currentMap[x2]['addr']+'\n')
            #returnSpace is mem
            else:
                self.gen.asm.append("\tmov "+"eax"+", "+self.currentMap[x1]['addr']+'\n')
                self.gen.asm.append("\tmul "+"eax"+", "+self.currentMap[x2]['addr']+'\n')
                self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            
        else:
            if(x1==returnSpace):
                self.gen.asm.append("\tmul "+returnSpace+", "+self.currentMap[x2]['addr']+'\n')
            else:
                self.gen.asm.append("\tmov "+returnSpace+", "+x1+'\n')
                self.gen.asm.append("\tmul "+returnSpace+", "+self.currentMap[x2]['addr']+'\n')
        
        return returnSpace        


def div(self,x1,x2,returnSpace):
        if(isinstance(x1,Data)):
            x1=x1.name
        if(isinstance(x2,Data)):
            x2=x2.name

        #mem mem
        if(x1 in self.currentMap):
            if(returnSpace in self.registers):
                self.gen.asm.append("\tmov "+"eax"+", "+self.currentMap[x1]['addr']+'\n')
                self.gen.asm.append("cdq")
                self.gen.asm.append("\tidiv "+self.currentMap[x1]['addr']+'\n')
                self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            
        else:
            if(x1==returnSpace):
                if(x1=='eax'):
                    self.gen.asm.append("cdq")
                    self.gen.asm.append("\tidiv "+returnSpace+", "+self.currentMap[x2]['addr']+'\n')
                else:
                    self.gen.asm.append("\tmov "+"eax"+", "+x1+'\n')
                    self.gen.asm.append("cdq")
                    self.gen.asm.append("\tidiv"+self.currentMap[x2]['addr']+'\n')
                    self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            else:
                self.gen.asm.append("\tmov "+"eax"+", "+x1+'\n')
                self.gen.asm.append("cdq")
                self.gen.asm.append("\tidiv"+self.currentMap[x2]['addr']+'\n')
                self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
        
        return returnSpace  

    def mov(self,x1,x2):
        if(isinstance(x1,Data)):
            x1=x1.name
        if(isinstance(x2,Data)):
            x2=x2.name

        #x2 is not a imm
        if(x1 in self.currentMap and x2 on self.currentMap):
            self.gen.asm.append("\tmov eax, "+self.currentMap[x2]['addr']+'\n')
            self.gen.asm.append("\tmov "+self.currentMap[x2]['addr']+' eax'+'\n')
        elif(isinstance(x2,str)):
            self.gen.asm.append('\tmov '+x1+', '+self.currentMap[x2]['addr']+'\n')
        else:
            self.gen.asm.append('\tmov '+x1+', %.d'%x2+'\n')
        return x1
        
    def passPara(self,para):
            source=None
            Type=para.type
            if(Type=='char'):
                self.gen.asm.append('\tmov BYTE PTR ')
                self.callOffset+=4
            elif(Type=='short'):
                self.gen.asm.append('\tmov WORD PTR ')
                self.callOffset+=4
            elif(Type=='int'):
                self.gen.asm.append('\tmov DWORD PTR ')
                self.callOffset+=4
            elif(Type=='const int'):
                source=int(para)
                self.callOffset+=4
            elif(Type=='const char'):
                source=char(para)
            elif(Type=='struct'):
                for i in 
            if(self.callOffset==0):
                self.gen.asm.append('[esp], ')
            else:
                self.gen.asm.append('[esp+%.d], '%self.callOffset)
            if(source==None):
                checkIn(para)
                source=self.currentMap[para]['reg']
            self.gen.asm.append(source+'\n')

    def getEax(self):
        return "eax"
    
    def getNull(self):
        return 0
        

    def call(self,funcName,parameters=None):
        '''
        @funcName: function
        @parameters: a dict like{parameter1 name: type, parameter2 ...}
        '''

            
        # for vName in self.currentMap:
        #     if(self.currentMap[vName]['reg']=='eax'):
        #         self.currentMap[vName]['reg']=0
        #         self.registers['eax']=0
        #         self.gen.asm.append('\tmov '+self.currentMap[vName]['addr']+', eax\n')
        self.callOffset=0
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
    
    def markLabel(self,label=None):
        """
        give a label at current place
        mostly use at loop
        """
        if(label==None):
            label='.LC%.d'%self.magicNum
            self.magicNum+=1
        self.gen.asm.append(label+':\n')
    
    def allocateLabel(self):
        
        return '.LC%.d'%self.magicNum

    
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
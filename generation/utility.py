#!/usr/bin/python
import re
import sys
sys.path.append('c:\\zcc\\zcc')
from public.ZCCglobal import *
from data import Data

class utility:
    def __init__(self,Gen):
        self.gen=Gen
        self.currentMap={}
        # record all map of scope
        self.mapStack=[]
        # global record for register uses
        self.registers={'eax':1,'st':1,'ebx':0,'ecx':0,'edx':0,'esi':0,'edi':0}
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
        self.magicNum=0
        # record whether reg is modified by func
        self.dirty={'ebx':0,'ecx':0,'edx':0,'esi':0,'edi':0}
        # point to the tmp stack top
        self.tmpSP=0
        #use for mark the next reg which will be alternate
        self.randomReg='edx'
        #tmp Name
        self.tmpName='__tmp'
        self.tmpNum=1
        self.constName='.LC'
        self.constMap={}
        self.callOffset=0
        self.funcName=None
        self.localOffset=0

        
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
                self.gen.asm.append('\t.comm '+key+',%d,4\n' %(value.size))
        self.gen.asm.append('\t.section .rodata\n')
        #get const string and double
        for v in global_context.literal:
            self.constMap.update({v:(self.constName+str(self.magicNum))})
            self.magicNum+=1
            self.gen.asm.append(self.constMap[v]+'\n')
            if(isinstance(v,str)):
                self.gen.asm.append("\t.string "+v+'\n')
            else:
                self.gen.asm.append("\t.double"+str(v)+'\n')

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
        self.localOffset=space-reserve
        map={}
        map.update({0:{'reg':0,'type':None,'addr':0}})
        for v in global_context.local[funcName].compound_statement.context.local:
            value=global_context.local[funcName].compound_statement.context.local[v]
            s_class=value.storage_class
            Type=value.type
            print(type(value))
            size=value.Size()
            # if(Type == 'struct'):
            #     st=self.__parseStruct(v,value)
            #     for member in st:
            #         Type = st[member].type
            #         if(Type == 'double'):
            #             size=8
            #         else:
            #             size=4
            #         map.update({member:{'reg':0,'type':Type,'addr':'[esp+%d]'%(offset-size)}})
            #         offset-=size
            #     continue
            if(s_class == 'static'):
                v=v+'%d' % self.magicNum
                self.magicNum+=4
                map.update({v:{'reg':0,'type':Type,'addr':v}})
                self.currentStatic.update({v:Type})
                self.statics.update({v:Type})
                continue
            map.update({v:{'reg':0,'type':Type,'addr':'[esp+%d]'%(self.localOffset-size)}})
            self.localOffset-=size
        for v in self.globalV:
            map.update({v:{'reg':0,'type':self.globalV[v],'addr':v}})
        self.dirty={'ebx':0,'ecx':0,'edx':0,'esi':0,'edi':0}
        return map
    
    def newFunc(self,funcName):
        space=64
        self.funcName=funcName
        self.gen.asm.append('\t.globl '+funcName+'\n')
        self.gen.asm.append('\t.type '+funcName+', @function\n')
        self.gen.asm.append(funcName+':\n')
        self.gen.asm.append('\tpush ebp\n')
        self.gen.asm.append('\tmov ebp, esp\n')
        self.gen.asm.append('\tsub esp, %d\n' % space)
        self.currentMap=self.newMap(funcName)
        self.tmpSP=self.localOffset-size
        print("ok~~~")
    

    def endFunc(self):
        self.showMap()
        self.gen.asm.append('\t.size '+self.funcName+', .-'+self.funcName+'\n')
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
                    v=v+'%d' % self.magicNum
                    self.magicNum+=4
                    map.update({v:{'reg':0,'type':Type,'addr':v}})
                    self.currentStatic.update({v:Type})
                    self.statics.update({v:Type})
                    continue
                map.update({v:{'reg':0,'type':Type,'addr':'[esp+%d]'%(self.localOffset-size)}})
                self.localOffset-=size
        return

        raise TypeError("error in newScope!\n")
    
    def endScope(self):
        self.currentMap=self.mapStack.pop()
        
        return

    def getTrue():
        return 'true'
    
    def getFalse():
        return 'false'

    def ret(self,returnV=None):
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
            if(self.registers[reg]==0):
                return reg
        return -1

    def getAbsoluteAdd(self,data):
        # base=int(re.findall('[1-9]+',self.currentMap[data.name]['addr'])[0])
        if(data.name==0):
            return '[eax]'
        if(data.offset):
            index=self.currentMap[data.name]['addr'].find('p')+1
            strAddr=self.currentMap[data.name]['addr'][:index]+'+eax+'+self.currentMap[data.name]['addr'][index:]
            return strAddr
        
        return self.currentMap[data.name]['addr']
        
    
    def allocateNewReg(self,vName=1):
        """
            get a new free reg, if full get a mem address
        """
        if(vName in self.currentMap):
            Type=self.currentMap[vName]['Type']
        elif(isinstance(vName,str)):
            if(vName=='eax'):
                Type='int'
            else:
                Type='double'
        elif(isinstance(vName,int)):
            Type='int'
        elif(isinstance(vName,float)):
            Type='double'
        else:
            raise TypeError("error in allocateNewReg\n")

        if(Type=='double'):
            return
        
        newTmp=self.tmpName+str(self.tmpNum)
        self.tmpNum+=1
        reg=self.checkFull()
        if(reg!=-1):
            self.currentMap.update({newTmp:{'reg':reg,'type':Type,'addr':0}})
            return reg
        else:
            self.currentMap.update({newTmp:{'reg':0,'type':Type,'addr':'[esp+%d]'%(self.tmpSP)}})
            return newTmp
        


    def lock(self,name):
        if(name in self.registers):
            self.registers[name]=1
            return

        if(self.currentMap[name]['type']=='double'):
            self.tmpSP-=8
        else:
            self.tmpSP-=4
        
        return
    
    def unLock(self,name):
        if(name in self.registers):
            self.registers[name]=0
            return

        if(self.currentMap[name]['type']=='double'):
            self.tmpSP+=8
        else:
            self.tmpSP+=4
        
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
    
    def checkIsFloat(self,x1,x2):
        isFloat=False

        if(isinstance(x1,Data)):
            isFloat=(x1.type.type=='double')
        elif(isinstance(x1,str)):
            isFloat=(x1=='st')
        elif(isinstance(x1,float)):
            isFloat=True
        else:
            pass
        
        if(isinstance(x2,Data)):
            isFloat=(x2.type.type=='double')
        elif(isinstance(x2,str)):
            isFloat=(x2=='st')
        elif(isinstance(x2,float)):
            isFloat=True
        else:
            pass

    def __vPush(self,reg):
        addr='[esp+%d] '%self.tmpSP+reg
        self.gen.asm.append('\tmov '+addr)
        self.tmpSP-=4
        return addr
    
    def __vPop(self,reg):
        self.tmpSP+=4

    def add(self,x1,x2):
        isFloat=self.checkIsFloat(x1,x2)
        
        if(not isFloat):
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                self.gen.asm.append("\tadd eax, "+x2addr+'\n')
            elif(isinstance(x1,Data)):
                if(x2!='eax'):
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    self.gen.asm.append("\tadd eax, "+x2+'\n')
                else:
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\tadd eax, "+x1addr+'\n')
            elif(isinstance(x2,Data)):
                if(x1!='eax'):
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tadd eax, "+x1+'\n')
                else:
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tadd eax, "+x2addr+'\n')
            else:
                if(x1=='eax'):
                    self.gen.asm.append("\tadd eax, "+x2+'\n')
                else:
                    self.gen.asm.append("\tmov eax, "+x1+'\n')
                    self.gen.asm.append("\tadd eax, "+x2+'\n')
            
            return 'eax'
        
        else:
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                type1=x1.type.type
                type2=x2.type.type
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                if(type1=='double' and type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfadd QWORD PTR "+x2addr+"\n")
                elif(type1=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfiadd DWORD PTR "+x2addr+"\n")
                elif(type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                    self.gen.asm.append("\tfiadd DWORD PTR "+x1addr+"\n")
            elif(isinstance(x1,Data)):
                type1=x1.type.type
                x1addr=self.getAbsoluteAdd(x1)
                if(x2 in self.registers):
                    if(type1=='double' and x2=='st'):
                        self.gen.asm.append("\tfadd QWORD PTR "+x1addr+"\n")
                    elif(type1=='double'):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfiadd DWORD PTR "+x2addr+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfadd QWORD PTR "+x1addr+"\n")
                # x2 is imm
                else:
                    if(type1!='double'):
                        x2=int(x2)
                    if(type1=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x2]+"\n")
                        self.gen.asm.append("\tfaddp"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                        self.gen.asm.append("\tadd eax, "+x2+'\n')
            elif(isinstance(x2,Data)):
                type2=x2.type.type
                x2addr=self.getAbsoluteAdd(x2)
                if(x1 in self.registers):
                    if(type2=='double' and x1=='st'):
                        self.gen.asm.append("\tfadd QWORD PTR "+x2addr+"\n")
                    elif(type2=='double'):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                        self.gen.asm.append("\tfiadd DWORD PTR "+x1addr+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfadd QWORD PTR "+x2addr+"\n")
                # x2 is imm
                else:
                    if(type2!='double'):
                        x1=int(x1)
                    if(type2=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x1]+"\n")
                        self.gen.asm.append("\tfaddp"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                        self.gen.asm.append("\tadd eax, "+x1+'\n')
            else:
                if(x1 != 'st'):
                    if(x2 in self.registers):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfiadd DWORD PTR "+x1addr+"\n")
                        self.__vPop()
                    else:
                        x2=int(x2)
                        self.gen.asm.append("\tmov eax, "+x1+'\n')
                        self.gen.asm.append("\tadd eax, "+str(x2)+'\n')
                else:
                    if(x2 in self.registers):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfiadd DWORD PTR "+x2addr+"\n")
                        self.__vPop()
                    else:
                        pass
           
            return 'st'                    

        # y1=None
        # y2=None
        # if(isinstance(x1,Data)):
        #     y1addr=self.getAbsoluteAdd(x1)
        #     y1=x1.name
        # if(isinstance(x2,Data)):
        #     y2addr=self.getAbsoluteAdd(x2)
        #     y2=x2.name
        # #x2 is not a imm
        # if(x2=='eax'):
        #     tmp=y1
        #     y1=y2
        #     y2=tmp
        #     tmp=y1addr
        #     y1addr=y2addr
        #     y2addr=tmp  

        # if(y1 in self.currentMap and y2 in self.currentMap):
        #     self.gen.asm.append("\tmov eax, "+y1addr+'\n')
        #     self.gen.asm.append("\tadd eax, "+y2addr+'\n')
        # elif(isinstance(y2,str)):
        #     if(y2 in self.currentMap):
        #         self.gen.asm.append('\tadd eax, '+y2addr+'\n')
        #     else:
        #         self.gen.asm.append('\tadd eax, '+y2+'\n')
        # else:
        #     if(y2 in self.currentMap):
        #         self.gen.asm.append("\tmov eax, "+y1addr+'\n')
        #     self.gen.asm.append("\tadd eax, "+str(y2)+'\n')
        # return 'eax'
    
    # def addToTmp(self):
    #     '''
    #     perform bx=bx+ax
    #     bx is a tmp reg
    #     deal with assignment like a=func(b)+func(c)+...
    #     '''
    #     self.gen.asm.append('\tadd ebx eax\n')
    
    def sub(self,x1,x2):
        isFloat=self.checkIsFloat(x1,x2)

        if(not isFloat):
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                self.gen.asm.append("\tsub eax, "+x2addr+'\n')
            elif(isinstance(x1,Data)):
                if(x2!='eax'):
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    self.gen.asm.append("\tsub eax, "+x2+'\n')
                else:
                    x1addr=self.getAbsoluteAdd(x1)
                    reg=self.allocateNewReg('eax')
                    self.gen.asm.append("\tmov "+reg+", "+'eax'+'\n')
                    self.gen.asm.append("\tadd "+reg+", "+x1addr+'\n')
                    self.gen.asm.append("\tmov eax, "+reg+'\n')
            elif(isinstance(x2,Data)):
                if(x1!='eax'):
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tsub eax, "+x1+'\n')
                else:
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tsub eax, "+x2addr+'\n')
            else:
                if(x1=='eax'):
                    self.gen.asm.append("\tsub eax, "+x2+'\n')
                else:
                    self.gen.asm.append("\tmov eax, "+x1+'\n')
                    self.gen.asm.append("\tsub eax, "+x2+'\n')
        
            return 'eax'

        else:
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                type1=x1.type.type
                type2=x2.type.type
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                if(type1=='double' and type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfsub QWORD PTR "+x2addr+"\n")
                elif(type1=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfisub DWORD PTR "+x2addr+"\n")
                elif(type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfild DWORD PTR "+x2addr+"\n")
                    self.gen.asm.append("\tfsubp st(1), st"+"\n")
            elif(isinstance(x1,Data)):
                type1=x1.type.type
                x1addr=self.getAbsoluteAdd(x1)
                if(x2 in self.registers):
                    if(type1=='double' and x2=='st'):
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfsubp st(1), st"+"\n")
                    elif(type1=='double'):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfisub DWORD PTR "+x2addr+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfld DWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfsubp st(1), st"+"\n")
                # x2 is imm
                else:
                    if(type1!='double'):
                        x2=int(x2)
                    if(type1=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x2]+"\n")
                        self.gen.asm.append("\tfsubp st(1), st"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                        self.gen.asm.append("\tsub eax, "+x2+'\n')
            elif(isinstance(x2,Data)):
                type2=x2.type.type
                x2addr=self.getAbsoluteAdd(x2)
                if(x1 in self.registers):
                    if(type2=='double' and x1=='st'):
                        self.gen.asm.append("\tfsub QWORD PTR "+x2addr+"\n")
                    elif(type2=='double'):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld DWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                        self.gen.asm.append("\tfsubp st(1), st "+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfsub QWORD PTR "+x2addr+"\n")
                # x2 is imm
                else:
                    if(type2!='double'):
                        x1=int(x1)
                    if(type2=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x1]+"\n")
                        self.gen.asm.append("\tfsub st, st(1)"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x1+'\n')
                        self.gen.asm.append("\tsub eax, "+x2addr+'\n')
            else:
                if(x1 != 'st'):
                    if(x2 in self.registers):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld DWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfsub st, st(1)"+"\n")
                        self.__vPop()
                    else:
                        x2=int(x2)
                        self.gen.asm.append("\tmov eax, "+x1+'\n')
                        self.gen.asm.append("\tsub eax, "+str(x2)+'\n')
                else:
                    if(x2 in self.registers):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfisub DWORD PTR "+x2addr+"\n")
                        self.__vPop()
                    else:
                        pass 
            
            return 'st'   
                          
        # if(isinstance(x1,Data)):
        #     x1addr=self.getAbsoluteAdd(x1)
        #     x1=x1.name
        # if(isinstance(x2,Data)):
        #     x2addr=self.getAbsoluteAdd(x2)
        #     x2=x2.name
        # #x2 is not a imm
        # if(x2=='eax'):
        #     self.gen.asm.append("\tsub "+x1+', '+'eax'+'\n')
        #     self.gen.asm.append('\tmov eax, '+x1+'\n')
        # if(x1 in self.currentMap and x2 in self.currentMap):
        #     self.gen.asm.append("\tmov eax, "+x1addr+'\n')
        #     self.gen.asm.append("\tsub eax, "+x2addr+'\n')
        # elif(isinstance(x2,str)):
        #     if(x2 in self.currentMap):
        #         self.gen.asm.append('\tsub eax, '+x2addr+'\n')
        #     else:
        #         self.gen.asm.append('\tsub eax, '+x2+'\n')
        # else:
        #     if(x2 in self.currentMap):
        #         self.gen.asm.append("\tmov eax, "+x1addr+'\n')
        #     self.gen.asm.append("\tsub eax, "+str(x2)+'\n')
        # return 'eax'
    
    # def subTmp(self):
    #     '''
    #     perform bx=bx-ax
    #     bx is a tmp reg
    #     deal with assignment like a=func(b)-func(c)-...
    #     '''
    #     self.gen.asm.append('\tsub ebx eax\n')
    
    def mul(self,x1,x2,returnSpace):
        if(isinstance(x1,Data)):
            x1addr=self.getAbsoluteAdd(x1)
            x1=x1.name
        if(isinstance(x2,Data)):
            x2addr=self.getAbsoluteAdd(x2)
            x2=x2.name

        #mem mem
        if(x1 in self.currentMap):
            # returnSpace is reg
            if(returnSpace in self.registers):
                self.gen.asm.append("\tmov "+newSpace+", "+x1addr+'\n')
                self.gen.asm.append("\tmul "+newSpace+", "+x2addr+'\n')
            #returnSpace is mem
            else:
                self.gen.asm.append("\tmov "+"eax"+", "+x1addr+'\n')
                self.gen.asm.append("\tmul "+"eax"+", "+x2addr+'\n')
                self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            
        else:
            if(x1==returnSpace):
                self.gen.asm.append("\tmul "+returnSpace+", "+x2addr+'\n')
            else:
                self.gen.asm.append("\tmov "+returnSpace+", "+x1+'\n')
                self.gen.asm.append("\tmul "+returnSpace+", "+x1addr+'\n')
        
        return returnSpace        


    def div(self,x1,x2,returnSpace):
        if(isinstance(x1,Data)):
            x1addr=self.getAbsoluteAdd(x1)
            x1=x1.name
        if(isinstance(x2,Data)):
            x2addr=self.getAbsoluteAdd(x2)
            x2=x2.name

        #mem mem
        if(x1 in self.currentMap):
            if(returnSpace in self.registers):
                self.gen.asm.append("\tmov "+"eax"+", "+x1addr+'\n')
                self.gen.asm.append("cdq")
                self.gen.asm.append("\tidiv "+x1addr+'\n')
                self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            
        else:
            if(x1==returnSpace):
                if(x1=='eax'):
                    self.gen.asm.append("cdq")
                    self.gen.asm.append("\tidiv "+returnSpace+", "+x2addr+'\n')
                else:
                    self.gen.asm.append("\tmov "+"eax"+", "+x1+'\n')
                    self.gen.asm.append("cdq")
                    self.gen.asm.append("\tidiv"+x2addr+'\n')
                    self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            else:
                self.gen.asm.append("\tmov "+"eax"+", "+x1+'\n')
                self.gen.asm.append("cdq")
                self.gen.asm.append("\tidiv"+x2addr+'\n')
                self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
        
        return returnSpace  

    def mov(self,x1,x2):
        l1=None
        l2=None
        if(isinstance(x1,Data)):
            x1addr=self.getAbsoluteAdd(x1)
            l1=x1.name
        if(isinstance(x2,Data)):
            x2addr=self.getAbsoluteAdd(x2)
            l2=x2.name

        if(l1 in self.currentMap and l2 in self.currentMap):
            self.gen.asm.append("\tmov eax, "+x2addr+'\n')
            self.gen.asm.append("\tmov "+x2addr+' eax'+'\n')
        elif(isinstance(x2,Data)):
            self.gen.asm.append('\tmov '+x1+', '+x2addr+'\n')
        elif(isinstance(x1,Data)):
            if(isinstance(x2,int)):
                self.gen.asm.append('\tmov '+x1addr+', %d'%x2+'\n')
            else:
                print(x1addr)
                self.gen.asm.append('\tmov '+x1addr+', '+x2+'\n')
        else:
            if(isinstance(x2,int)):
                self.gen.asm.append('\tmov '+x1+', %d'%x2+'\n')
            else:
                self.gen.asm.append('\tmov '+x1+', '+x2+'\n')
        return x1
        
    def passPara(self,para):
            if(para in self.registers):
                self.gen.asm.append('\tmov BYTE DWORD '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                return
            print(para)
            if(isinstance(para,Data)):
                Type=para.type.type
                if(Type=='char'):
                    self.gen.asm.append('\tmov BYTE PTR '+"eax, "+self.currentMap[para.name]['addr']+'\n')
                    self.gen.asm.append('\tmov BYTE PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
                elif(Type=='short'):
                    self.gen.asm.append('\tmov WORD PTR '+"eax, "+self.currentMap[para.name]['addr']+'\n')
                    self.gen.asm.append('\tmov WORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
                elif(Type=='int'):
                    self.gen.asm.append('\tmov DWORD PTR '+"eax, "+self.currentMap[para.name]['addr']+'\n')
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
                elif(Type=='const int'):
                    source=int(para)
                    self.callOffset+=4
                elif(Type=='const char'):
                    source=char(para)
                elif(Type=='struct'):
                    for i in range(0,para.size/4+1):
                        base=int(re.findall('[1-9]+',self.currentMap[para.name]['addr'])[0])
                        addr=i*4+base
                        strAddr=self.currentMap[para.name]['addr'].replace(str(base),str(addr))
                        self.gen.asm.append('\tmov DWORD PTR '+"eax, "+strAddr+'\n')
                        self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                        self.callOffset+=4
                else:
                    raise TypeError("error in passPara")
            else:
                if(isinstance(para,str)):
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+self.constMap[para]+'\n')
                    self.callOffset+=4
                elif(isinstance(para,float)):
                    pass
                else:
                    raise TypeError('error in passPara\n')
            
            return
            
            # if(self.callOffset==0):
            #     self.gen.asm.append('[esp], ')
            # else:
            #     self.gen.asm.append('[esp+%d], '%self.callOffset)
            # if(source==None):
            #     checkIn(para)
            #     source=self.currentMap[para]['reg']
            # self.gen.asm.append(source+'\n')

    def getEax(self):
        return "eax"
    
    def getNull(self):
        return 0
        

    def call(self,func,parameters=None):
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
        if(isinstance(func,Data)):
            self.gen.asm.append('\tcall '+func.name+'\n')
        else:
            self.gen.asm.append('\tcall '+func+'\n')
    
    def And(self,x1,x2):
        if(isinstance(x1,Data)):
            y1addr=self.getAbsoluteAdd(x1)
            y1=x1.name
        if(isinstance(x2,Data)):
            y2addr=self.getAbsoluteAdd(x2)
            y2=x2.name
        #x2 is not a imm
        if(x2=='eax'):
            tmp=y1
            y1=y2
            y2=tmp
            tmp=y1addr
            y1addr=y2addr
            y2addr=tmp  

        if(y1 in self.currentMap and y2 in self.currentMap):
            self.gen.asm.append("\tmov eax, "+y1addr+'\n')
            self.gen.asm.append("\tand eax, "+y2addr+'\n')
        elif(isinstance(y2,str)):
            if(y2 in self.currentMap):
                self.gen.asm.append('\tand eax, '+y2addr+'\n')
            else:
                self.gen.asm.append('\tand eax, '+y2+'\n')
        else:
            if(y2 in self.currentMap):
                self.gen.asm.append("\tmov eax, "+y1addr+'\n')
            self.gen.asm.append("\tand eax, "+str(y2)+'\n')
        return 'eax'
        
    def Or(self,x1,x2):
        if(isinstance(x1,Data)):
            y1addr=self.getAbsoluteAdd(x1)
            y1=x1.name
        if(isinstance(x2,Data)):
            y2addr=self.getAbsoluteAdd(x2)
            y2=x2.name
        #x2 is not a imm
        if(x2=='eax'):
            tmp=y1
            y1=y2
            y2=tmp
            tmp=y1addr
            y1addr=y2addr
            y2addr=tmp  
        if(y1 in self.currentMap and y2 in self.currentMap):
            self.gen.asm.append("\tmov eax, "+y1addr+'\n')
            self.gen.asm.append("\tor eax, "+y2addr+'\n')
        elif(isinstance(y2,str)):
            if(y2 in self.currentMap):
                self.gen.asm.append('\tor eax, '+y2addr+'\n')
            else:
                self.gen.asm.append('\tor eax, '+y2+'\n')
        else:
            if(y2 in self.currentMap):
                self.gen.asm.append("\tmov eax, "+y1addr+'\n')
            self.gen.asm.append("\tor eax, "+str(y2)+'\n')
        return 'eax'
        
    def nor(self,x1,x2):
        if(isinstance(x1,Data)):
            y1addr=self.getAbsoluteAdd(x1)
            y1=x1.name
        if(isinstance(x2,Data)):
            y2addr=self.getAbsoluteAdd(x2)
            y2=x2.name
        #x2 is not a imm
        if(x2=='eax'):
            tmp=y1
            y1=y2
            y2=tmp
            tmp=y1addr
            y1addr=y2addr
            y2addr=tmp  
        if(y1 in self.currentMap and y2 in self.currentMap):
            self.gen.asm.append("\tmov eax, "+y1addr+'\n')
            self.gen.asm.append("\tnor eax, "+y2addr+'\n')
        elif(isinstance(y2,str)):
            if(y2 in self.currentMap):
                self.gen.asm.append('\tnor eax, '+y2addr+'\n')
            else:
                self.gen.asm.append('\tnor eax, '+y2+'\n')
        else:
            if(y2 in self.currentMap):
                self.gen.asm.append("\tmov eax, "+y1addr+'\n')
            self.gen.asm.append("\tnor eax, "+str(y2)+'\n')
        return 'eax'
        
    def Not(self,x1):
        x1addr=self.getAbsoluteAdd(x1)
        self.gen.asm.append("\tnot eax, "+x1addr+'\n')
        return 'eax'
    
    def markLabel(self,label=None):
        """
        give a label at current place
        mostly use at loop
        """
        if(label==None):
            label='.LC%d'%self.magicNum
            self.magicNum+=1
        self.gen.asm.append(label+':\n')
    
    def allocateLabel(self):
        self.magicNum+=1
        return '.LC%d'%self.magicNum

    def lea(self,x):
        if(isinstance(x,Data)):
            xaddr=self.getAbsoluteAdd(x)
        if(x in self.registers):
            self.gen.asm.append('\tlea '+'eax '+'['+x+']'+'\n')
        else:
            self.gen.asm.append('\tlea '+'eax '+xaddr+'\n')
        return 'eax'
    
    def cmp(self,x1,x2):
        if(isinstance(x1,Data)):
            x1addr=self.getAbsoluteAdd(x1)
            x1=x1.name
        if(isinstance(x2,Data)):
            x2addr=self.getAbsoluteAdd(x2)
            x2=x2.name
        if(x1 in self.currentMap and x2 in self.currentMap):
            self.gen.asm.append("\tmov eax, "+x1addr+'\n')
            self.gen.asm.append('\tcmp '+'eax'+', '+x2+'\n')
            return

        self.gen.asm.append('\tcmp '+x1+', '+x2+'\n')
        return 
    
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

    def jmp(self,label):
        self.gen.asm.append('\tjne '+label+'\n')
    
    def loop(self,label):
        self.gen.asm.append('\tloop '+label+'\n')
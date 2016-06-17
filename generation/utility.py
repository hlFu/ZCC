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
        self.registers={'eax':1,'st':1,'ebx':0,'ecx':0,'edx':0}
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
        self.paraOffset=0

        
    def globalInitialize(self):
        self.gen.asm.append('\t.intel_syntax noprefix\n')
        for key in global_context.local:
            value = global_context.local[key]
            if(value.type!='function'):
                # if(value.type=='struct'):
                #     size=value.Size()
                #     # st=self.__parseStruct(key,value)
                #     # size=0
                #     # for member in st:
                #     #     if(st[member].type!='double'):
                #     #         size+=4
                #     #     else:
                #     #         size+=8
                #     # self.globalV.update(st)
                #     self.gen.asm.append('\t.comm '+key+',%d,4\n' %(size))
                #     continue
                if(value.storage_class=='static'):
                    self.gen.asm.append('\t.local '+key+'\n')
                self.gen.asm.append('\t.comm '+key+',%d,4\n' %(value.Size()))
                self.globalV.update({key:value})
        self.gen.asm.append('\t.section .rodata\n')
        #get const string and double
        for v in global_context.literal:
            try:
                v=float(v)
            except:
                pass
            self.constMap.update({v:(self.constName+str(self.magicNum))})
            self.magicNum+=1
            self.gen.asm.append(self.constMap[v]+":"+'\n')
            if(isinstance(v,str)):
                self.gen.asm.append("\t.string "+v+'\n')
            else:
                self.gen.asm.append("\t.double "+str(v)+'\n')

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

    def newMap(self,funcName,space=32,reserve=12):
        self.localOffset=space-reserve
        map={}
        map.update({0:{'reg':0,'type':None,'addr':0}})
        for v in global_context.local[funcName].compound_statement.context.local:
            value=global_context.local[funcName].compound_statement.context.local[v]
            s_class=value.storage_class
            Type=value.type
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
        space=500
        self.funcName=funcName
        self.gen.asm.append('\t.globl '+funcName+'\n')
        self.gen.asm.append('\t.type '+funcName+', @function\n')
        self.gen.asm.append(funcName+':\n')
        self.gen.asm.append('\tpush ebp\n')
        self.gen.asm.append('\tmov ebp, esp\n')
        self.gen.asm.append('\tsub esp, %d\n' % space)
        if(funcName!='main'):
            self.gen.asm.append('\tmov [ebp-4], ebx\n')
            self.gen.asm.append('\tmov [ebp-8], ecx\n')
            self.gen.asm.append('\tmov [ebp-12], edx\n')
        self.currentMap=self.newMap(funcName,space)
        self.getParaList(funcName)
        self.tmpSP=self.localOffset-8


    def endFunc(self):
        self.gen.asm.append('\t.size '+self.funcName+', .-'+self.funcName+'\n')
        pass
    
    def newScope(self,scope):
        self.mapStack.append(self.currentMap)
        if(isinstance(scope,Context)):
            for v in scope.local:
                value=scope.local[v]
                s_class=value.storage_class
                Type=value.type
                size=value.Size()
                if(s_class == 'static'):
                    v=v+'%d' % self.magicNum
                    self.magicNum+=4
                    self.currentMap.update({v:{'reg':0,'type':Type,'addr':v}})
                    self.currentStatic.update({v:Type})
                    self.statics.update({v:Type})
                    continue
                self.currentMap.update({v:{'reg':0,'type':Type,'addr':'[esp+%d]'%(self.localOffset-size)}})
                self.localOffset-=size
        return


    def endScope(self):
        self.currentMap=self.mapStack.pop()
        
        return

    def getTrue(self):
        return 1
    
    def getFalse(self):
        return 0

    def ret(self,returnV=None):
        # for v in self.currentStatic:
        #     if(self.currentMap[v]['reg']!=0):
        #         self.gen.asm.append('\tmov '+v+', '+self.currentMap[v]['reg'])
        # for v in self.globalV:
        #     if(self.currentMap[v]['reg']!=0):
        #         self.gen.asm.append('\tmov '+v+', '+self.currentMap[v]['reg'])
        # if(returnV!=None and self.currentMap[returnV]['reg']!='eax' and self.currentMap[returnV]['reg']!=0):
        #     self.gen.asm.append('\tmov eax, '+self.currentMap[returnV]['reg'])
        if(self.funcName=='main'):
            self.gen.asm.append('\tleave\n')
        else:
            index=self.findLast(self.gen.asm,'\tpush ebp\n')
            if self.funcName!="main":
                self.gen.asm.append('\tmov ebx, [ebp-4]\n')
                self.gen.asm.append('\tmov ecx, [ebp-8]\n')
                self.gen.asm.append('\tmov edx, [ebp-12]\n')
            # for reg in self.dirty:
            #     if(self.dirty[reg]!=0):
            #         self.gen.asm.insert(index,'\tpush '+reg+'\n')
            #         self.gen.asm.append('\tpop '+reg+'\n')
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
            addr=self.currentMap[data.name]['addr']
            if(addr[0]!='['):
                return addr+'[eax]'
            index=addr.find('p')+1
            strAddr=addr[:index]+'+eax'+addr[index:]
            return strAddr
        
        return self.currentMap[data.name]['addr']
        
    
    def allocateNewReg(self,vName):
        """
            get a new free reg, if full get a mem address
        """
        if(isinstance(vName,Data)):
            Type=vName.type.type
        # if(vName in self.currentMap):
        #     Type=self.currentMap[vName]['Type']
        elif(vName in self.registers):
            if(vName=='eax'):
                Type='int'
            elif(vName=='st'):
                Type='double'
        elif(isinstance(vName,int)):
            Type='int'
        elif(isinstance(vName,float)):
            Type='double'
        else:
            raise TypeError("error in allocateNewReg\n")

        if(Type=='double'):
            newTmp=self.tmpName+str(self.tmpNum)
            self.tmpNum+=1
            self.currentMap.update({newTmp:{'reg':0,'type':Type,'addr':'[esp+%d]'%(self.tmpSP)}})
            newType=CType('double',8)
            newTmp=Data(newTmp,False,newType)
            return newTmp
        
        
        reg=self.checkFull()
        if(reg!=-1):
            newTmp=self.tmpName+str(self.tmpNum)
            self.tmpNum+=1
            self.currentMap.update({newTmp:{'reg':reg,'type':Type,'addr':0}})
            return reg
        else:
            newTmp=self.tmpName+str(self.tmpNum)
            self.tmpNum+=1
            self.currentMap.update({newTmp:{'reg':0,'type':Type,'addr':'[esp+%d]'%(self.tmpSP)}})
            newType=CType('int',4)
            newTmp=Data(newTmp,False,newType)
            return newTmp

    def lock(self,name):
        if(name in self.registers):
            self.registers[name]=1
            return

        self.tmpSP-=8
        
        return
    
    def unLock(self,name):
        if(name in self.registers):
            self.registers[name]=0
            return

        self.tmpSP+=8
        
        self.currentMap.pop(name.name)
        
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
        if isFloat:
            return isFloat
        
        if(isinstance(x2,Data)):
            isFloat=(x2.type.type=='double')
        elif(isinstance(x2,str)):
            isFloat=(x2=='st')
        elif(isinstance(x2,float)):
            isFloat=True
        else:
            pass
        return isFloat

    def __vPush(self,reg):
        addr='[esp+%d] '%self.tmpSP
        self.gen.asm.append('\tfstp QWORD PTR '+addr+'\n')
        self.tmpSP-=8
        return addr
    
    def __vPop(self):
        self.tmpSP+=8

    def add(self,x1,x2):
        isFloat=self.checkIsFloat(x1,x2)
        
        if(isinstance(x1,Data)):
            pointNum=x1.type.pointer_count() 
            x1addr=self.getAbsoluteAdd(x1)
            if(pointNum==1):
                if(isinstance(x2,Data)):
                    x2addr=self.getAbsoluteAdd(x2)
                    # reg=self.allocateNewReg(x2)
                    # if(reg in self.registers):
                    #     self.gen.asm.append("\tmov "+reg+", "+x2addr+'\n')
                    #     self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    #     self.gen.asm.append("\tlea eax, "+'[%d*'%(int(x2.type.size/2))+reg+'+eax]'+'\n')
                    # else:
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tsal eax, "+str(int(x1.type.size/2))+'\n')
                    self.gen.asm.append("\tadd eax, "+x1addr+'\n')
                else:
                    size=x2*x1.type.size
                    self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    self.gen.asm.append("\tadd eax, "+str(size)+'\n')
                return 'eax'
            elif(pointNum>1):
                if(isinstance(x2,Data)):
                    x2addr=self.getAbsoluteAdd(x2)
                    # reg=self.allocateNewReg(x2)
                    # if(reg in self.registers):
                    #     self.gen.asm.append("\tmov "+reg+", "+x2addr+'\n')
                    #     self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    #     self.gen.asm.append("\tlea eax, "+'[%d*'%(int(x2.type.size/2))+reg+'+eax]'+'\n')
                    # else:
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tsal eax, "+str(2)+'\n')
                    self.gen.asm.append("\tadd eax, "+x1addr+'\n')
                else:
                    size=4*x2
                    self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    self.gen.asm.append("\tadd eax, "+str(size)+'\n')
                return 'eax'

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
                    self.gen.asm.append("\tadd eax, "+str(x2)+'\n')
                else:
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\tadd eax, "+x1addr+'\n')
            elif(isinstance(x2,Data)):
                if(x1!='eax'):
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tadd eax, "+str(x1)+'\n')
                else:
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tadd eax, "+x2addr+'\n')
            else:
                if(x1=='eax'):
                    self.gen.asm.append("\tadd eax, "+str(x2)+'\n')
                elif(x2=='eax'):
                    self.gen.asm.append("\tadd eax, "+str(x1)+'\n')
                else:
                    self.gen.asm.append("\tmov eax, "+str(x1)+'\n')
                    self.gen.asm.append("\tadd eax, "+str(x2)+'\n')

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
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x2]+"\n")
                        self.gen.asm.append("\tfaddp"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                        self.gen.asm.append("\tadd eax, "+str(x2)+'\n')
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
                    self.gen.asm.append("\tsub eax, "+str(x2)+'\n')
                else:
                    x1addr=self.getAbsoluteAdd(x1)
                    reg=self.allocateNewReg('eax')
                    self.gen.asm.append("\tmov "+reg+", "+x1addr+'\n')
                    self.gen.asm.append("\tsub "+reg+", "+'eax'+'\n')
                    self.gen.asm.append("\tmov eax, "+reg+'\n')
            elif(isinstance(x2,Data)):
                if(x1!='eax'):
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tsub eax, "+str(x1)+'\n')
                else:
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tsub eax, "+x2addr+'\n')
            else:
                if(x1=='eax'):
                    self.gen.asm.append("\tsub eax, "+str(x2)+'\n')
                else:
                    self.gen.asm.append("\tmov eax, "+str(x1)+'\n')
                    self.gen.asm.append("\tsub eax, "+str(x2)+'\n')
        
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
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfsubp st(1), st"+"\n")
                # x2 is imm
                else:
                    if(type1!='double'):
                        x2=int(x2)
                    if(type1=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x2]+"\n")
                        self.gen.asm.append("\tfsubp st(1), st"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                        self.gen.asm.append("\tsub eax, "+str(x2)+'\n')
            elif(isinstance(x2,Data)):
                type2=x2.type.type
                x2addr=self.getAbsoluteAdd(x2)
                if(x1 in self.registers):
                    if(type2=='double' and x1=='st'):
                        self.gen.asm.append("\tfsub QWORD PTR "+x2addr+"\n")
                    elif(type2=='double'):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
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
                        self.gen.asm.append("\tmov eax, "+str(x1)+'\n')
                        self.gen.asm.append("\tsub eax, "+x2addr+'\n')
            else:
                if(x1 != 'st'):
                    if(x2 in self.registers):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
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
    
    def mul(self,x1,x2):
        isFloat=self.checkIsFloat(x1,x2)
        
        if(not isFloat):
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                self.gen.asm.append("\timul eax, "+x2addr+'\n')
            elif(isinstance(x1,Data)):
                if(x2!='eax'):
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    self.gen.asm.append("\timul eax, "+str(x2)+'\n')
                else:
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\timul eax, "+x1addr+'\n')
            elif(isinstance(x2,Data)):
                if(x1!='eax'):
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\timul eax, "+str(x1)+'\n')
                else:
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\timul eax, "+x2addr+'\n')
            else:
                if(x1=='eax'):
                    self.gen.asm.append("\timul eax, "+str(x2)+'\n')
                elif(x2=='eax'):
                    self.gen.asm.append("\timul eax, "+str(x1)+'\n')
                else:
                    self.gen.asm.append("\tmov eax, "+str(x1)+'\n')
                    self.gen.asm.append("\timul eax, "+str(x2)+'\n')
            
            return 'eax'
        
        else:
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                type1=x1.type.type
                type2=x2.type.type
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                if(type1=='double' and type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfmul QWORD PTR "+x2addr+"\n")
                elif(type1=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfimul DWORD PTR "+x2addr+"\n")
                elif(type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                    self.gen.asm.append("\tfimul DWORD PTR "+x1addr+"\n")
            elif(isinstance(x1,Data)):
                type1=x1.type.type
                x1addr=self.getAbsoluteAdd(x1)
                if(x2 in self.registers):
                    if(type1=='double' and x2=='st'):
                        self.gen.asm.append("\tfmul QWORD PTR "+x1addr+"\n")
                    elif(type1=='double'):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfimul DWORD PTR "+x2addr+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfmul QWORD PTR "+x1addr+"\n")
                # x2 is imm
                else:
                    if(type1!='double'):
                        x2=int(x2)
                    if(type1=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x2]+"\n")
                        self.gen.asm.append("\tfmulp"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                        self.gen.asm.append("\timul eax, "+str(x2)+'\n')
            elif(isinstance(x2,Data)):
                type2=x2.type.type
                x2addr=self.getAbsoluteAdd(x2)
                if(x1 in self.registers):
                    if(type2=='double' and x1=='st'):
                        self.gen.asm.append("\tfmul QWORD PTR "+x2addr+"\n")
                    elif(type2=='double'):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                        self.gen.asm.append("\tfimul DWORD PTR "+x1addr+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfmul QWORD PTR "+x2addr+"\n")
                # x2 is imm
                else:
                    if(type2!='double'):
                        x1=int(x1)
                    if(type2=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x1]+"\n")
                        self.gen.asm.append("\tfmulp"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                        self.gen.asm.append("\timul eax, "+str(x1)+'\n')
            else:
                if(x1 != 'st'):
                    if(x2 in self.registers):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfimul DWORD PTR "+x1addr+"\n")
                        self.__vPop()
                    else:
                        x2=int(x2)
                        self.gen.asm.append("\tmov eax, "+x1+'\n')
                        self.gen.asm.append("\timul eax, "+str(x2)+'\n')
                else:
                    if(x2 in self.registers):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfimul DWORD PTR "+x2addr+"\n")
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

        # #mem mem
        # if(x1 in self.currentMap):
        #     # returnSpace is reg
        #     if(returnSpace in self.registers):
        #         self.gen.asm.append("\tmov "+newSpace+", "+x1addr+'\n')
        #         self.gen.asm.append("\tmul "+newSpace+", "+x2addr+'\n')
        #     #returnSpace is mem
        #     else:
        #         self.gen.asm.append("\tmov "+"eax"+", "+x1addr+'\n')
        #         self.gen.asm.append("\tmul "+"eax"+", "+x2addr+'\n')
        #         self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            
        # else:
        #     if(x1==returnSpace):
        #         self.gen.asm.append("\tmul "+returnSpace+", "+x2addr+'\n')
        #     else:
        #         self.gen.asm.append("\tmov "+returnSpace+", "+x1+'\n')
        #         self.gen.asm.append("\tmul "+returnSpace+", "+x1addr+'\n')
        
        # return returnSpace        


    def div(self,x1,x2):
        isFloat=self.checkIsFloat(x1,x2)

        if(not isFloat):
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                self.gen.asm.append("\tdiv eax, "+x2addr+'\n')
            elif(isinstance(x1,Data)):
                if(x2!='eax'):
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                    self.gen.asm.append("\tdiv eax, "+x2+'\n')
                else:
                    x1addr=self.getAbsoluteAdd(x1)
                    reg=self.allocateNewReg('eax')
                    self.gen.asm.append("\tmov "+reg+", "+x1addr+'\n')
                    self.gen.asm.append("\tdiv "+reg+", "+'eax'+'\n')
                    self.gen.asm.append("\tmov eax, "+reg+'\n')
            elif(isinstance(x2,Data)):
                if(x1!='eax'):
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tdiv eax, "+x1+'\n')
                else:
                    x2addr=self.getAbsoluteAdd(x2)
                    self.gen.asm.append("\tdiv eax, "+x2addr+'\n')
            else:
                if(x1=='eax'):
                    self.gen.asm.append("\tdiv eax, "+x2+'\n')
                else:
                    self.gen.asm.append("\tmov eax, "+x1+'\n')
                    self.gen.asm.append("\tdiv eax, "+x2+'\n')
        
            return 'eax'

        else:
            if(isinstance(x1,Data) and isinstance(x2,Data)):
                type1=x1.type.type
                type2=x2.type.type
                x1addr=self.getAbsoluteAdd(x1)
                x2addr=self.getAbsoluteAdd(x2)
                if(type1=='double' and type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfdiv QWORD PTR "+x2addr+"\n")
                elif(type1=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfidiv DWORD PTR "+x2addr+"\n")
                elif(type2=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                    self.gen.asm.append("\tfild DWORD PTR "+x2addr+"\n")
                    self.gen.asm.append("\tfdivp st(1), st"+"\n")
            elif(isinstance(x1,Data)):
                type1=x1.type.type
                x1addr=self.getAbsoluteAdd(x1)
                if(x2 in self.registers):
                    if(type1=='double' and x2=='st'):
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfdivp st(1), st"+"\n")
                    elif(type1=='double'):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfidiv DWORD PTR "+x2addr+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfdivp st(1), st"+"\n")
                # x2 is imm
                else:
                    if(type1!='double'):
                        x2=int(x2)
                    if(type1=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x2]+"\n")
                        self.gen.asm.append("\tfdivp st(1), st"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+x1addr+'\n')
                        self.gen.asm.append("\tdiv eax, "+str(x2)+'\n')
            elif(isinstance(x2,Data)):
                type2=x2.type.type
                x2addr=self.getAbsoluteAdd(x2)
                if(x1 in self.registers):
                    if(type2=='double' and x1=='st'):
                        self.gen.asm.append("\tfdiv QWORD PTR "+x2addr+"\n")
                    elif(type2=='double'):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                        self.gen.asm.append("\tfdivp st(1), st "+"\n")
                        self.__vPop()
                    else:
                        self.gen.asm.append("\tfdiv QWORD PTR "+x2addr+"\n")
                # x2 is imm
                else:
                    if(type2!='double'):
                        x1=int(x1)
                    if(type2=='double'):
                        self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x1]+"\n")
                        self.gen.asm.append("\tfdiv st, st(1)"+"\n")
                    else:
                        self.gen.asm.append("\tmov eax, "+str(x1)+'\n')
                        self.gen.asm.append("\tdiv eax, "+x2addr+'\n')
            else:
                if(x1 != 'st'):
                    if(x2 in self.registers):
                        x1addr=self.__vPush(x1)
                        self.gen.asm.append("\tfld QWORD PTR "+x1addr+"\n")
                        self.gen.asm.append("\tfdiv st, st(1)"+"\n")
                        self.__vPop()
                    else:
                        x2=int(x2)
                        self.gen.asm.append("\tmov eax, "+x1+'\n')
                        self.gen.asm.append("\tdiv eax, "+str(x2)+'\n')
                else:
                    if(x2 in self.registers):
                        x2addr=self.__vPush(x2)
                        self.gen.asm.append("\tfidiv DWORD PTR "+x2addr+"\n")
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

        # #mem mem
        # if(x1 in self.currentMap):
        #     if(returnSpace in self.registers):
        #         self.gen.asm.append("\tmov "+"eax"+", "+x1addr+'\n')
        #         self.gen.asm.append("cdq")
        #         self.gen.asm.append("\tidiv "+x1addr+'\n')
        #         self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
            
        # else:
        #     if(x1==returnSpace):
        #         if(x1=='eax'):
        #             self.gen.asm.append("cdq")
        #             self.gen.asm.append("\tidiv "+returnSpace+", "+x2addr+'\n')
        #         else:
        #             self.gen.asm.append("\tmov "+"eax"+", "+x1+'\n')
        #             self.gen.asm.append("cdq")
        #             self.gen.asm.append("\tidiv"+x2addr+'\n')
        #             self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
        #     else:
        #         self.gen.asm.append("\tmov "+"eax"+", "+x1+'\n')
        #         self.gen.asm.append("cdq")
        #         self.gen.asm.append("\tidiv"+x2addr+'\n')
        #         self.gen.asm.append("\tmov "+returnSpace+", "+"eax"+'\n')
        
        # return returnSpace

    def mov(self,x1,x2):
        isFloat=self.checkIsFloat(x1,x2)
        if(isFloat):
            if(x2 in self.registers):
                if(x2!='st'):
                    x2addr=self.__vPush(x2)
                    self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                    self.__vPop()
                else:
                    x1addr=self.getAbsoluteAdd(x1)
                    self.gen.asm.append("\tfstp QWORD PTR "+x1addr+"\n")
                    return

            elif(isinstance(x2,float)):
                self.gen.asm.append("\tfld QWORD PTR "+self.constMap[x2]+"\n")
            elif(isinstance(x2,Data)):
                x2addr=self.getAbsoluteAdd(x2)
                if(x2.type.type=='double'):
                    self.gen.asm.append("\tfld QWORD PTR "+x2addr+"\n")
                else:
                    self.gen.asm.append("\tfld DWORD PTR "+x2addr+"\n")
            if(isinstance(x1,Data)):
                type1=x1.type.type
                x1addr=self.getAbsoluteAdd(x1)
                if(type1=='double'):
                    self.gen.asm.append("\tfstp QWORD PTR "+x1addr+"\n")
                else:
                    self.gen.asm.append("\tfstp DWORD PTR "+x1addr+"\n")
            elif(x1 in self.registers):
                pass
            
            return x1
                        

        l1=None
        l2=None
        if(isinstance(x1,Data) and isinstance(x2,Data)):
            pointNum=x2.type.pointer_count()
            if(pointNum>=0 and x2.type.type=='function'):
                x1addr=self.getAbsoluteAdd(x1)
                self.gen.asm.append("\tmov "+x1addr+", OFFSET FLAT:"+x2.name+'\n')
                return x1

        if(isinstance(x1,Data)):
            x1addr=self.getAbsoluteAdd(x1)
            l1=x1.name
        if(isinstance(x2,Data)):
            pointNum=x2.type.pointer_count()
            if(pointNum>=0 and x2.type.type=='function'):
                self.gen.asm.append("\tmov "+str(x1)+", OFFSET FLAT:"+x2.name+'\n')
                return x1
            x2addr=self.getAbsoluteAdd(x2)
            l2=x2.name


        if(isinstance(x1,Data) and isinstance(x2,Data)):
            if(x2.type.type=='char' and x2.type.pointer_count()==0):
                self.gen.asm.append("\tmovsx eax, BYTE PTR"+x2addr+'\n')
                self.gen.asm.append("\tmov BYTE PTR "+x1addr+', eax'+'\n')
            elif(x1.type.type=='char' and x1.type.pointer_count()==0):
                self.gen.asm.append('\tmov edi, eax\n')
                self.gen.asm.append("\tmovsx eax, BYTE PTR"+x2addr+'\n')
                self.gen.asm.append("\tmov BYTE PTR "+x1addr.replace("eax","edi")+', eax'+'\n')
                self.gen.asm.append('\tmov eax, edi\n')
            else:
                if(not x1.offset):
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tmov "+x1addr+', eax'+'\n')
                else:
                    self.gen.asm.append('\tmov edi, eax\n')
                    self.gen.asm.append("\tmov eax, "+x2addr+'\n')
                    self.gen.asm.append("\tmov "+x1addr.replace("eax","edi")+', eax'+'\n')
                    self.gen.asm.append('\tmov eax, edi\n')
        elif(isinstance(x2,Data)):
            if(x2.type.type=='char' and x2.type.pointer_count()==0):
                self.gen.asm.append('\tmovsx '+x1+', BYTE PTR'+x2addr+'\n')
            else:
                self.gen.asm.append('\tmov '+x1+', '+x2addr+'\n')
        elif(isinstance(x1,Data)):
            if(isinstance(x2,int)):
                if(x1.type.type=='char' and x1.type.pointer_count()==0):
                    self.gen.asm.append('\tmov BYTE PTR '+x1addr+', %d'%x2+'\n')
                else:
                    self.gen.asm.append('\tmov DWORD PTR '+x1addr+', %d'%x2+'\n')
            else:
                if(x1.type.type=='char' and x1.type.pointer_count()==0):
                    self.gen.asm.append('\tmov BYTE PTR '+x1addr+', '+x2+'\n')
                else:
                    self.gen.asm.append('\tmov '+x1addr+', '+x2+'\n')
        else:
            if(isinstance(x2,int)):
                self.gen.asm.append('\tmov '+x1+', %d'%x2+'\n')
            else:
                try:
                    if(x2 in self.registers):
                        self.gen.asm.append('\tmov '+x1+', '+x2+'\n')
                    self.gen.asm.append('\tmov '+x1+', '+self.constMap[x2]+'\n')
                except Exception,e:
                    # print(self.constMap)
        return x1


    def passPara(self,para):
            if(para in self.registers):
                self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                return
            if(isinstance(para,Data)):
                Type=para.type.type
                pointerCount=para.type.pointer_count()
                addr=self.getAbsoluteAdd(para)
                if(pointerCount>0):
                    self.gen.asm.append("\tmov eax, "+'DWORD PTR '+addr+'\n')
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
                    return

                if(Type=='char'):
                    self.gen.asm.append("\tmov eax, "+'BYTE PTR '+addr+'\n')
                    self.gen.asm.append('\tmov BYTE PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
                elif(Type=='short'):
                    self.gen.asm.append("\tmov eax, "+'WORD PTR '+addr+'\n')
                    self.gen.asm.append('\tmov WORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
                elif(Type=='int'):
                    self.gen.asm.append("\tmov eax, "+'DWORD PTR '+addr+'\n')
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
                elif(Type=='double'):
                    self.gen.asm.append('\tmov '+"esi, "+addr+'\n')
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' esi'+'\n')
                    try:
                        base=int(re.findall('[0-9]+',addr)[0])
                        num=4+base
                        strAddr=addr.replace(str(base),str(num))
                    except Exception,e:
                        strAddr=addr[:-1]+"+4"+addr[-1:]
                    self.callOffset+=4
                    self.gen.asm.append('\tmov '+"esi, "+strAddr+'\n')
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' esi'+'\n')
                    self.callOffset+=4
                elif(Type=='struct'):
                    for i in range(0,para.size/4+1):
                        base=int(re.findall('[1-9]+',addr)[0])
                        num=i*4+base
                        strAddr=addr.replace(str(base),str(num))
                        self.gen.asm.append('\tmov DWORD PTR '+"eax, "+strAddr+'\n')
                        self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                        self.callOffset+=4
                else:
                    raise TypeError("error in passPara")
            else:
                if(isinstance(para,str)):
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+'OFFSET FLAT:'+self.constMap[para]+'\n')
                    self.callOffset+=4
                elif(isinstance(para,float)):
                    for i in range(2):
                        self.gen.asm.append('\tmov eax, DWORD PTR'+self.constMap[para]+'\n')
                        self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                        self.callOffset+=4
                elif(isinstance(para,int)):
                    self.gen.asm.append('\tmov eax, '+str(para)+'\n')
                    self.gen.asm.append('\tmov DWORD PTR '+'[esp+%d], '%self.callOffset+' eax'+'\n')
                    self.callOffset+=4
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
    
    def getParaList(self,funcName):
        self.paraOffset=8
        paraList=global_context.local[funcName].parameter_list
        if len(paraList)==1 and paraList[0][1].type=="void":
            return
        for para in paraList:
            #para:str Type:string
            Type=para[1].type
            pointNum=para[1].pointer_count()
            if(pointNum>0):
                localAddr="[esp+%d]"%(self.localOffset-4)
                self.gen.asm.append('\tmov '+"eax, DWORD PTR "+"[ebp+%d]"%self.paraOffset+'\n')
                self.gen.asm.append('\tmov DWORD PTR '+localAddr+', eax\n')
                self.paraOffset+=4
                self.localOffset-=4
            elif(Type=='char'):
                localAddr="[esp+%d]"%(self.localOffset-4)
                self.gen.asm.append('\tmov '+"eax, DWORD PTR "+"[ebp+%d]"%self.paraOffset+'\n')
                self.gen.asm.append('\tmov BYTE PTR '+localAddr+', al\n')
                self.paraOffset+=4
                self.localOffset-=4
            elif(Type=='int'):
                localAddr="[esp+%d]"%(self.localOffset-4)
                self.gen.asm.append('\tmov '+"eax, DWORD PTR "+"[ebp+%d]"%self.paraOffset+'\n')
                self.gen.asm.append('\tmov DWORD PTR '+localAddr+', eax\n')
                self.paraOffset+=4
                self.localOffset-=4
            elif(Type=='double'):
                for i in range(0,2):
                    localAddr="[esp+%d]"%(self.localOffset-4)
                    self.gen.asm.append('\tmov '+"eax, DWORD PTR "+"[ebp+%d]"%self.paraOffset+'\n')
                    self.gen.asm.append('\tmov DWORD PTR '+localAddr+', eax\n')
                    self.paraOffset+=4
                    self.localOffset-=4
            self.currentMap.update({para[0]:{'reg':0,'type':Type,'addr':localAddr}})

        return

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
            if(func.type.type=='function' and func.type.pointer_count()>0):
                self.gen.asm.append('\tcall '+self.currentMap[func.name]["addr"]+'\n')
            else:
                self.gen.asm.append('\tcall '+func.name+'\n')
        else:
            self.gen.asm.append('\tcall '+func+'\n')
        return 'eax'
    
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
            self.gen.asm.append('\tlea '+'eax, '+'['+x+']'+'\n')
        else:
            self.gen.asm.append('\tlea '+'eax, '+xaddr+'\n')
        return 'eax'
    
    def cmp(self,x1,x2):
        if(isinstance(x1,Data) and isinstance(x2,Data)):
            x1addr=self.getAbsoluteAdd(x1)
            x2addr=self.getAbsoluteAdd(x2)
            self.gen.asm.append("\tmov eax, "+x1addr+'\n')
            self.gen.asm.append('\tcmp '+'eax'+', '+x2addr+'\n')
            return

        dataflag1=False;
        if(isinstance(x1,Data)):
            x1=self.getAbsoluteAdd(x1)
            dataflag1=True
        dataflag2=False;
        if(isinstance(x2,Data)):
            x2=self.getAbsoluteAdd(x2)
            dataflag2=True
        # if(isinstance(x1,Data)):
        #     x1addr=self.getAbsoluteAdd(x1)
        #     x1=x1.name
        # if(isinstance(x2,Data)):
        #     x2addr=self.getAbsoluteAdd(x2)
        #     x2=x2.name
        # if(x1 in self.currentMap and x2 in self.currentMap):
        #     self.gen.asm.append("\tmov eax, "+x1addr+'\n')
        #     self.gen.asm.append('\tcmp '+'eax'+', '+x2+'\n')
        #     return
        if(dataflag1):
            self.gen.asm.append('\tcmp DWORD PTR '+str(x1)+', '+str(x2)+'\n')
            return
        if(dataflag2):
            self.gen.asm.append('\tcmp '+str(x1)+', DWORD PTR '+str(x2)+'\n')
            return
        self.gen.asm.append('\tcmp '+str(x1)+', '+str(x2)+'\n')
        return
    
    def jg(self,label):
        self.gen.asm.append('\tjg '+label+'\n')
        return
    
    def jge(self,label):
        self.gen.asm.append('\tjge '+label+'\n')
        return
    
    def jl(self,label):
        self.gen.asm.append('\tjl '+label+'\n')
        return
    
    def jle(self,label):
        self.gen.asm.append('\tjle '+label+'\n')
        return
        
    def je(self,label):
        self.gen.asm.append('\tje '+label+'\n')
        return
        
    def jne(self,label):
        self.gen.asm.append('\tjne '+label+'\n')
        return

    def jmp(self,label):
        self.gen.asm.append('\tjmp '+label+'\n')
        return
    
    def loop(self,label):
        self.gen.asm.append('\tloop '+label+'\n')
        return
    
    def sal(self,x,offset):
        if(isinstance(x,Data)):
            x=self.getAbsoluteAdd(x)
        self.gen.asm.append('\tsal '+x+str(offset)+'\n')
        return
    
    def sar(self,x,offset):
        if(isinstance(x,Data)):
            x=self.getAbsoluteAdd(x)
        self.gen.asm.append('\tsar '+x+str(offset)+'\n')
        return
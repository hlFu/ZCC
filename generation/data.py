#!/usr/bin/env python
#coding=utf-8
from public.ZCCglobal import *

class Data(object):
    def __init__(self,name,offset,type):
        """
        :type name:str
        :type offset:bool
        :type type:CType
        """
        self.name=name
        self.offset=offset
        self.type=type

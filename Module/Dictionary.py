# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 19:33:20 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Dictionary
"""

import copy as cp

#============================================================================== 
#字典按value搜索key
def DictKeyOfValue(dictionary,value):
    
    keys=list(dictionary.keys())
    values=list(dictionary.values())
    
    #要查询的值为value
    key=keys[values.index(value)]
    
    return key

#============================================================================== 
#获取字典子集的函数，从索引start到索引stop,不包括索引stop
def DictSlice(dictionary,start,stop):
    
    keys=list(dictionary.keys())
    values=list(dictionary.values())  
    
    new_dict={}
    
    for i in range(start,stop):
        
        new_dict[keys[i]]=values[i]
        
    return new_dict

#============================================================================== 
#以start为起始索引，将字典重新排序
def DictSortFromStart(dictionary,start):
    
    #两个字典切片
    new_dict_1=DictSlice(dictionary,start,len(dictionary))
    new_dict_2=DictSlice(dictionary,0,start)
    
    #建立新的索引列表
    keys=[]
    
    for item in list(new_dict_1.items()):
        
        keys.append(item[0])
        
    for item in list(new_dict_2.items()):
        
        keys.append(item[0])
        
    #建立新的值列表 
    values=[]
    
    for item in list(new_dict_1.items()):
        
        values.append(item[1])
        
    for item in list(new_dict_2.items()):
        
        values.append(item[1])
        
    #建立新的字典
    new_dict={}
    
    for k in range(len(dictionary)):
        
        new_dict[keys[k]]=values[k]
        
    return new_dict

#============================================================================== 
#让字典索引以某列表的顺序排列
def DictSortByIndex(which_dict,which_keys):
    
    #结果
    that_dict={}
    
    #遍历新列表，并填充字典
    for this_key in which_keys:
        
        that_dict[this_key]=which_dict[this_key]
        
    return that_dict

#============================================================================== 
#重新排序，以某个中间节点为起点，前部接在后部之后
def SortFromStart(which_list,start_index):

    #新老列表
    old_list=cp.deepcopy(which_list)
    new_list=which_list[start_index:]+which_list[:start_index]
    
    #新老列表的索引
    old_index=[k for k in range(len(old_list))]
    new_index=old_index[start_index:]+old_index[:start_index]
    
    #新老列表索引的对应关系
    map_new_old_index=dict(zip(old_index,new_index))
    
    return new_list,map_new_old_index 

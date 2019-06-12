# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 18:52:23 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Geometry
"""

import numpy as np
import matplotlib.pyplot as plt

from Module import Display as Dis
from Module import Dictionary as Dict

#==============================================================================     
#事后将其写进类里
#计算两点之间的距离
def Distance(pos_A,pos_B):
    
    #判断pos_A,pos_B的数据类型，无论如何都转化为np.array
    if type(pos_A) is not np.array:
       
        pos_A=np.array(pos_A)
    
    if type(pos_B) is not np.array:
       
        pos_B=np.array(pos_B)
  
    return np.sqrt(np.sum((pos_A-pos_B)**2))

#==============================================================================    
#定义一个组合对应位置x和y坐标的函数
#to_int表示是否取整,默认为True
def CombineXY(x,y,to_int=True):
    
    #转为列表
    list(x),list(y)
    
    #输出结果的列表
    that_data=[]
    
    for k in range(len(x)):
        
        #如果取整
        if to_int:    
            that_x=int(np.round(x[k]))
            that_y=int(np.round(y[k]))
        
        else:
            that_x=x[k]
            that_y=y[k]
            
        that_data.append([that_x,that_y])
        
    return that_data

#==============================================================================     
#定义过(x0,y0),斜率为k的像素点集合
#threshold是自变量取值范围[x_min,x_max]
def GenerateLineList(x0,y0,k,threshold):
         
    #自变量x的取值范围为
    x=np.linspace(min(threshold),max(threshold),max(threshold)-min(threshold)+1) 
    y=(x-x0)*k+y0
    
    return CombineXY(x,y)

#============================================================================== 
#计算点集当中所有点的质心/重心
def CalculateBaryCenter(which_content):
    
    #横纵坐标的集合
    I=[pos[0] for pos in which_content]
    J=[pos[1] for pos in which_content]
    
    I_center=np.mean(I)
    J_center=np.mean(J)
    
    return [I_center,J_center]

#============================================================================== 
#某点which_pos到点集which_points的距离 
def Distances(which_pos,which_points):
    
    return [Distance(which_pos,this_point) for this_point in which_points]

#============================================================================== 
#计算某个点到某个点集中的点的距离的集合
def DistancesMap(which_pos,which_points):
        
    return dict(zip(Distances(which_pos,which_points),which_points))

#============================================================================== 
#集合which_content中到which_pos最近的点
def NearestPoint(which_pos,which_content):
    
    #距离和点的索引
    map_distances=DistancesMap(which_pos,which_content)
    
    return map_distances[min(list(map_distances.keys()))]

#============================================================================== 
#生成邻居点的列表
def NeighborList(which_pos):
    
    return [(which_pos[0]+step_x,which_pos[1]+step_y) for step_x in[-1,0,1] for step_y in [-1,0,1]]

#============================================================================== 
#邻居判断并返回相对的方位索引
#根据两个点的坐标来判断
def NeighborIndex(pos_A,pos_B):
    
    #用邻居原则来判断    
    #A,B各自的邻居
    neighbor_A=[(pos_A[0]+step_x,pos_A[1]+step_y) for step_x in[-1,0,1] for step_y in [-1,0,1]]
    neighbor_B=[(pos_B[0]+step_x,pos_B[1]+step_y) for step_x in[-1,0,1] for step_y in [-1,0,1]]
    
#    print(neighbor_A)
#    print(neighbor_B)
    
    #判断是否在各自的8邻域内
    A_in_B=tuple(pos_A) in neighbor_B
    B_in_A=tuple(pos_B) in neighbor_A
    
    #必须都成立哦
    if not (A_in_B and B_in_A):
        
        print('this point is not available')
        
        return
    
    #通过位置建立索引
    code_list=[k for k in range(8)]
    relative_pos_list=[(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
    
    #建立编码与位置的映射
    map_code_relative_pos=dict(zip(code_list,relative_pos_list))
    
    #如果为AB邻居
    if A_in_B and B_in_A:
        
        pos_A=np.array(pos_A)
        pos_B=np.array(pos_B)
        
        #相对位置
        relative_pos_B2A=tuple(pos_B-pos_A)
        relative_pos_A2B=tuple(pos_A-pos_B)
        
        #位置编码
        code_B2A=Dict.DictKeyOfValue(map_code_relative_pos,relative_pos_B2A)
        code_A2B=Dict.DictKeyOfValue(map_code_relative_pos,relative_pos_A2B)
     
#        print('B:the position code',code_B2A,'of A')
#        print('A:the position code',code_A2B,'of B')
    
    return code_B2A,code_A2B

#============================================================================== 
#计算曲线距离：连续计算
def ContinuousDistance(which_curve_points):
    
    curve_distance=0
    
    for k in range(len(which_curve_points)-1):
        
        curve_distance+=Distance(which_curve_points[k],which_curve_points[k+1])
        
    return curve_distance

#============================================================================== 
#map_corner_point为角点坐标及其索引
#lines_amount为曲线的数量
def CurvedLinesLength(which_content,map_corner_points,lines_amount,img_rgb):
            
    #按索引排序
    map_corner_points=Dict.DictSortByIndex(map_corner_points,sorted(list(map_corner_points.keys())))
    
#    print(map_corner_points)
    
    #计算出几个点的曲线距离
    #索引
    corner_index=list(map_corner_points.keys())
        
    #索引列表做一下
    curve_points=[]
    
    for k in range(len(corner_index)):
        
        #第一段特殊处理
        if k==0:
            
            curve_points.append(which_content[corner_index[-1]:]+which_content[:corner_index[0]+1])
       
        #其他正常
        else:
            
            curve_points.append(which_content[corner_index[k-1]:corner_index[k]+1])
     
#    print(curve_points)
    
    '''简单算法(用于检验)'''
#    #所有的
#    curve_distances=[]
#    
#    #计算每一条曲线的曲线长度  
#    curve_distances=[ContinuousDistance(this_curve_points) for this_curve_points in curve_points]    
#    
#    print(curve_distances)
    
    '''拾取算法'''
    curve_points_up_and_down=[]
    
    #获取两个点的坐标，确定两条层长线
    for temp_point in plt.ginput(lines_amount):
           
        #点击获取曲线中的点的坐标并转化一下
        point=[int(np.round(temp_point[1])),int(np.round(temp_point[0]))]
        
#        print(point)
        
        #多条线到这个点的距离
        #以及用坐标集合当返回值
        map_distance_curve_points={}
        
        #先求每条线的中点
        for this_curve_points in curve_points:
            
            #重心
            center=CalculateBaryCenter(this_curve_points)
            
            #收录进映射关系
            map_distance_curve_points[Distance(center,point)]=this_curve_points
            
        curve_points_up_and_down.append(map_distance_curve_points[min(list(map_distance_curve_points.keys()))])
        
    #上下两条边的点集合
    curve_points_up,curve_points_down=curve_points_up_and_down
    
    return curve_points_up,curve_points_down

    #上下两条边的长度
    curve_length_up=ContinuousDistance(curve_points_up)
    curve_length_down=ContinuousDistance(curve_points_down)
    
#    print(curve_length_up)
#    print(curve_length_down)
    
    Dis.Line2Red(curve_points_up+curve_points_down,img_rgb)
    
    return (curve_length_up+curve_length_down)/2

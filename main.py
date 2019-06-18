# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 19:17:36 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒引法的平衡恢复脚本
"""

import copy as cp
import numpy as np
import matplotlib.pyplot as plt

import sys,os

if os.getcwd() not in sys.path:
    
    sys.path.append(os.getcwd())
    
from Module import Pick
from Module import Image as Img
from Module import Angle as Ang
from Module import Display as Dis
from Module import Initialize as Init
from Module import Geometry as Geom
from Module import Dictionary as Dict
from Module import Corner as Cor
from Module import Length as Len
from Module import Recover as Rec

#导入图片，生成rgb数组
#load_path=r'C:\Users\whj\Desktop\Spyder\例\offset_model.bmp'
#load_path=r'C:\Users\whj\Desktop\Spyder\例\挤压.bmp'
load_path=r'C:\Users\whj\Desktop\Spyder\例\fault.bmp'
#load_path=r'C:\Users\whj\Desktop\Spyder\例\simple.bmp'
#load_path=r'C:\Users\whj\Desktop\Spyder\例\Corner.bmp'

save_path=r'C:\Users\whj\Desktop\bcs'

Rec.SeriesRecover(load_path,save_path)


#导入图片，生成rgb矩阵
img_rgb=Init.LoadImage(load_path,show=False)

#生rgb相关的列表和字典
#rgb_dict=Init.InitDict(img_rgb)
rgb_dict=Init.InitDict(img_rgb,base_adjust=True,fault_exist=True)

#改变图片尺寸增加padding
img_tag,img_rgb=Init.AddPadding(img_rgb,rgb_dict,show=True)

#初始化fractions，并显示
total_fractions=Pick.PickFractions(img_rgb,img_tag,rgb_dict)  

#'''解决layer内的有fault情况的恢复'''
#
##要搞的那个layer
#which_layer=Pick.PickLayer(total_fractions,img_rgb)
#
##所有的邻居fault列表
#neighbor_faults=Pick.NeighborFault(which_layer,total_fractions)
#
##完全就是个边界的fault列表
#border_faults=Pick.BorderFaults(which_layer,total_fractions)
#
##求neighbor和border的差集
#internal_faults=[this_fault for this_fault in neighbor_faults if this_fault not in border_faults]
#
##只要里面有宝贝就干他
#if len(internal_faults):
#    
#    #多个内部fault的edge的邻居总列表
#    internal_faults_edge_neighbor=[]
#    
#    #找他们的邻居点列表
#    for this_fault in internal_faults:
#        
#        #邻居列表
#        this_fault_edge_neighbor=[]
#        
#        for this_pos in this_fault.edge:
#            
#            #横纵坐标
#            this_i,this_j=this_pos
#            
#            #邻居们
#            this_neighbor=[[this_i+step_i,this_j+step_j] for step_i in [-1,0,1] for step_j in [-1,0,1]]
#            
#            #加入到总列表当中
#            this_fault_edge_neighbor+=this_neighbor
#        
#        #总列表    
#        internal_faults_edge_neighbor.append(this_fault_edge_neighbor)
#        
#        #做交集
#        cross_points=[this_pos for this_pos in this_fault_edge_neighbor if this_pos in which_layer.content]
#           
#        #显示一下头和尾
##        Dis.ShowOnePoint(cross_points[0],img_rgb)
##        Dis.ShowOnePoint(cross_points[-1],img_rgb)
#        
#        #确定一下头尾的相对位置关系噢
#        if [cross_points[0][0],cross_points[0][1]+1] in which_layer.content:
#            
##            print('0')
#            
#            right_attachment_point=cp.deepcopy(cross_points[0])
#            left_attachment_point=cp.deepcopy(cross_points[-1])
#    
#        if [cross_points[0][0],cross_points[0][1]-1] in which_layer.content:
#            
##            print('1')
#            
#            right_attachment_point=cp.deepcopy(cross_points[-1])
#            left_attachment_point=cp.deepcopy(cross_points[0])
#            
#        #确认一下它们的位置？
#        Dis.ShowOnePoint(right_attachment_point,img_rgb,5)
#        Dis.ShowOnePoint(left_attachment_point,img_rgb,10)
#        
#        #所有的faults,不能复制地址
#        total_faults=cp.copy(neighbor_faults)
#        
#        #删除这个fault
#        total_faults.remove(this_fault)
#        
#        #this_fault的左右衔接fault
#        other_faults=cp.deepcopy(total_faults)
#        
#        '''找左右faults集合'''
#        left_other_faults=[this_other_fault for this_other_fault in other_faults if this_other_fault.center[1]<this_fault.center[1]]
#        right_other_faults=[this_other_fault for this_other_fault in other_faults if this_other_fault.center[1]>this_fault.center[1]]
#           
#        #完成左右衔接点与隔壁的串联
#        '''layer.edge中某侧在fault.content中且到接应点的索引差最近'''
#        
#        #寻找右侧
#        for this_right_fault in right_other_faults:
#            
#            #中某侧在fault.content中的点
#            point_near_this_right_fault=[]
#            
#            for this_pos in this_right_fault.edge:
#
#                #fault上的点右侧的点
#                left_this_pos=[this_pos[0],this_pos[1]-1]
#                
#                if left_this_pos in which_layer.edge:
#                    
#                    point_near_this_right_fault.append(left_this_pos)
#            
#         
##%%        
#for this_fault in right_other_faults:
#    
#    this_fault.Show(img_rgb,rgb_dict)
    
'''完整版？？？'''   
 

##所有faults对象
#total_faults=Pick.DeleteLayer(total_fractions)

   
#which_content=total_layers[0].edge
#
#corner_points=[]
#
##点击获取图像中的点的坐标
#for temp_point in plt.ginput(4): 
#
#    #转化一下
#    point=[int(np.round(temp_point[1])),int(np.round(temp_point[0]))]
#    
#    #计算距离最短的点作为角点
#    map_distances_points=Geom.DistancesMap(point,which_content)
#    
#    #最短的距离 
#    corner_points.append(map_distances_points[min(list(map_distances_points.keys()))])
#    
    
#new_fractions=[]
#
#for k in range(5):
#    
#    new_fractions.append(Len.RecoverLength(total_fractions,img_rgb,img_tag,rgb_dict))
#
#for this_fraction in new_fractions:
#
#    this_fraction.Show(img_rgb,rgb_dict)

#a=Pick.PickFault(total_fractions,img_rgb)  

##从图中获取几个点   
#for this_fraction in Pick.DeleteFault(total_fractions)[0:1]:
#    
##    Ang.AnglesFromFraction(this_fraction,img_rgb,show=True,axis=True)
#
##    print(len(this_fraction.edge))
#    
#    points=EdgeIndex(this_fraction,'difference',True,True)
#    
##    points=PickPointsFromImg(4,this_fraction.edge)
 
#从图像中获取断层
#this_fault=Pick.PickFault(total_fractions,img_rgb)

#计算某部分面积
#Pick.PickAndCalculateArea(total_fractions)

##生成上下盘 
#plate_up=Pick.PickAndGeneratePlate(total_fractions,img_rgb)
#
#plate_down=Pick.PickAndGeneratePlate(total_fractions,img_rgb)
#
#plate_up.Show(img_rgb,rgb_dict)
#
#plate_down.Show(img_rgb,rgb_dict)
#
##将layer切割成chip
#CHIP_1=plate_up.ToChip(this_fault,img_tag,20,'A')
#CHIP_2=plate_down.ToChip(this_fault,img_tag,20,'B')
#
#Dis.ShowChips([CHIP_1,CHIP_2],img_rgb,rgb_dict,grid='on')
#
#CHIP_1.Show(img_rgb,rgb_dict,grid='on')
#CHIP_2.Show(img_rgb,rgb_dict,grid='on')
#
##拉到一块
#CHIP_1,CHIP_2=CO.Cohere([CHIP_2,CHIP_1])

#Chips=[CHIP_1,CHIP_2]

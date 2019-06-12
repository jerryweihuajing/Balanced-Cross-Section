# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 19:55:07 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-ChipOperation
"""
import numpy as np

from Module import Dictionary as Dict

#============================================================================== 
#写一个通过id搜索chips的函数
#Chips为本场比赛的Chip集合
def SearchByID(Chips,ID):
    
    #可搜索Chip chips chip
    #搜索Chip
    for this_Chip in Chips:
        if this_Chip.id==ID:
            return this_Chip
    
    #搜索chips    
    if '-' in ID and '|' not in ID:
        for this_Chip in Chips:
            for this_chips in this_Chip.total_chips:
                if this_chips.id==ID:
                    return this_chips
                
    #搜索chip
    if '-' in ID and '|' in ID:
        for this_Chip in Chips:
            for this_chips in this_Chip.total_chips:
                for this_chip in this_chips.total_chip:
                    if this_chip.id==ID:
                        return this_chip
                    
#==============================================================================             
#搜索相邻10个参数的函数
#which_Chip表示这件事发生在某个Chip中
#which_chips表示被搜索的chips
#amount表示参与计算的点的数量
#side表示该chips位于整体chips的什么位置
def chipsNearby(which_Chip,which_chips,amount,side):
    
    #计算which_Chip里chips的id上下限
    total_chips_id=[int(this_chips.id.split('-')[1]) for this_chips in which_Chip.total_chips]
    
    #上下限id
    chips_id_max=which_Chip.id+'-'+str(max(total_chips_id))
    chips_id_min=which_Chip.id+'-'+str(min(total_chips_id))
    
#    print(chips_id_max,chips_id_min)
    
    #最终结果得到集合
    chips_nearby=[]
    
    #处理顶部异常的chips
    if which_chips.need_to_advanced_regularization:
        
        start_chips_id=int(which_chips.id.split('-')[1])
        
        #初始化左右id,用split函数分别取id的前后半段
        left_id=which_chips.id.split('-')[0]+'-'+str(start_chips_id)
        right_id=which_chips.id.split('-')[0]+'-'+str(start_chips_id)
        
        #count大于amount时停止
        count=0
        
        #左端的chips们的相应参数由其右端的中间参数集合得到
        if side=='left':
            
            while count<amount:
                            
                left_id=which_Chip.id+'-'+str(int(left_id.split('-')[1])-1)
                
                #到顶了就结束
                if left_id==chips_id_min:
                    break
                
                #前提是他们存在呢
                if SearchByID([which_Chip],left_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],left_id))
                    
#                    print('left')
                    
        #右端的chips们的相应参数由其左端的中间参数集合得到
        if side=='right':
            while count<amount:
                
                right_id=which_Chip.id+'-'+str(int(right_id.split('-')[1])+1)
                
                #到头了就结束
                if right_id==chips_id_max:
                    break
                
                #判断存在这样一个事物
                if SearchByID([which_Chip],right_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],right_id))
                    
#                    print('right')
                    
        #两头增长，数量为amount时停止，取的平均
        if side=='middle':
            while count<amount:
                
                #左右开弓
                left_id=which_Chip.id+'-'+str(int(left_id.split('-')[1])-1)
                right_id=which_Chip.id+'-'+str(int(right_id.split('-')[1])+1)
                
                #到顶了就结束
                if left_id==chips_id_min or right_id==chips_id_max:
                    break
                
                #前提是他们存在呢
                if SearchByID([which_Chip],left_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],left_id))
                    
#                    print('middle-left')
                    
                #判断存在这样一个事物
                if SearchByID([which_Chip],right_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],right_id))
                    
#                    print('middle-right')
                    
    return chips_nearby

#============================================================================== 
#表示chips和中点坐标对应关系的键值对
#axis：'both','I','J'分别表示行列索引，行索引，列索引
def MapCenterchipsOf(which_Chip,axis):

    map_J_total_chips={}
    
    for this_chips in which_Chip.total_chips:
        
        if this_chips.center!=None:
            
            #以下两句意思一样的
#            map_J_total_chips.update({this_chips:this_chips.center[1]})
#            map_J_total_chips[this_chips]=this_chips.center[1]   
             
            #行索引
            if axis is 'I':
                
                map_J_total_chips[this_chips]=this_chips.center[0] 
                
            #列索引
            if axis is 'J':
                
                map_J_total_chips[this_chips]=this_chips.center[1] 
                
            #列索引
            if axis is 'both':
                
                map_J_total_chips[this_chips]=this_chips.center
            
#    print(map_J_total_chips)
    
    return map_J_total_chips

#==============================================================================  
#返回两端的chips
#side表示边，有'left'和'right'两个选项
def chipsOf(which_Chip,side):
    
    #先建立键值对
    #根据values的值返回chips对象
    map_J_total_chips=MapCenterchipsOf(which_Chip,'J')
    
    #最左的即J最小的chips
    if side is 'left':
    
        return Dict.DictKeyOfValue(map_J_total_chips,min(list(map_J_total_chips.values())))

    #最右的即J最大的chips
    if side is 'right':
    
        return Dict.DictKeyOfValue(map_J_total_chips,max(list(map_J_total_chips.values())))

#============================================================================== 
#which_chips中行索引最小的所有pos集合
def TopIPosIn(which_chips):
    
    #求最高点的所有坐标
    I_which_chips=[pos[0] for pos in which_chips.content]
    
#    print(I_which_chips)
    
    top_I_which_chips=min(I_which_chips)
    
#    print(top_I_which_chips)
#    print(which_chips.content)
    
    #返回这一行中所有满足top的点
    top_I_pos_in_which_chips=[pos for pos in which_chips.content if pos[0]==top_I_which_chips]
    
#    print(top_I_pos_in_which_chips)

    return top_I_pos_in_which_chips

#============================================================================== 
#返回左右chips的距离最近的两个点  
#side表示左右chips
def SpecialPointOf(which_chips,side):
    
    #先求which_chips中行索引最小的所有pos集合
    top_I_pos_in_which_chips=TopIPosIn(which_chips)
    
#    print(top_I_pos_in_which_chips)
    
    #求他们的行列索引集合
    I_top_I_pos_in_which_chips=[pos[0] for pos in top_I_pos_in_which_chips]
    J_top_I_pos_in_which_chips=[pos[1] for pos in top_I_pos_in_which_chips]
    
#    print(I_top_I_pos_in_which_chips)
#    print(J_top_I_pos_in_which_chips)
    
    #建立索引呗
    map_JI_top_I_pos_in_which_chips=dict(zip(J_top_I_pos_in_which_chips,I_top_I_pos_in_which_chips))
    
#    print(map_JI_top_I_pos_in_which_chips)
    
    #max在右
    if side is 'right':
        
        special_point=[map_JI_top_I_pos_in_which_chips[max(J_top_I_pos_in_which_chips)],max(J_top_I_pos_in_which_chips)]
    
    #min在左
    if side is 'left':
        
        special_point=[map_JI_top_I_pos_in_which_chips[min(J_top_I_pos_in_which_chips)],min(J_top_I_pos_in_which_chips)]
        
#    print(special_point)
    
    return special_point

#==============================================================================      
#将Chips对象聚合在一起
#先处理两个Chip对象
def Cohere(Chips):
    
    #根据中点来判断
    J_center_Chips=[this_Chip.center[1] for this_Chip in Chips]
    
    #建立Chip和J值的索引关系
    map_J_center_Chips=dict(zip(Chips,J_center_Chips))

    #min在左
    Chip_left=Dict.DictKeyOfValue(map_J_center_Chips,min(list(map_J_center_Chips.values())))
    
    #max在右
    Chip_right=Dict.DictKeyOfValue(map_J_center_Chips,max(list(map_J_center_Chips.values())))
   
#    print(Chip_left.center)
#    print(Chip_right.center)
    
    #取Chip_left中最右的
    chips_left=chipsOf(Chip_left,'right')
    
    #取Chip_right中最左的
    chips_right=chipsOf(Chip_right,'left')

#    print(chips_right,chips_left)
    
    #根据其坐标进行移动
#    print(chips_right.center)
#    print(chips_left.center)
#    
#    print(chips_right.content)
#    print(chips_left.content)

    I_offset=SpecialPointOf(chips_right,'left')[0]-SpecialPointOf(chips_left,'right')[0]
    J_offset=SpecialPointOf(chips_right,'left')[1]-SpecialPointOf(chips_left,'right')[1]
    
#    print(I_offset,J_offset)
    
    #左右盘的位移
    I_offset_left=int(np.floor(I_offset/2))
    J_offset_left=int(np.floor(J_offset/2))
    
    #右边的偏移距        
    I_offset_right=abs(abs(abs(I_offset)-abs(I_offset_left)))        
    J_offset_right=abs(abs(abs(J_offset)-abs(J_offset_left)))
    
    #判断是否为0 
    #乘上算子
    if I_offset_left!=0:
        
        I_offset_right*=(-I_offset_left/abs(I_offset_left))
    
    if J_offset_left!=0:
        
        J_offset_right*=(-J_offset_left/abs(J_offset_left))
    
#    print(I_offset_left,J_offset_left)
#    print(I_offset_right,J_offset_right)
    
#    print(Chip_left.center)
#    print(Chip_right.center)

    #移动Chip_left,Chip_right
    Chip_left.Move(I_offset_left,J_offset_left)
    Chip_right.Move(I_offset_right,J_offset_right)

#    print(Chip_left.center)
#    print(Chip_right.center)
    
    return [Chip_left,Chip_right]

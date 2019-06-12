# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 19:20:33 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Pick
"""

import copy as cp
import matplotlib.pyplot as plt

import Module.Target as Tar
import Module.Display as Dis
import Module.Geometry as Geom

#跨文件夹导入包
import sys
sys.path.append('.')

from Object.o_layer import layer
from Object.o_fault import fault
from Object.o_plate import plate

#============================================================================== 
#初始化所有的fractions
def PickFractions(img_rgb,
                  img_tag,
                  rgb_dict,
                  show=False,
                  axis=True,
                  text=False,
                  output=False,
                  base='off'):
    
    #基底tag
    base_tag=-2
    
    #拾取出tag为2,3,4的层
    fraction_rgb_dict=cp.deepcopy(rgb_dict)
    
    #删除空白rgb索引
    del fraction_rgb_dict[0]
    
    #是否要基底的那个tag
    if base=='off':

        if base_tag in list(fraction_rgb_dict.keys()):
            
            del fraction_rgb_dict[base_tag]
    
    #图像中的所有fraction对象列表
    total_fractions=[]
    
    #拾取断层和地层并显示
    for this_tag in list(fraction_rgb_dict.keys()):
     
        that_fraction=Tar.PickSomething(img_rgb,
                                        img_tag,
                                        this_tag,
                                        fraction_rgb_dict,
                                        show,
                                        axis,
                                        text,
                                        output)
        
        total_fractions+=that_fraction
    
    #显示total_fractions
    if show:
        
        Dis.ShowFractions(total_fractions,
                          img_rgb,
                          rgb_dict,
                          axis,
                          text,
                          output)
        
    return total_fractions

#==============================================================================                     
#处理掉total_fractions中所有fault对象的函数
def DeleteFault(total_fractions):
    
    #结果fractions列表
    result_fractions=[]
    
    for this_fraction in total_fractions:   
        
        if not isinstance(this_fraction,fault):
            
            result_fractions.append(this_fraction)
        
    return result_fractions 

#==============================================================================                     
#处理掉total_fractions中所有layer对象的函数
def DeleteLayer(total_fractions):
    
    #结果fractions列表
    result_fractions=[]
    
    for this_fraction in total_fractions:   
        
        if not isinstance(this_fraction,layer):
            
            result_fractions.append(this_fraction)
        
    return result_fractions 

#============================================================================== 
#求点击获得的fraction的面积
#falut_exclude表示不计算断层的面积
def PickAndCalculateArea(total_fractions,fault_exclude=True):
    
    #总点集合
    total_fractions_content=[]
    
    #复制total_fractions
    temp_total_fractions=cp.deepcopy(total_fractions)
    
    #不考虑断层
    if fault_exclude:
        
        total_layers=DeleteFault(total_fractions)
         
        #暂时性的列表
        temp_total_fractions=cp.deepcopy(total_layers)
        
#    print(len(temp_total_fractions))
    
    #从fractions列表中获取点集
    for this_fraction in temp_total_fractions:
        
        total_fractions_content+=this_fraction.content
        
    #循环开始的标志
    flag_loop=True
    
    print('')
    print('......')
    print('picking the fraction and calculate the area')
   
    #迭代
    while flag_loop:
              
        #点击获取像素点坐标
        fraction_point_pos=plt.ginput(1)[0]
        
        print('......')
        print('picking the fraction')
        
        #注意反过来，因为是xy坐标
        pos_xy=[int(fraction_point_pos[0]),int(fraction_point_pos[1])]
    
        pos_IJ=cp.deepcopy(pos_xy)
        
        #IJ形式是xy形式的颠倒
        pos_IJ.reverse()

        #判断在不在总集合内
        if pos_IJ in total_fractions_content:
            
            #具体在哪呢
            for this_fraction in total_fractions:
            
                #首先直接判断是否位于content内部
                if pos_IJ in this_fraction.content:
        
                    #被选中区域的面积
                    area=len(this_fraction.content)
                    
                    print('......')  
                    print('the fraction picked is')
                    
                    #一般情况下只有layer
                    name='layer'
                    
                    #有fault的情况
                    if not fault_exclude:
                        
                        if isinstance(this_fraction,fault):
                                
                            name='fault'
                        
                    print(name,'id:',this_fraction.id,'area:',area)  
                                         
                    continue
                
        #点击fraction之外的内容结束拾取   
        if pos_IJ not in total_fractions_content:
        
            flag_loop=False
         
            print('......')                      
            print('picking of the fraction is over') 
            print('the end of area calculation')

#============================================================================== 
#点击拾取fractions对象并生成plate对象
#total_fractions表示图像中的所有fraction对象
def PickAndGeneratePlate(total_fractions,img_rgb):

    print('')
    print('here comes a new plate')
    
    #建立fractions的content
    Content=[]
    
    #建立pos总集合
    for this_fraction in total_fractions:
        
        Content+=this_fraction.content
    
    #这个plate中所有的fractions
    that_fractions=[]
    
    count=0
    
    import copy
    
    #像素矩阵
    img_rgb_temp=copy.deepcopy(img_rgb)
    
    #循环呗
    while True:
        
        print('......')
        print('please pick the layer')
        
        #点击获取像素点坐标
        layer_point_pos=plt.ginput(1)[0]
        
        #注意反过来，因为是xy坐标
        pos_xy=[int(layer_point_pos[0]),int(layer_point_pos[1])]
        
        pos_IJ=copy.deepcopy(pos_xy)
        
        #IJ形式是xy形式的颠倒
        pos_IJ.reverse()
        
    #    print('......')
    #    print(pos_IJ)
                
        #如果点到外面，此plate的fraction提取结束
        if pos_IJ not in Content:
            
            print('......')
            print('layer picking of this plate is over')
            
            break
        
        #判断这个坐标合理与否
        for this_fraction in total_fractions:
                
            #判断他在哪
            if pos_IJ in this_fraction.content:
                
                #且不在已收录的fraction对象集中
                if this_fraction in that_fractions: 
                    
                    print('......')
                    print('this layer is already picked')
                    
                    break
                    
                if this_fraction not in that_fractions:
                    
                    count+=1
            
                    print('......')
                    print('picking the layer'+''+str(count))
                    
                    Dis.ShowEdge(this_fraction,img_rgb_temp)
                    
                    that_fractions.append(this_fraction)
                    
                    break
                
    #显示一下呗
    plt.figure()
    plt.imshow(img_rgb_temp)

    #生成的plate对象
    that_plate=plate()
    
    #初始化
    that_plate.Init(that_fractions)
    
    return that_plate

#3.11
#============================================================================== 
#从图像中获取fault对象
def PickFault(total_fractions,
              img_rgb,
              show=False,
              axis=True):
    
    print('')
    print('here comes a new fault')
    print('......')
    print('please pick the fault')
    
    #点击获取像素点坐标
    fault_point_pos=plt.ginput(1)[0]

    print('......')
    print('picking the fault')
    
    #注意反过来，因为是xy坐标
    pos_xy=[int(fault_point_pos[0]),int(fault_point_pos[1])]

    pos_IJ=cp.deepcopy(pos_xy)
    
    #IJ形式是xy形式的颠倒
    pos_IJ.reverse()
    
    #所有fault的列表
    total_faults=[]
    
    #这个点到所有fault的距离列表
    distance_total_faults=[]
    
    #建立所有fault的列表
    #计算这个点到fault中心的远近
    for this_fraction in total_fractions:
        
        if isinstance(this_fraction,fault):
            
            #上车上车
            total_faults.append(this_fraction)
     
            #计算距离
            distance_this_fault=Geom.Distance(this_fraction.center,pos_xy)
            distance_total_faults.append(distance_this_fault)
    
    #队距离和fault对象建立索引你关系
    map_distance_total_faults=dict(zip(distance_total_faults,total_faults))
    
#    print(total_faults)
    
    for this_fault in total_faults:
    
        #首先直接判断是否位于content内部
        if pos_IJ in this_fault.content:

            print('......')
            print('picking of the fault is over')
            
            if show:
                
                Dis.ShowEdge(this_fault,img_rgb,axis)
                
            return this_fault
               
    #其次如果第一下没点上，通过计算距离远近来判断
    that_fraction=map_distance_total_faults[min(distance_total_faults)]

    print('......')
    print('picking of the fault is over')
    
    if show:
        
        Dis.ShowEdge(that_fraction,img_rgb,axis)
         
    return that_fraction

#============================================================================== 
#从图像中获取layer对象 
def PickLayer(total_fractions,
              img_rgb,
              show=False,
              axis=True):
    
    print('')
    print('here comes a new layer')
    print('......')
    print('please pick the layer')
    
    #点击获取像素点坐标
    layer_point_pos=plt.ginput(1)[0]

    print('......')
    print('picking the layer')
    
    #注意反过来，因为是xy坐标
    pos_xy=[int(layer_point_pos[0]),int(layer_point_pos[1])]

    pos_IJ=cp.deepcopy(pos_xy)
    
    #IJ形式是xy形式的颠倒
    pos_IJ.reverse()
    
    #所有fault的列表
    total_layers=[]
    
    #这个点到所有fault的距离列表
    distance_total_layers=[]
    
    #建立所有fault的列表
    #计算这个点到fault中心的远近
    for this_fraction in total_fractions:
        
        if isinstance(this_fraction,layer):
            
            #上车上车
            total_layers.append(this_fraction)
     
            #计算距离
            distance_this_layer=Geom.Distance(this_fraction.center,pos_xy)
            distance_total_layers.append(distance_this_layer)
    
    #队距离和fault对象建立索引你关系
    map_distance_total_layers=dict(zip(distance_total_layers,total_layers))
    
#    print(total_faults)
    
    for this_layer in total_layers:
    
        #首先直接判断是否位于content内部
        if pos_IJ in this_layer.content:

            print('......')
            print('picking of the layer is over')
            
            if show:
                
                Dis.ShowEdge(this_layer,img_rgb,axis)
                
            return this_layer
               
    #其次如果第一下没点上，通过计算距离远近来判断
    that_fraction=map_distance_total_layers[min(distance_total_layers)]

    print('......')
    print('picking of the layer is over')
    
    if show:
        
        Dis.ShowEdge(that_fraction,img_rgb,axis)
         
    return that_fraction

#============================================================================== 
#layer附近的fault
def NeighborFault(which_layer,total_fractions):
    
    #判断所处理的是不是个layer
    if not isinstance(which_layer,layer):
        
        print('Incorrect object:Please select a layer')
        
        return
    
    #总的邻居
    neighbor_content=[]
    
    #将layer的edge的邻居全加入列表
    for this_pos in which_layer.edge:
        
        #this_pos的索引
        this_i,this_j=this_pos
        
        #邻居们
        this_neighbor=[[this_i+step_i,this_j+step_j] for step_i in [-1,0,1] for step_j in [-1,0,1]]
        
        #加入总的邻居列表了噢
        neighbor_content+=this_neighbor
      
    #所有的fault
    total_faults=DeleteLayer(total_fractions)
    
    #结果的fault
    result_faults=[]
    
    #判断layer.edge的邻居的tag
    for this_pos in neighbor_content:
        
        #this_pos的索引
        this_i,this_j=this_pos
        
        #判断这些个点在哪个fault里
        for this_fault in total_faults:
            
            #这个点有没有在某个fault内部
            if this_pos in this_fault.content:
                
                result_faults.append(this_fault)
                
    return list(set(result_faults))

#============================================================================== 
#fault附近的layer
def NeighborLayer(which_fault,total_fractions):
    
    #判断所处理的是不是个fault
    if not isinstance(which_fault,layer):
        
        print('Incorrect object:Please select a fault')
        
        return
    
    #总的邻居
    neighbor_content=[]
    
    #将layer的edge的邻居全加入列表
    for this_pos in which_fault.edge:
        
        #this_pos的索引
        this_i,this_j=this_pos
        
        #邻居们
        this_neighbor=[[this_i+step_i,this_j+step_j] for step_i in [-1,0,1] for step_j in [-1,0,1]]
        
        #加入总的邻居列表了噢
        neighbor_content+=this_neighbor
      
    #所有的layer
    total_layers=DeleteFault(total_fractions)
    
    #结果的fault
    result_layers=[]
    
    #判断layer.edge的邻居的tag
    for this_pos in neighbor_content:
        
        #this_pos的索引
        this_i,this_j=this_pos
        
        #判断这些个点在哪个fault里
        for this_layer in total_layers:
            
            #这个点有没有在某个fault内部
            if this_pos in this_layer.content:
                
                result_layers.append(this_layer)
                
    return list(set(result_layers))

#============================================================================== 
#去除layer内的fault
def BorderFaults(which_layer,total_fractions):
    
    #判断所处理的是不是个layer
    if not isinstance(which_layer,layer):
        
        print('Incorrect object:Please select a layer')
        
        return
    
    #相关联的断层可能多个
    which_faults=NeighborFault(which_layer,total_fractions)
    
    #fault内部的断层
    Internal_faults=[]
    
    #存在包围情况的就是层内断层
    for this_fault in which_faults:
        
        #fault边界点中找左右逢源的点
        for this_pos in this_fault.edge:
        
            #I坐标的集合
            I_edge=[this_pos[0] for this_pos in this_fault.edge]
            
        #在I_edge里遍历左右的I相同的点
        for this_I in I_edge:
            
            J_pocket=[]
            
            for this_pos in this_fault.edge:
                
                #找到横坐标相同的点
                if this_pos[0]==this_I:
                    
                    J_pocket.append(this_pos[1])               
            
            #两侧的边界点
            boundary_right=[this_I,max(J_pocket)+1]   
            boundary_left=[this_I,min(J_pocket)-1]
            
            #左右都在说明fault被夹
            if boundary_right in which_layer.edge and boundary_left in which_layer.edge:
                
                #把这个layer内部的fault加进来
                Internal_faults.append(this_fault)
                
                break
    
    return [this_fault for this_fault in which_faults if this_fault not in Internal_faults]
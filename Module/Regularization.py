# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 19:34:47 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Regularization
"""

import numpy as np

from Module import Algebra as Al
from Module import ChipOperation as CO

#============================================================================== 
"""第一轮正则化""" 
def PreRegularization(which_Chip,this_id):

    #第一步将平行四边形中的点都挪到node_quadrangle顶部    
    #切成chips一个个移动好吧
    this_chips_id=which_Chip.id+'-'+str(this_id)
    
    #找到这个chips
    this_chips=CO.SearchByID([which_Chip],this_chips_id)
    
#        print(len(this_chips.content))
#        print(len(this_chips.node_quadrangle))
          
    #确保平行四边形内有content
    if this_chips.content==None:             
        return
    
    if this_chips.content==[]:
        return
    
    if this_chips.top.tag!=which_Chip.top.tag:
        return
#            
    if this_chips.need_to_advanced_regularization:    
        return
    
#    print(this_chips.top.tag)
    
    #横纵坐标
    I_this_chips_content=[pos[0] for pos in this_chips.content]
    I_this_chips_node_quadrangle=[pos[0] for pos in this_chips.node_quadrangle]
    
    #this_chips中的J最高点
    I_this_chips_top_content=min(I_this_chips_content)
    I_this_chips_top_node_quadrangle=min(I_this_chips_node_quadrangle)
    
    #i,j方向上的移动距离
    i_offset=I_this_chips_top_node_quadrangle-I_this_chips_top_content
    j_offset=int(np.floor(-i_offset/which_Chip.k))
    
    this_chips.Move(i_offset,j_offset)
    
    #正则化完成的标志
    this_chips.regularization=True
    
#    print('round 1')
        
#9.2   

#功能细化
#mode表示左中右
"""第二轮正则化""" 
def SubRegularization(which_Chip,this_id,mode,adjustment):
    
    this_chips_id=which_Chip.id+'-'+str(this_id)
    
    #找到这个chips
    this_chips=CO.SearchByID([which_Chip],this_chips_id)
    
#    print(this_chips.id)
#    print('round 2 '+mode) 

    #确保平行四边形内有content
    if this_chips.content==None or this_chips.content==[]:
        return 
    
    #如果不需要这一步，那就滚吧
    if not this_chips.need_to_advanced_regularization:    
        return 
    
    #调整端点
    if adjustment:
        
        #横纵坐标
        I_this_chips_content=[pos[0] for pos in this_chips.content]
        
        I_this_chips_node_quadrangle=[pos[0] for pos in this_chips.node_quadrangle]
        
        #this_chips中的J最高点
        I_this_chips_top_content=min(I_this_chips_content)
        I_this_chips_top_node_quadrangle=min(I_this_chips_node_quadrangle)
        
        #i,j方向上的移动距离
        i_offset=I_this_chips_top_node_quadrangle-I_this_chips_top_content
        j_offset=int(np.floor(-i_offset/which_Chip.k))
        
        this_chips.Move(i_offset,j_offset)
        
        #正则化完成的标志
        this_chips.regularization=True   
        
    #从这里开始使用chipsNearby函数
    chips_nearby=CO.chipsNearby(which_Chip,this_chips,3,mode)

#    print(len(chips_nearby))
    
    #8.31
    
    #chips_nearby所有的id列表
    chips_nearby_id=[this_near_chips.id for this_near_chips in chips_nearby]

#    print(chips_nearby_id)

    #寻觅chips_nearby的两个端点chips
    chips_nearby_id_int=[int(this_near_chips_id.split('-')[1]) for this_near_chips_id in chips_nearby_id]
    
#    print(chips_nearby_id_int)
    
    #chips_nearby的端点
    limit_chips_nearby=[]
    
    #用于计算limit的content内容
    content_limit_chips_nearby=[]
    
    #chips_nearby内部端点的id
    max_id_internal=which_Chip.id+'-'+str(max(chips_nearby_id_int))
    min_id_internal=which_Chip.id+'-'+str(min(chips_nearby_id_int))
    
    #chips_nearby外部端点的id
    max_id_external=which_Chip.id+'-'+str(max(chips_nearby_id_int)+1)
    min_id_external=which_Chip.id+'-'+str(min(chips_nearby_id_int)-1)
    
    id_limit_chips_nearby=[max_id_internal,min_id_internal,
                           max_id_external,min_id_external]
    
#    print(id_limit_chips_nearby)
    
    #判断存在性
    for this_limit_id in id_limit_chips_nearby:
        
        if CO.SearchByID([which_Chip],this_limit_id) is not None:
            
            #chips上船
            limit_chips_nearby.append(CO.SearchByID([which_Chip],this_limit_id))
            
            #content上船
            if this_limit_id==max_id_external or this_limit_id==min_id_external:
                
                content_limit_chips_nearby+=limit_chips_nearby[-1].content
             
    #检验这几个id好吧
#    print([item.id for item in limit_chips_nearby])
  
    #9.1
    
#    print(len(content_limit_chips_nearby))
    
    #用于计算的threshold
    J_content_limit_chips_nearby=[pos[1] for pos in content_limit_chips_nearby]    
    
    limit=[max(J_content_limit_chips_nearby),min(J_content_limit_chips_nearby)]
    
#    print(limit)
    
    #8.24
    
    #计算相邻chips的所有tag集合
    total_tag_chips_nearby=[]
    
    #计算各层的最高点
    for this_near_chips in chips_nearby:
        
        if len(this_near_chips.content)==0:
            continue
        
        total_tag_this_near_chips=[this_chip.tag for this_chip in this_near_chips.total_chip]
       
        #每个chips的tag集合
        total_tag_chips_nearby+=total_tag_this_near_chips
        
#    print('check 1')
    
    #如果啥都没有那也别玩了
    if total_tag_chips_nearby==[]:
        return 
    
#    print('check 2')
    
    #将其取集合运算并转化为列表
    total_tag_chips_nearby=list(set(total_tag_chips_nearby))
    
#    print(total_tag_chips_nearby)
    
    #更正
    total_tag_this_chips=[]
    
    for this_chip in this_chips.total_chip:
        
        if this_chip.content==[] or this_chip.content==None:
            continue
        
        total_tag_this_chips.append(this_chip.tag)
        
#    print(total_tag_this_chips)    
      
    """权利的交接"""
    import copy
    total_tag_chips_nearby=copy.deepcopy(total_tag_this_chips)
    
    #total_tag对应的下家
    total_tag_chips_nearby_total_chip=[]
    
    #建立不同tag的dict组成的列表  
    for this_tag in total_tag_chips_nearby:
        
        #this_tag在nearby中所有的chip的集合
        this_tag_chips_nearby_total_chip=[]
        
        for this_near_chips in chips_nearby:
            
            this_chip_id=this_near_chips.id+'|'+str(this_tag)
            
#            print(this_chip_id)
            
            this_chip=CO.SearchByID([which_Chip],this_chip_id)            
            this_tag_chips_nearby_total_chip.append(this_chip)
        
        #建立索引:map表示映射关系          
        total_tag_chips_nearby_total_chip.append(this_tag_chips_nearby_total_chip)
        
    #建立map的集合
    total_map=dict(zip(total_tag_chips_nearby,total_tag_chips_nearby_total_chip))
   
#    print(total_map)
#    print(list(total_map.keys()))
    
    #8.25
            
    #用于存储所有的this_tag_top_chips_nearby的列表
    top_total_tag=[]
    
    for this_tag in list(total_map.keys()):
        
        #chips_nearby中每个tag的chip的最高点I的集合    
        I_top_this_tag_chips_nearby=[]
        
        #以及I_J的集合
        I_J_top_this_tag_chips_nearby=[]
        
        for this_chip in total_map[this_tag]:
            
            #确保非空
            if this_chip==None:
                continue         
            
            if this_chip.content!=[] or this_chip.content!=None:

                I_this_chip=[pos[0] for pos in this_chip.content]   
                J_this_chip=[pos[1] for pos in this_chip.content]  
                
                #建立索引
                map_I_J_this_chip=dict(zip(I_this_chip,J_this_chip))
                
                I_top_this_chip=min(I_this_chip)
                J_top_this_chip=map_I_J_this_chip[I_top_this_chip]
                
                I_top_this_tag_chips_nearby.append(I_top_this_chip)
                I_J_top_this_tag_chips_nearby.append([I_top_this_chip,J_top_this_chip])
        
        #8.28
        
#        print(I_top_this_tag_chips_nearby)
#        print(I_J_top_this_tag_chips_nearby)
        
        #如果top_this_tag_chips_nearby为空：不可以让分母为0对吧
        if I_top_this_tag_chips_nearby==[] or I_J_top_this_tag_chips_nearby==[]:
            
            #要添加进列表的值
            top_this_tag=None
        
        #无异常就正常计算  
        #一般情况下使用插值
        else:                           
            top_this_tag=Al.CalculateThisPoint(I_J_top_this_tag_chips_nearby,
                                            'interpolation',
                                            this_chips,
                                            limit)
            #特殊情况下使用平均值
            if top_this_tag==None:
                
                 top_this_tag=Al.CalculateThisPoint(I_J_top_this_tag_chips_nearby,
                                                 'average')
            
        top_total_tag.append(top_this_tag)
        
#    print(top_total_tag)  
    
    #建立this_tag和this_tag_top的索引
    map_total_tag_top=dict(zip(total_tag_chips_nearby,top_total_tag))
  
#    print(list(map_total_tag_top.values()))
#    print(map_total_tag_top)
#    print(this_chips.top.tag)
    
    new_top_this_chips=min(map_total_tag_top.values())
    
    #计算咯
    #计算this_chips各个tag的chip相应的最高I值
    if this_chips.content!=[]:
        
#        print('good')
        
        I_this_chips=[pos[0] for pos in this_chips.content]
        now_top_this_chips=min(I_this_chips)
        
#        print(this_chips.id)
#        print(new_top_this_chips)
#        print(now_top_this_chips)
                  
        #i,j方向上的移动距离
        i_offset=new_top_this_chips-now_top_this_chips
        j_offset=int(np.floor(-i_offset/which_Chip.k))
    
#        print(i_offset,j_offset)
        
        this_chips.Move(i_offset,j_offset)
        
        I_this_chips=[pos[0] for pos in this_chips.content]
        now_top_this_chips=min(I_this_chips)
        
#        print(now_top_this_chips)
        
        #正则化完成的标志
        this_chips.regularization=True         

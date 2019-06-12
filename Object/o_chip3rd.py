# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:54:49 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-chip3rd
"""

import copy as cp
import numpy as np
import matplotlib.pyplot as plt

from Object.o_fraction import fraction

from Module import Regularization as Reg

"""第三类chip"""
#==============================================================================       
#建立Chip列表
#total_chips=[chips_1,chips_2,chips_3...]
#plate是Chip对应的plate对象
#node_quadrangle表示小平行四边形chips的边界点的集合
#regularization表示是否被矫正过
#fault_content表示tag为fault对象的点的集合
#==============================================================================  
"""增加top和others对象？"""
class chip3rd:
    def __init__(self,id=None,  
                 total_chips=None,
                 total_tag=None,
                 content=None,
                 center=None,
                 plate=None,
                 node_quadrangle=None,
                 top=None,
                 others=None,
                 fault=None,
                 fault_content=None,
                 tilt=None,
                 k=None,
                 regularization=None):
        
        self.id=id
        self.total_chips=total_chips  
        self.total_tag=total_tag
        self.content=content
        self.center=center
        self.plate=plate
        self.node_quadrangle=node_quadrangle
        self.top=top
        self.others=others
        self.fault=fault
        self.fault_content=fault_content
        self.tilt=tilt
        self.k=k
        self.regularization=regularization
        
    #初始化
    def Init(self):
        
        self.content=[]
        self.total_tag=[]
        
        #初始化chipses的点坐标content
        for this_chips in self.total_chips:
            
            this_chips.Init()
            self.content+=this_chips.content
            
            #初始化Chip包含的所有tag
            for this_chip in this_chips.total_chip:
                
                if this_chip.tag not in self.total_tag:
                    
                    self.total_tag.append(this_chip.tag)
        
        #初始化center
        if self.content!=[]:
            
            I=[pos[0] for pos in self.content]
            J=[pos[1] for pos in self.content]
            
            I_center=(max(I)+min(I))/2
            J_center=(max(J)+min(J))/2
            
            self.center=[I_center,J_center]
            
        """"""
        #初始化top
        self.UpdateTop()
        
        #tag为-1的对象
        #暂时不能将其作为fraction对象
        self.fault_content=[]
        
        #先将fault存为一个大型的content集合，然后膨胀后再对其进行初始化
        
        for this_chips in self.total_chips:

            for this_chip in this_chips.total_chip:
                
                for pos in this_chip.content:
                
                    if this_chip.tag==-1:
                        
                        self.fault_content.append(pos)
        
    #平移一定的距离
    def Move(self,i_offset,j_offset):  
        
        #移动content
        for pos in self.content:
            
            pos[0]+=i_offset
            pos[1]+=j_offset
            
        #移动边框
        for pos in self.node_quadrangle:
            
            pos[0]+=i_offset
            pos[1]+=j_offset
            
        #center更新
        if self.center!=None:
            
            self.center=[self.center[0]+i_offset,self.center[1]+j_offset]
        
    #移动至pos_P的某一侧
    def MoveTo(self,pos_P,side):
        
        self.Init()
        
        #分别计算I,J方向上的移动距离    
        #J_offset是整个Chip统一的
        
#        print(len(self.content))
        
        J_chips=[pos[1] for pos in self.content]

#        print(len(J_chips))        
        
        if side=='left':
            J_offset=pos_P[1]-max(J_chips)-1
        
        if side=='right':
            J_offset=pos_P[1]-min(J_chips)+1
            
        #Chip中的每个chips纵向移动分量不一    
        for this_chips in self.total_chips:

            I_chips=[]
            
            for pos in this_chips.content:
                
                if pos in self.plate.top.content:
                    
                    I_chips.append(pos[0])
                    
            #确保集合非空
            if I_chips!=[]:

                I_offset=pos_P[0]-min(I_chips)
                
                this_chips.Move(I_offset,J_offset)
            
    #显示Chip对象
    def Show(self,img_rgb,rgb_dict,grid='off'):
        
        #显示找到的内容         
        background_rgb=img_rgb[0,0]
        img_temp=np.full(np.shape(img_rgb),background_rgb)
             
        #Chip主体着色
        for this_chips in self.total_chips:
            for this_chip in this_chips.total_chip:
                for pos in this_chip.content:       
                    img_temp[pos[0],pos[1]]=rgb_dict[this_chip.tag]   
        
        #是否存在四边形边框            
        if grid=='on':

            #平行四边形边框
            for pos in self.node_quadrangle:
                img_temp[pos[0],pos[1]]=np.array([0,0,0]) 
            
        #在图中显示
        plt.figure()
        plt.imshow(img_temp)
          
    #更新Chip的id函数
    def UpdateID(self):
        
        #初始化哟
        chips_id=1
        
        #逐层更新
        for this_chips in self.total_chips:
            
            this_chips.id=self.id+'-'+str(chips_id)   
            chips_id+=1
        
#            print(this_chips.id)
            
            #更新chip的id
            for this_chip in this_chips.total_chip:
                
                this_chip.id=this_chips.id+'|'+str(this_chip.tag)
            
#                print(this_chip.id)
      
    #9.4
          
    #正则化
    def Regularize(self,adjustment=True):
        
    #    print(which_Chip.id)
    #    print(which_Chip.top.tag)
    #    print(which_Chip.total_tag)  
           
        #8.16
     
        #通过need_to_advanced_regularization参数计算n_special
        id_list_to_calculate_n_special=[]
        
        for this_chips in self.total_chips:
            
            if this_chips.need_to_advanced_regularization:
                
                id_list_to_calculate_n_special.append(int(this_chips.id.split('-')[1]))
    
#        print(id_list_to_calculate_n_special)  
        
        #8.17
        
        #左区间的起点和终点
        #虽然经过了初始化的处理，但是这几个节点还是需要计算的
        left_external=id_list_to_calculate_n_special[0]
        
        #计算n_special之路
        left_internal=id_list_to_calculate_n_special[0]
                
        for k in range(1,len(id_list_to_calculate_n_special),+1):    
            
#            print(k)
            
            #判断是否连续
            if id_list_to_calculate_n_special[k-1]==id_list_to_calculate_n_special[k]-1:               
               
                left_internal+=1
            
            #若这种连续中止了
            else:
                break
        
        #右区间的起点和终点
        
        right_external=id_list_to_calculate_n_special[-1]
        right_internal=id_list_to_calculate_n_special[-1]
        
        for k in range(len(id_list_to_calculate_n_special)-1,0,-1): 
            
#            print(k)
            
            #判断是否连续
            if id_list_to_calculate_n_special[k-1]==id_list_to_calculate_n_special[k]-1:               
                
                right_internal-=1
                
            #若这种连续中止了
            else:
                break
     
#        print(left_external,left_internal)
#        print(right_external,right_internal)
        
        """第一轮正则化"""
        
        print('')
        
        for this_id in range(left_internal,right_internal):
            
            Reg.PreRegularization(self,this_id)
         
        print('......')    
        print('the end of round 1')
        
        """第二轮正则化"""    
    
        print('')
        
        #分段函数,且从某一头取滑动点集
        #分组调试

        #中点
        medium=len(self.total_chips)/2
        
        #左段 
        if medium>=left_internal>=left_external:

            for this_id in range(left_internal,left_external-1,-1):
                
#                print('left')
                
                Reg.SubRegularization(self,this_id,'right',adjustment)
            
        #右段    
        if medium<=right_internal<=right_external:
            
            for this_id in range(right_internal,right_external+1,+1):
                
#                print('right')
                
                Reg.SubRegularization(self,this_id,'left',adjustment)    
        
        """有问题"""
        #中段
#        for this_id in range(left_internal,right_internal):
#            
#            whj.SubRegularization(self,this_id,'middle',adjustment)
    
        print('......')    
        print('the end of round 2')  
         
#9.5
    
    #更新Chip的top,也可作初始化
    def UpdateTop(self):
    
#        print(which_Chip.total_tag)
        
        total_tag=cp.deepcopy(self.total_tag)
        
        #top不可以是fault
        if -1 in total_tag:
            total_tag.remove(-1)
        
        #所有tag的高度
        total_tag_top=[]
        
        #所有tag的fraction
        total_tag_fraction=[]
        
        for this_tag in total_tag:
            
            this_tag_fraction=fraction()
            this_tag_content=[]
            
            for this_chips in self.total_chips:
    
                for this_chip in this_chips.total_chip:
                    
                    for pos in this_chip.content:
                    
                        if this_tag==this_chip.tag:
                            
                            this_tag_content.append(pos)
                            
            #I坐标取平均，求最小值                
            I_this_tag=[pos[0] for pos in this_tag_content]
            top_I_this_tag=np.mean(I_this_tag)   
            
            this_tag_fraction.content=this_tag_content
            this_tag_fraction.tag=this_tag
            
            #上车上车
            total_tag_top.append(top_I_this_tag)
            total_tag_fraction.append(this_tag_fraction)
                
        #平均I与total_tag的索引
        map_top_total_tag=dict(zip(total_tag_top,total_tag))
        
        #total_tag和content的索引
        map_total_tag_fraction=dict(zip(total_tag,total_tag_fraction))  
              
        #不加这一限制条件说明没有top了
        if total_tag_top!=[]:
            
            #求目标tag值
            target_tag=map_top_total_tag[min(total_tag_top)]   
            
    #        print(target_tag)
            
            #更新top
            top_content=[]
            
            for this_chips in self.total_chips:
                
                for this_chip in this_chips.total_chip:
                    
                    if this_chip.tag==target_tag:
                        
                        top_content+=this_chip.content
            
            #定义top
            self.top=fraction()
            self.top.content=top_content
            self.top.tag=target_tag
            
            #移除top
            del map_total_tag_fraction[map_top_total_tag[min(total_tag_top)]]
        
            #定义pthers
            self.others=list(map_total_tag_fraction.values())
        
        #检验模块
#        print(self.top.tag)
#        
#        for this_fraction in self.others:
#            print(this_fraction.tag)
     
    #将Chip转化为plate
    def ToPlate(self):
        
        pass
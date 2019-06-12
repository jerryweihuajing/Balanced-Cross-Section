# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:41:57 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-plate
"""

import copy as cp
import numpy as np

from Object.o_fault import fault
from Object.o_chip1st import chip1st
from Object.o_chip2nd import chip2nd
from Object.o_chip3rd import chip3rd

import Module.Display as Dis
import Module.Initialize as Init

#==============================================================================  
#定义plate这个类
#top表示即将被剥去的fraction
#others并表示底下的fraction们（list）
#fractions表示plate包含的所有fraction对象
#content表示fractions的坐标集合
#==============================================================================  
class plate:
    def __init__(self,
                 top=None,
                 others=None,
                 fault=None,
                 fractions=None,
                 content=None):
        self.top=top
        self.others=others
        self.fault=fault
        self.fractions=fractions
        self.content=content
        
    #plate初始化
    def Init(self,fractions):
        
        #定义fractions属性
        self.fractions=fractions
        
        #将输入的fractions分开成顶部fraction和底下的fractions 
        #height为fraction的高度
        depth=[]  
        
        for this_fraction in fractions:
            
            this_fraction.UpdateCenter()
            depth.append(this_fraction.center[0])
        
        #建立一个字典表示fraction的纵坐标和fraciton的对应关系
        height_fractions=dict(zip(depth,fractions))
        
        #深度最浅的是top的fraction  
        self.top=height_fractions[min(depth)]
        
        """不对，应该删除所有tag与之相同的fraction，之后遇到问题再改"""  

        #除了top其余的是others
        temp_fractions=cp.copy(fractions)          
        temp_fractions.remove(self.top)  
        
        self.others=temp_fractions  
        
        #定义content属性
        self.content=[] 
        
        #self.content=content[0]+content[1]+...content[n-1]
        for this_fraction in fractions:
            self.content+=this_fraction.content
    
        #初始化fault属性
        self.fault=[]
        
        #加入fault对象们
        for this_fraction in self.fractions:
            
            if isinstance(this_fraction,fault):
                
                self.fault.append(this_fraction)
            
    #显示plate对象
    def Show(self,img_rgb,rgb_dict,text=False,output=False):
        
        Dis.ShowFractions(self.fractions,img_rgb,rgb_dict,text,output)   
        
        
    #plate整体移动函数    
    def Move(self,i_offset,j_offset):
               
        #进行移动，调用类方法，并修改所有参数
        for this_fraction in self.fractions:
            this_fraction.Move(i_offset,j_offset)
            
        #根据修改的参数，重新定义plate对象
        self.Init(self.fractions)
    
    #plate的像素点集合的上下左右坐标
    def Threshold(self):
        
        #求content中坐标的最大值和最小值
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]

        #上下左右
        left,right,bottom,top=min(J),max(J),max(I),min(I)
        
        return left,right,bottom,top
    
    #plate对象转化为fractions
    def Tofractions(self):
        
        #将top和others收录进来
        total_fractions=self.others
        total_fractions.append(self.top)
        
        return total_fractions
    
    #9.4
    
    #plate转化为chip对象的函数 
    #which_fault是划分上下盘的fault
    #width是切片宽度
    #Chip_id是Chip的名字
    def ToChip(self,which_fault,img_tag,width,Chip_id):
        
        #获取fault倾角和斜率
        tilt,k=Init.InitTilt(which_fault)
        
    #    print(k)
        
        #分别取layer中的最大值和最小值
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]
        
        #大偏移距(绝对值)
        J_total_offset=(max(I)-min(I))/abs(k)  
        
        #分段有利于提高计算速度：特殊区段
        n_special=int(np.ceil(J_total_offset/width))
        
        #分成n段：四边形角落多出一块
        n=int(np.ceil((max(J)-min(J)+(J_total_offset))/width))
        
#        print(n)
#        print(n_special)
#        print(n-n_special)
#        print(len(which_plate.content))
        
        #plate中的所偶tag
        tags=[this_fraction.tag for this_fraction in self.Tofractions()]
        total_tag=list(set(tags))
        
    #    print(total_tag)
        
        #总chips对象列表
        total_chips=[]
        
        #创建一个表示平行四边形端点的列表
        that_Chip_node_quadrangle=[]
          
        #大平行四边形四个顶点
    #    print(type(I))
    #    print(type(J))
    
        #斜率分类讨论    
        if k>0:   
            pos_A=[min(I),max(J)]
            pos_B=[max(I),max(J)+J_total_offset]
            
        if k<0:
            pos_A=[min(I),max(J)]
            pos_B=[max(I),max(J)-J_total_offset]
            
    #    print(pos_A,pos_B)
    #    print(len(which_plate.content))
        
        for m in range(n,0,-1): 
            
            #创建一个表示平行四边形端点的列表
            that_chips_node_quadrangle=[]
            
            pos_C=[min(I),pos_A[1]-width]
            pos_D=[max(I),pos_B[1]-width]
            
            ABCD=[pos_A,pos_B,pos_C,pos_D]
            
            #在这四个点横纵坐标的最大范围内进行搜索
            I_quadrangle_point=[pos[0] for pos in ABCD]
            J_quadrangle_point=[pos[1] for pos in ABCD]
            
            I_max=max(I_quadrangle_point)
            I_min=min(I_quadrangle_point)   
            J_max=max(J_quadrangle_point)
            J_min=min(J_quadrangle_point)
             
    #        print(I_max,I_min,J_max,J_min)
            
            this_chip=chip1st()
            
            #初始化
            this_chip.k=k
            this_chip.part=m
            this_chip.tilt=tilt
            this_chip.inclination=which_fault.inclination
            this_chip.content=[]
      
            #填充横向点
            if k>0:    
                for JJ in range(int(np.ceil(J_max)),int(np.ceil(J_total_offset+J_min)),-1):   
                    
                    that_chips_node_quadrangle.append([I_max,JJ-int(np.ceil(J_total_offset))])
                    that_chips_node_quadrangle.append([I_min,JJ])
                
            if k<0:        
                for JJ in range(int(np.ceil(J_max)),int(np.ceil(J_total_offset+J_min)),-1):   
                    
                    that_chips_node_quadrangle.append([I_min,JJ])
                    that_chips_node_quadrangle.append([I_max,JJ+int(np.ceil(J_total_offset))])
                
    #        print(len(node_quadrangle))
            
            #收录which_plate中的点
            for i in range(I_min,I_max+1):
                
                #用斜率联系IJ
                I_offset=i-I_min
                J_offset=I_offset/k
                
                #收录端点
                start=int(np.round(J_max-J_offset-width))
                end=int(np.round(J_max-J_offset))
                
                that_chips_node_quadrangle.append([i,start])
                that_chips_node_quadrangle.append([i,end])
                
                for j in range(end,start,-1):
                    
                    #根据tag值进行收录
                    if img_tag[i,j] in total_tag:   
                        
                        #增加判断条件
                        if [i,j] in self.content:
                            
                            this_chip.content.append([i,j])
            
#            print(len(this_chip.content))     
            
            #计算下一个平行四边形                
            pos_A[1]-=width
            pos_B[1]-=width                                                
            
            #一个chip分成多个chip
            #这一个小四边形中的所有chip
            total_chip=[]
            
            #将this_chip拆成不同tag的多个部分
            for target_tag in total_tag:
                
                that_chip=chip1st()
                that_chip.tag=target_tag
                that_chip.k=k
                that_chip.part=m
                that_chip.tilt=tilt
                that_chip.inclination=which_fault.inclination
                that_chip.content=[]
                
                for pos in this_chip.content:
                    
                    #根据tag进行划分
                    if img_tag[pos[0],pos[1]]==target_tag:   
                        
                        that_chip.content.append(pos)
                        
#                print(len(that_chip.content))
                      
                #确保that_chip有点东西才添加它
                if that_chip.content!=[]:
                    
                    total_chip.append(that_chip)
                
            #建立新的chips对象
            that_chips=chip2nd()
            
            #初始化
            that_chips.k=k
            that_chips.part=m
            that_chips.tilt=tilt
            that_chips.total_chip=total_chip      
            that_chips.node_quadrangle=that_chips_node_quadrangle
            that_chips.Init() 
            that_chips.need_to_advanced_regularization=False
            
            #特殊处理区段
            if that_chips.part<n_special or that_chips.part>=n-n_special:
                
                #得有点东西吧
#                if that_chips.content!=[] and that_chips.content!=None:
               
                that_chips.need_to_advanced_regularization=True

#                print(that_chips.part)
                    
#            #检验一波
#            if that_chips.top!=None:
#                
#                print(that_chips.top.tag)
            
            #添加至chips列表
            total_chips.append(that_chips)
            that_Chip_node_quadrangle+=that_chips_node_quadrangle
            
        #建立新的Chip对象
        that_Chip=chip3rd()
        
        #初始化各属性
        that_Chip.id=Chip_id
        that_Chip.k=k
        that_Chip.tilt=tilt
        that_Chip.total_chips=total_chips
        that_Chip.plate=self
        that_Chip.node_quadrangle=that_Chip_node_quadrangle
        that_Chip.Init()
        that_Chip.UpdateID()
        
        return that_Chip
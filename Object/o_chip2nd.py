# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:51:38 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-chip2nd
"""

import numpy as np 
import matplotlib.pyplot as plt

"""第二类chip"""
#==============================================================================  
#total_chip表示chip列表
#total_chip=[chip_1,chip_2,chip_3...]
#node_quadrangle表示小平行四边形的边界点
#regularization表示是否被矫正过
#==============================================================================  
class chip2nd:
    def __init__(self,id=None,
                 total_chip=None,
                 total_tag=None,
                 content=None,
                 center=None,
                 top=None,
                 others=None,
                 node_quadrangle=None,
                 tilt=None,
                 k=None,
                 regularization=None,
                 need_to_advanced_regularization=None):
        
        self.id=id
        self.total_chip=total_chip
        self.total_tag=total_tag
        self.content=content
        self.center=center
        self.top=top
        self.others=others
        self.node_quadrangle=node_quadrangle
        self.tilt=tilt
        self.k=k
        self.regularization=regularization
        self.need_to_advanced_regularization=need_to_advanced_regularization
        
    #初始化
    def Init(self):
         
        #初始化所有tag
        self.total_tag=[this_chip.tag for this_chip in self.total_chip]
        
#        print(len(self.total_chip))     
#        print(self.total_chip[0].tag)
           
        self.content=[]
        
        for this_chip in self.total_chip:
            
            this_chip.InitCenter()
            self.content+=this_chip.content    
                       
#        print(len(self.content))
#        print(len(self.total_chip))
        
        if self.content!=[]:
            
            I=[pos[0] for pos in self.content]
            J=[pos[1] for pos in self.content]
            
            I_center=(max(I)+min(I))/2
            J_center=(max(J)+min(J))/2
            
            self.center=[I_center,J_center]
            
        #total_chip中删除fault，即刻删除tag为-1的chip
        total_chip_temp=[this_chip for this_chip in self.total_chip if this_chip.tag!=-1]
        
        #建立chip和chip的center的索引        
        depth=[]

        for this_chip in total_chip_temp:
            
            #确保中心存在
            if this_chip.center!=None:              
                depth.append(this_chip.center[0])
                    
#                    if this_chip.center==None:
#                        depth.append(None)
        if depth!=[]:
            
            #建立top和others
            others_temp=self.total_chip.copy()
            
            depth_chip=dict(zip(depth,others_temp))
            
            top_temp=depth_chip[min(depth)]
               
#            若这个chip的content不存在，则重新排序
#            while top_temp==None:
#                    
#                depth.remove(min(depth))
#                others_temp.remove(None)
#                
#                depth_chip=dict(zip(depth,others_temp))
#                
#                top_temp=depth_chip[min(depth)]
            
            #正常情况
            self.top=top_temp
            self.others=[this_chip for this_chip in others_temp if this_chip!=top_temp]
            
#            print(self.top.tag)
                
    #移动(I_offset,J_offset)个单位
    def Move(self,I_offset,J_offset):

        #从属的chip移动
        for this_chip in self.total_chip:
            
            this_chip.Move(I_offset,J_offset)
            
        #center更新
        if self.center!=None:
            
            self.center=[self.center[0]+I_offset,self.center[1]+J_offset]
        

    #显示chips对象
    def Show(self,img_rgb,rgb_dict,output=False,axis=False):
        
        #显示找到的内容         
        background_rgb=img_rgb[0,0]
        img_temp=np.full(np.shape(img_rgb),background_rgb)
             
        #着色
        for this_chip in self.total_chip:
            
            for pos in this_chip.content:       
               
                img_temp[pos[0],pos[1]]=rgb_dict[this_chip.tag]   
            
        #在图中显示
        plt.figure()
        plt.imshow(img_temp)
        
        #要不要坐标轴呢
        if axis:
            
           plt.axis('off')
           
        #是否输出矩阵哦
        if output:
           
            return img_temp      
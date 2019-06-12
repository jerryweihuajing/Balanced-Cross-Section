# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:50:09 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-chip1st
"""

import numpy as np
import matplotlib.pyplot as plt

from Object.o_fraction import fraction

"""第一类chip"""
#==============================================================================                 
#定义平行四边形切片
#==============================================================================  
class chip1st(fraction):
      
    #先继承,后重构
    def __init__(self,id=None,
                 tag=None,
                 part=None,
                 content=None,
                 center=None,
                 inclination=None,
                 tilt=None,
                 k=None):  
        
        #继承父类的构造方法
        fraction.__init__(self,tag=None,
                          part=None,
                          content=None)  
        
        self.inclination=inclination
        self.tilt=tilt
        self.k=k
        self.id=id
        
    #初始化center
    def InitCenter(self):
        
        if self.content!=[]:
            
            I=[pos[0] for pos in self.content]
            J=[pos[1] for pos in self.content]
            
            I_center=(max(I)+min(I))/2
            J_center=(max(J)+min(J))/2
            
            self.center=[I_center,J_center]
        
    #平移chip对象
    def Move(self,i_offset,j_offset):
        
        #更新content
        for pos in self.content:
            
            pos[0]+=int(i_offset)
            pos[1]+=int(j_offset)
            
    #显示chip对象
    def Show(self,img_rgb,rgb_dict,output=False):
        
        #显示找到的内容         
        background_rgb=img_rgb[0,0]
        img_temp=np.full(np.shape(img_rgb),background_rgb)
             
        #着色
        for pos in self.content:
            img_temp[pos[0],pos[1]]=rgb_dict[self.tag]   
            
        #在图中显示
        plt.figure()
        plt.imshow(img_temp)
        
        if output:
            
            return img_temp
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 20:10:18 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Image
"""

import numpy as np
import matplotlib.pyplot as plt

from Module import Dictionary as Dict

#==============================================================================     
#补色变换
def ReverseRGB(img_rgb):
    
    return np.array([255,255,255]-img_rgb,dtype=np.uint8) 

#==============================================================================    
#由img_rgb生成img_tag
def RGB2Tag(img_rgb,rgb_dict,show=False,axis=False):
    
    img_tag=np.zeros((np.shape(img_rgb)[0],np.shape(img_rgb)[1]))
    
    #给img_tag矩阵赋值
    for i in range(np.shape(img_tag)[0]):
        
        for j in range(np.shape(img_tag)[1]):
            
            img_tag[i,j]=Dict.DictKeyOfValue(rgb_dict,list(img_rgb[i,j].astype(int)))
    
    #显示
    if show:
        
        plt.figure()
        plt.imshow(img_tag,cmap='gray')
        
        #显示坐标轴吗
        if axis:
            
            plt.axis('off')
            
    return img_tag

#==============================================================================    
#由img_tag生成img_rgb
def Tag2RGB(img_tag,rgb_dict,show=False,axis=False):
    
    #初始化这个rgb矩阵
    img_rgb=np.zeros((np.shape(img_tag)[0],np.shape(img_tag)[1],3))

    #给img_rgb矩阵赋值
    for i in range(np.shape(img_rgb)[0]):
        
        for j in range(np.shape(img_rgb)[1]):
            
#            print(img_tag[i,j])
#            print(rgb_dict[int(img_tag[i,j])])

            #注意dtype，必须是uint8才能正常显示RGB
            img_rgb[i,j]=np.array(rgb_dict[img_tag[i,j]])
    
    #转化为正确输出格式      
    img_rgb=np.array(img_rgb,dtype=np.uint8)  
      
    #显示
    if show:
        
        plt.figure()
        plt.imshow(img_rgb)
        
        #显示坐标轴吗
        if axis:
            
            plt.axis('off')
            
    return img_rgb

#==============================================================================   
#计算base_tag的方法
def GetBaseTag(img_tag):
    
    """从图像末尾进行扫描，获取到的非背景色的tag或rgb就是"""
    for i in range(np.shape(img_tag)[0]-1,0,-1):
        
        #只要不是全空白那就一定是它咯
        if list(img_tag[i])!=list(img_tag[-1]):  
            
            break
    
    #取中间值
    return img_tag[i,int(np.shape(img_tag)[1]/2)]

#==============================================================================  
#boundary rectangular boundary
def BoundaryImg(which_fraction,img_rgb):
    
    I=[this_pos[0] for this_pos in which_fraction.edge]
    J=[this_pos[1] for this_pos in which_fraction.edge]
    
    #maximum and minimum of I,J 
    #the first layer
    img_rgb[min(I):max(I)+1,max(J)]=np.array([0,0,0],dtype=np.uint8)
    img_rgb[min(I):max(I)+1,min(J)]=np.array([0,0,0],dtype=np.uint8)  
    img_rgb[min(I),min(J):max(J)+1]=np.array([0,0,0],dtype=np.uint8)
    img_rgb[max(I),min(J):max(J)+1]=np.array([0,0,0],dtype=np.uint8)
    
    #the second layer
    img_rgb[min(I)-1:max(I)+2,max(J)+1]=np.array([0,0,0],dtype=np.uint8)
    img_rgb[min(I)-1:max(I)+2,min(J)-1]=np.array([0,0,0],dtype=np.uint8)  
    img_rgb[min(I)-1,min(J)-1:max(J)+2]=np.array([0,0,0],dtype=np.uint8)
    img_rgb[max(I)+1,min(J)-1:max(J)+2]=np.array([0,0,0],dtype=np.uint8)
    
    return img_rgb

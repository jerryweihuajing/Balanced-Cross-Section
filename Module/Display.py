# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 16:25:25 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Show
"""

import numpy as np
import matplotlib.pyplot as plt

#============================================================================== 
#显示某个列表中的所有像素点
#something为要显示的对象
def ShowSomething(img_rgb,
                  which_thing,
                  which_tag,
                  rgb_dict,
                  axis=False,
                  output=False):  
    
    #显示找到的集合
    background_rgb=img_rgb[0,0]
    img_temp=np.full(np.shape(img_rgb),background_rgb)
    
    #赋予目标对象的位置
    for item in which_thing:
        
        i,j=item[0],item[1]
        img_temp[i,j]=rgb_dict[which_tag]   
        
    #在图中显示
    plt.figure()
    plt.imshow(img_temp)
    
    #是否显示坐标轴
    if axis:
        
        plt.axis('off')
    
    #是否输出矩阵
    if output:
        
        return img_temp
    
#==============================================================================     
#显示fraction对象的边界点
def ShowEdge(fraction,img_rgb,axis=True):
    
    #对所有的边界点，赋予全0的rgb值
    for pos in fraction.edge:
        
        img_rgb[pos[0],pos[1]]=np.array([0,0,0])
        
    plt.imshow(img_rgb)   
    
    #是否显示坐标轴
    if not axis:
        
        plt.axis('off')
 
#============================================================================== 
#在图中用正方形标记某个点      
#length_of_side为方框的边长的一半       
def ShowOnePoint(pos,img_rgb,length_of_side=3):
 
    #转化为整数
    pos=np.round(pos).astype(int)
    
    #对正方形边赋值
    img_rgb[pos[0]-length_of_side,pos[1]-length_of_side:pos[1]+length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]+length_of_side,pos[1]-length_of_side:pos[1]+length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]-length_of_side:pos[0]+length_of_side,pos[1]-length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]-length_of_side:pos[0]+length_of_side,pos[1]+length_of_side]=np.array([0,0,0])
    
    #对正方形角赋值
    img_rgb[pos[0]-length_of_side,pos[1]-length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]+length_of_side,pos[1]-length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]-length_of_side,pos[1]+length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]+length_of_side,pos[1]+length_of_side]=np.array([0,0,0])
    
    plt.imshow(img_rgb) 
    
    axis=False
    
    #是否显示坐标轴
    if not axis:
        
        plt.axis('off')
        
    return img_rgb

#============================================================================== 
#给定像素点坐标，用红色显示
def Line2Red(which_content,img_rgb):
    
    plt.close()
    
    #着色
    for pos in which_content:
        
        img_rgb[int(pos[0]),int(pos[1])]=np.array([255,0,0])
      
    plt.figure()
    plt.imshow(img_rgb)
    
    return img_rgb
    
"""设计通过显示tag和part显示块体的函数"""
#============================================================================== 
#写一个同时能显示很多tag像素点的函数，混合tag，显示对象为fraction对象的集合
#显示多个fraction对象的函数
def ShowFractions(fractions,
                  img_rgb,
                  rgb_dict,
                  axis=False,
                  text=False,
                  output=False):
    
    #显示找到的内容
    background_rgb=img_rgb[0,0]
    img_temp=np.full(np.shape(img_rgb),background_rgb)
    
    #赋予目标对象的位置
    for this_fraction in fractions:
        
        #tag,part,content,center      
        tag=this_fraction.tag
        part=this_fraction.part
        content=this_fraction.content
        center=this_fraction.center
    
        #着色
        for pos in content:
            i,j=pos[0],pos[1]
            img_temp[i,j]=rgb_dict[tag] 
            
            if text:     
                #annotate函数:s表示输出的文本，
                plt.annotate(s='tag'+' '+str(tag)+' '+'part'+' '+str(part),
                             #xy表示中心点坐标
                             xy=center,
                             #xycoords表示输出类型，默认为'data'
                             xycoords='data',
                             #fontsize字体
                             fontsize=10,
                             #xytext和textcoords='offset points'对于标注位置的描述和x偏差值
                             textcoords='offset points',
                             #4个字符相当于2个fontsize
                             xytext=(-20,0))          

    plt.imshow(img_temp)
    
    #是否显示坐标轴
    if not axis:
        
        plt.axis('off')
    
    #是否输出矩阵
    if output:
        
        return img_temp
    
#==============================================================================     
#显示多个plate对象的函数
#plates是plate对象组成的列表
def ShowPlates(which_plates,
               img_rgb,
               rgb_dict,
               axis=True,
               text=False,
               output=False):
        
    #建立总fractions列表
    total_fractions=[]
    
    #遍历plates中的每一个plate
    for this_plate in which_plates:

        #将每一个fraction对象都放进来
        total_fractions+=this_plate.fractions
        
    #显示
    ShowFractions(total_fractions,img_rgb,rgb_dict,text,axis,output)  
    
#==============================================================================      
#Chips表示chip3rd对象列表
def ShowChips(which_Chips,
                img_rgb,
                rgb_dict,
                axis=True,
                grid='off'):
    
    #显示找到的内容         
    background_rgb=img_rgb[0,0]
    img_temp=np.full(np.shape(img_rgb),background_rgb)
    
    #给像素点赋予rgb值
    for this_Chip in which_Chips:
         
        #Chip的颜色
        for this_chips in this_Chip.total_chips:
            
            for this_chip in this_chips.total_chip:
                
                for pos in this_chip.content:
                    
                    img_temp[int(pos[0]),int(pos[1])]=rgb_dict[this_chip.tag]
        
        #网格表示
        if grid=='on':
        
            #平行四边形边框
            for pos in this_Chip.node_quadrangle:
                
                img_temp[int(pos[0]),int(pos[1])]=np.array([0,0,0])      
            
    #在图中显示
    plt.figure()
    plt.imshow(img_temp)
    
    #是否显示坐标轴
    if axis:
        
        plt.axis('off')
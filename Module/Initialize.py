# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 19:16:08 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Init
"""

import copy as cp
import numpy as np
import matplotlib.pyplot as plt

from Module import Image as Im
from Module import Dictionary as Dict

#============================================================================== 
#输入路径path，读取图片，生成图片的rgb和灰度矩阵函数
#参数show表示图片预览参数：默认为None，rgb表示开启rgb预览，gray表示灰度预览
def LoadImage(load_path,
              show=True,
              axis=True):
    
    img_rgb=plt.imread(load_path) 
    
    #显示rgb图像
    if show: 
        
        plt.figure()
        plt.imshow(img_rgb) 
        
        #显示坐标轴吗
        if not axis:
            
            plt.axis('off')
        
    return img_rgb

#============================================================================== 
#增加画布，改变输入图像的尺寸：增加m行n列
def AddPadding(img_rgb,
               rgb_dict,
               show=False,
               axis=False,
               fault_exist=False):
    
    #新的img_rgb
    temp_img_rgb=cp.deepcopy(img_rgb)
    
    #默认为长宽的20%
    m_row,n_column=int(np.shape(img_rgb)[0]/3),int(np.shape(img_rgb)[1]/3)
    
#    print(m_row,n_column)
    
    #改变图像的尺寸
    new_img_rgb_shape=(np.shape(temp_img_rgb)[0]+m_row,
                       np.shape(temp_img_rgb)[1]+n_column,
                       np.shape(temp_img_rgb)[2])
    
    #这种定义背景方式最奏效
    #背景色
    background_rgb=np.array([255,255,255],dtype=np.uint8)
    
    #new_img_rgb视为底图
    new_img_rgb=np.full(new_img_rgb_shape,background_rgb)  
    
    mm,nn=int(np.floor(m_row/2)),int(np.floor(n_column/2))
    
    #着色
    new_img_rgb[mm:mm+np.shape(img_rgb)[0],nn:nn+np.shape(img_rgb)[1]]=img_rgb[:,:]
    
    #生成img_tag矩阵
    img_tag=Im.RGB2Tag(new_img_rgb,rgb_dict)
    
    #把边界边视为fault
    #一列一列地遍历
    if fault_exist:
           
        #左侧
        for j in range(np.shape(img_tag)[1]):
            
            if list(img_tag[:,j])!=[0]*np.shape(img_tag)[0]:
                
                #厚度为3
                img_tag[mm:-mm,j-1]=-1
                img_tag[mm:-mm,j-2]=-1
                img_tag[mm:-mm,j-3]=-1
      
                break
            
        #右侧
        for j in range(np.shape(img_tag)[1]):
            
            if list(img_tag[:,-j])!=[0]*np.shape(img_tag)[0]:
                
                #厚度为3
                img_tag[mm:-mm,1-j]=-1
                img_tag[mm:-mm,2-j]=-1
                img_tag[mm:-mm,3-j]=-1
                
                break 
 
    #显示rgb图像
    if show: 
        
        plt.figure()
        plt.imshow(Im.Tag2RGB(img_tag,rgb_dict)) 
        
        #显示坐标轴吗
        if not axis:
            
            plt.axis('off')
            
        plt.axis('scaled')
        
    #输出新的img_tag
    return img_tag,Im.Tag2RGB(img_tag,rgb_dict)

#============================================================================== 
#生成字典的初始化函数
#base_adjust表示是否需要用特殊符号来表示base的rgb值
#fault_exit表示输入图像当中是否存在断层对象
def InitDict(img_rgb,
             base_adjust=False,
             fault_exist=False):
    
    #临时变量
    rgb_list_temp=[]
    
    for i in range(np.shape(img_rgb)[0]):
        
        for j in range(np.shape(img_rgb)[1]):
            
            if list(img_rgb[i,j].astype(int)) not in rgb_list_temp:
                
                rgb_list_temp.append(list(img_rgb[i,j].astype(int)))
    
    #判断背景色
    if [255,255,255] in rgb_list_temp:
   
        rgb_list_temp.remove([255,255,255])   
        
    #只有layer的rgb
    layer_rgb_list=cp.deepcopy(rgb_list_temp)
    
#    print(layer_rgb_list)
    
    #fault
    #有断层的情况哦
    if fault_exist:
        
        #各种颜色像素点数量的字典
        rgb_number_dict={}
        
        for k in range(len(rgb_list_temp)):
            
            rgb_number_dict[k]=np.sum(img_rgb==rgb_list_temp[k])
            
        #比较像素点数量的多少    
        key=list(rgb_number_dict.keys())
        value=list(rgb_number_dict.values())
        
        #得到断层的rgb值
        fault_rgb=rgb_list_temp[key[value.index(min(value))]]
    
#        print(fault_rgb)
                
        #删除fault的rgb
        layer_rgb_list.remove(fault_rgb)
        
#        print(layer_rgb_list)
        
        #生成rgb_dict,包括layer和fault
        rgb_dict={}
        
        for i in range(len(layer_rgb_list)):
            
            rgb_dict[i+1]=layer_rgb_list[i]
                    
#    print(layer_rgb_list)
    
    #但是列表不可以作为索引，因此先转化为临时tag列表
    tag_list=[index+1 for index in range(len(layer_rgb_list))]
    
    #临时的tag_color索引
    rgb_dict_temp=dict(zip(tag_list,layer_rgb_list))
    
#    print(rgb_dict_temp)
    
    #比较他们的深度度
    depth_list=[]
    
    for this_rgb in list(rgb_dict_temp.values()):
          
#        print(np.mean(list(np.where(img_rgb==list(this_rgb))[0])))

        depth_list.append(np.mean(list(np.where(img_rgb==list(this_rgb))[0])))
        
#    建立颜色何深度的索引
    map_tag_depth_temp=dict(zip(tag_list,depth_list))
    
#    print(map_tag_depth_temp)
    
    #对depth进行排序
    depth_list.sort()
    
#    print(depth_list)
    
    #老的tag要修改
    tag_list_temp=[]
    
    #索引每一个深度值
    for this_depth in depth_list:
        
        tag_list_temp.append(Dict.DictKeyOfValue(map_tag_depth_temp,this_depth))
        
#    print(depth_list)
#    print(tag_list_temp)
    
    #再按照它找rgb
    rgb_list=[]
    
    for this_tag in tag_list_temp:
        
        rgb_list.append(rgb_dict_temp[this_tag])
        
    #最终结果
    rgb_dict=dict(zip(tag_list,rgb_list))
    
    if fault_exist:
        
        #索引-1代表断层fault
        rgb_dict[-1]=fault_rgb
    
    #重新排序
    rgb_dict=Dict.DictSortByIndex(rgb_dict,sorted(list(rgb_dict.keys())))
    
    #base
    #调整基底哦babe
    if base_adjust:
        
        base_tag=list(rgb_dict.keys())[-1]
        
#        print(base_tag)
        
        base_rgb=rgb_dict[base_tag]
        
        #删除并重命名
        del rgb_dict[base_tag]
        
        #base_tag的索引定义为-2
        rgb_dict[-2]=base_rgb
    
    #blank
    if np.array([255,255,255]) in img_rgb:
        
        #0代表背景色
        rgb_dict[0]=[255,255,255]
    
    #排序
    rgb_dict=Dict.DictSortByIndex(rgb_dict,sorted(list(rgb_dict.keys())))
    
#    print(rgb_dict)
    
    return rgb_dict

#==============================================================================     
#初始化fault倾角函数
def InitTilt(which_fault):
    
    #fault边缘点坐标
    I=[pos[0] for pos in which_fault.edge]
    J=[pos[1] for pos in which_fault.edge]
    
    #用J检索I
    I_J=dict(zip(I,J))
    
    #边缘集合中两侧存在layer_tag的最高点和最低点
    #由于纵坐标I是自上而下增长的，为描述方便，将其取相反数
    pos_top=np.array([-min(I),I_J[min(I)]])
    pos_bottom=np.array([-max(I),I_J[max(I)]])
    
#    print(pos_bottom)
#    print(pos_top)
    
    #斜率
    k=(pos_top-pos_bottom)[0]/(pos_top-pos_bottom)[1]
    
    #倾角
    tilt=180*np.arctan(abs(k))/np.pi
  
    return tilt,k
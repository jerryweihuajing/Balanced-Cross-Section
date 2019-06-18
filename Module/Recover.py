# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 22:37:43 2019

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：Module-Recover
"""
import copy as cp
import numpy as np
import matplotlib.pyplot as plt

import sys,os

if os.getcwd() not in sys.path:
    
    sys.path.append(os.getcwd())
    
from Module import Pick
from Module import Image as Img
from Module import Display as Dis
from Module import Initialize as Init
from Module import Length as Len

#==============================================================================    
#revocer all layers
#load_path: path where image was loaded
#save_path: path where image was saved 
def SeriesRecover(load_path,save_path):
    
    #导入图片，生成rgb矩阵
    img_rgb=Init.LoadImage(load_path,show=False)
    
    #生rgb相关的列表和字典
    #rgb_dict=Init.InitDict(img_rgb)
    rgb_dict=Init.InitDict(img_rgb,base_adjust=True,fault_exist=True)
    
    #改变图片尺寸增加padding
    img_tag,img_rgb=Init.AddPadding(img_rgb,rgb_dict,show=True)
    
    #初始化fractions，并显示
    total_fractions=Pick.PickFractions(img_rgb,img_tag,rgb_dict) 
    
    #所有layer对象
    total_layers=Pick.DeleteFault(total_fractions)
    
    #恢复结果
    final_layers=[]
    
    #temporary image
    temp_img_rgb=cp.deepcopy(img_rgb)
    
    for k in range(len(total_layers)):
        
        #fig name
        this_fig_name=str(k+1)+'.png'
        
        if k==0:
            
            final_layers.append(Len.LengthRecover(total_fractions,img_tag,img_rgb,rgb_dict))
        
        if k>0:
            
            final_layers.append(Len.LengthRecover(total_fractions,img_tag,Img.BoundaryImg(final_layers[-1],img_rgb),rgb_dict))
        
        #new blank canvas    
        temp_img_rgb[:,:]=np.array([255,255,255],dtype=np.uint8)
        
        #figure: for saving
        this_fig=plt.figure()
        Dis.ShowFractions(final_layers,temp_img_rgb,rgb_dict)
    
        #save this fig
        this_fig.savefig(save_path+'\\'+this_fig_name,dpi=300)
        
        plt.close()
    
    return final_layers
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 14:46:58 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库
"""

import copy
import numpy as np
import matplotlib.pyplot as plt
import offset_object as o

#============================================================================== 
#输入路径path，读取图片，生成图片的rgb和灰度矩阵函数
#参数show表示图片预览参数：默认为None，rgb表示开启rgb预览，gray表示灰度预览
def LoadImage(load_path,show=False):
    
    img_rgb=plt.imread(load_path) 
    
    #显示rgb图像
    if show: 

        plt.figure()
        plt.imshow(img_rgb) 
#        plt.axis('off')
        
    return img_rgb

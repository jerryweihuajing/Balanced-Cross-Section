# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 14:37:48 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于面积守恒的平衡恢复脚本

@需要输入的参数：
1 图片名
2 剖面长度
"""

import area_module as whj
import numpy as np
import matplotlib.pyplot as plt

#加载路径
load_path=r'C:\Users\whj\Desktop\Spyder\平衡恢复\例\1.bmp'
#load_path=r'C:\Users\whj\Desktop\Spyder\平衡恢复\例\2.bmp'

#load_path=r'C:\Users\whj\Desktop\软件著作权\面积守恒平衡剖面软件\area_model_complex.bmp'
#load_path=r'C:\Users\whj\Desktop\软件著作权\面积守恒平衡剖面软件\area_model.bmp'

#读取图片并创建图像矩阵
img_rgb=whj.LoadImage(load_path)

#生rgb相关的列表和字典
rgb_dict=whj.InitDict(img_rgb,base_adjust=True)

#生成img_tag矩阵
img_tag=whj.RGB2Tag(img_rgb,rgb_dict)

#第0期
original_img_tag=whj.Originate(img_tag,rgb_dict)

#各期次恢复
final_img_tag_list,transform_length_list=whj.Recover(original_img_tag,rgb_dict)

#请输入剖面长度（km）
profile_length=84.25

#保存路径
save_path=r'C:\Users\whj\Desktop\计算结果'

#输出结果
whj.PrintResult(profile_length,final_img_tag_list,transform_length_list,save_path)
   
#输出单张处理结果            
whj.PrintSingle(img_rgb,final_img_tag_list,rgb_dict,save_path)

#输出组合图处理结果
whj.PrintSubplot(img_rgb,final_img_tag_list,rgb_dict,save_path)

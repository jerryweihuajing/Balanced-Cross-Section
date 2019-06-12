# -*- coding: utf-8 -*-
"""
Created on Fri May  4 23:08:51 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于断层牵引法的平衡恢复脚本
"""

import module_fault_motion as whj
import object_fault_motion as o

import matplotlib.pyplot as plt  
import numpy as np

#输入图片名
#main('拉张')

#路径
#def main(name):

load_path=r'C:\Users\whj\Desktop\Spyder\平衡恢复\例\\'

name='拉张'
load_path+=name
load_path+='.bmp'

load_path=r'C:\Users\whj\Desktop\Spyder\平衡恢复\例\simple.bmp'

#导入图片，生成rgb数组
img_rgb=whj.LoadImage(load_path,True)

#改变图片尺寸增加padding
img_rgb=whj.AddPadding(img_rgb,m=30,n=150,show=True)

#生rgb相关的列表和字典
rgb_dict=whj.InitDict(img_rgb,True)

#计算初始长度
length_now=whj.CalculateLength(img_rgb,rgb_dict)

#生成img_tag矩阵
img_tag=whj.RGB2Tag(img_rgb,rgb_dict)

plt.figure()
plt.imshow(whj.FitSize(img_tag),cmap='gray')

plt.figure()
plt.imshow(whj.Tag2RGB(whj.FitSize(img_tag),rgb_dict))

#初始化fractions，并显示
total_fractions=whj.Initfractions(img_rgb,img_tag,rgb_dict,show=True)

#%%
#从图像中获取断层
this_fault=whj.FaultFrom(total_fractions,img_rgb,True)

#this_fault.Show(img_rgb,rgb_dict)

#%%

"""如何生成上下盘"""
#生成上下盘  
#plate_up,plate_down=whj.PickUpAndDown(this_fault,total_fractions,img_tag,img_rgb,rgb_dict)

plate_up=whj.PickAndGeneratePlate(total_fractions,img_rgb)

plate_down=whj.PickAndGeneratePlate(total_fractions,img_rgb)

#%%
plate_up.Show(img_rgb,rgb_dict)

plate_down.Show(img_rgb,rgb_dict)

#将layer切割成chip
CHIP_1=plate_up.ToChip(this_fault,img_tag,20,'A')
CHIP_2=plate_down.ToChip(this_fault,img_tag,20,'B')

whj.ShowChips([CHIP_1,CHIP_2],img_rgb,rgb_dict,grid='on')

CHIP_1.Show(img_rgb,rgb_dict,grid='on')
CHIP_2.Show(img_rgb,rgb_dict,grid='on')

#拉到一块
CHIP_1,CHIP_2=whj.Cohere([CHIP_2,CHIP_1])

Chips=[CHIP_1,CHIP_2]

#10.29
#==============================================================================  
#将多个Chips对象合并的函数？
#建立一个更大的平行四边形框框
def MergeChips(Chips,new_id):
    
    #建立新的Chip对象
    that_Chip=o.Chip()

    #重新定Chip的所有属性
    that_Chip.id=new_id
    
    #把列表里的玩意都拉进来呗
    for this_Chip in Chips:
        
        
        that_Chip.total_chips+=this_Chip.total_chips  
         
        that_Chip.content+=this_Chip.content

        
#    self.plate=plate
#    self.node_quadrangle=node_quadrangle
#    self.top=top
#    self.others=others
#    self.fault=fault
#    self.fault_content=fault_content
#    self.tilt=tilt
#    self.k=k
#    self.regularization=regularization


#Plate2Chip(which_plate,which_fault,img_tag,width,Chip_id)

    
#
#whj.ShowChips([CHIP_1,CHIP_2],img_rgb,rgb_dict)
#
#
#CHIP_1,CHIP_2=whj.ChipsRegularization(CHIP_1,CHIP_2,img_rgb,rgb_dict)
#
#whj.ShowChips([CHIP_1,CHIP_2],img_rgb,rgb_dict,grid='on')
#
#img_rgb=whj.Tag2RGB(whj.TopBaseFault([CHIP_1,CHIP_2],img_tag,rgb_dict,0,-30),rgb_dict,True)
#
#"""以上都ok"""
#
###计算长度
#length_before=whj.CalculateLength(img_rgb,rgb_dict)
#
#save_path=r'C:\Users\whj\Desktop\1'
#
##save_path+=name
#
#whj.PrintResult(save_path,1.8,length_before,length_now)
# 
#new_img_tag=whj.FitSize(whj.RGB2Tag(img_rgb,rgb_dict))
#
#new_img_rgb=whj.Tag2RGB(new_img_tag,rgb_dict)
#
#plt.figure()
#
#plt.imshow(new_img_rgb)
    
    
##输入图片名
#main('拉张')


#层长守恒


# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 14:36:30 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于面积守恒的平衡恢复脚本

@需要输入的参数：
1 图片名
2 剖面长度
"""

import numpy as np
from matplotlib.font_manager import FontProperties
import module_area_depth as whj

#动态修改字体，需要在可视化参数中添加fontproperties=font
font=FontProperties(fname=r"C:\Windows\Fonts\Simsun.ttc",size=12)

"""No表示第No条剖面"""
#No=2

"""控制台中输入文件名,加r表示绝对路径"""
#加载路径
load_path=r'C:\Users\whj\Desktop\Spyder\平衡恢复\例\1.bmp'

#读取图片并创建图像矩阵
img_rgb=whj.LoadImage(load_path)

#"""在必要时增加行"""
#
#"""第三层拾取不了"""
#

#顶面184:None BB:10
img_rgb=whj.AddTop(img_rgb,10)

#底面:184:300  BB:200
img_rgb=whj.AddBottom(img_rgb,10)

#plt.imshow(img_rgb) 

"""请输入获取地层rgb的well"""
#建立颜色标签
#创建rgb和tag列表和灰度和rgb的映射字典
rgb_list,tag_list,color_dict=whj.GenerateListAndDict(img_rgb,well=10)

"""
请输入剖面长度（km）
BB：84.25
184：62.15
"""

#请输入剖面长度（km）
profile_length=84.25

img_tag=whj.GenerateImgTag(img_rgb,color_dict)
  
#计算各层的像素点数量
layer=whj.InitLayer(tag_list,img_tag)

#原图的宽度和高度
(height,width)=np.shape(img_tag)

#创建各层最大高度值的列表        
Height=whj.InitHeight(layer,height,width)   

#计算缩短量，缩短后的长度，每一期缩短率，各阶段缩短率之和
shorten,shorten_length,shorten_sum,shorten_rate_sum,shorten_rate,rate=whj.Calculate(layer,Height,width)

#expo:1生成组合图 0生成多张单图
expo=1

#基底的tag
tag_base=tag_list[-1] 

#生成推像素点之后的rgb矩阵
push_rgb,rgb_push_for_single=whj.GeneratePushResult(layer,Height,width,shorten_length,tag_list,expo,tag_base,color_dict,img_rgb)

#保存路径
save_path=r'C:\Users\whj\Desktop\1'

#生成组合图
whj.ShowSubplot(img_rgb,font,push_rgb,shorten_length,shorten_rate,1000,expo,save_path,4,title='OFF')

#生成单独图片,参数d表示分辨率,No表示剖面序号，保存路径
"""若计算效率太低，可将rgb_push_for_single替换为push_rgb"""

whj.ShowSingle(img_rgb,rgb_push_for_single,1000,expo,save_path)

#打印计算结果
whj.PrintResult(profile_length,shorten,shorten_length,shorten_sum,shorten_rate_sum,save_path)

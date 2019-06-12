# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 16:11:47 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于面积深度法的平衡恢复软件
@目标：
1 自动读取颜色rgb和灰度（由浅到深） OK
2 读取输入图片的方式改为由路径读取
3 深度由min()函数来确定 OK
4 unit即比例尺由输入导入
5 导出bmp图片的函数，导出缩短量和缩短率计算结果（文本格式）
6 测试随机模型 
7* 所有输入界面化,所有输出美观化
8* 尝试加入断层的解释（深度学习与神经网络方法）

"""

#需要修改的参数：
#1 图片名
#2 比例尺

from skimage import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

#动态修改字体，需要在可视化参数中添加fontproperties=font
font=FontProperties(fname=r"C:\Windows\Fonts\Simsun.ttc",size=14)

#rgb转灰度的函数
def rgb2gray(rgb):
    gray=np.zeros(np.shape(rgb)[0:2])
    for i in range(np.shape(rgb)[0]):
        for j in range(np.shape(rgb)[1]):
            gray[i,j]=np.dot(rgb[i,j],[0.299,0.587,0.113])
    return gray.astype(int)

#显示rgb图像
"""需将bmp和脚本放在同一个文件夹当中，今后可转化为读路径的形式"""
img_rgb=io.imread('07e31086-魏华敬（东）.bmp') 
#plt.imshow(img_rgb)

#显示灰度图像
img_gray=rgb2gray(img_rgb) #将rgb值矩阵转化为灰度值矩阵
#plt.imshow(img_gray,cmap='gray')

rgb_list=[] #rgb数组
gray_list=[] #灰度数组
for j in range(np.shape(img_gray)[1]):
    for i in range(np.shape(img_gray)[0]):
        if img_gray[i,j] not in gray_list:
            rgb_list.append(img_rgb[i,j])
            gray_list.append(img_gray[i,j])
            
color_dict={} #建立灰度和rgb的映射字典
for i in range(len(rgb_list)):
    color_dict[gray_list[i]]=rgb_list[i]
    
first_layer,second_layer,third_layer=[],[],[] #三层分别的像素点数量
blank=[] #空白点集合列表
gray_base=img_gray[-1,-1] #基底的灰度值（自行寻找出）,这里假设左下角一定是基底
gray_list.remove(gray_base) #删除基底的灰度值
gray_list.sort(reverse=True) #灰度值从大到小排列
for j in range(np.shape(img_gray)[1]):
    blank.append(np.sum(img_gray[:,j]==gray_list[0]))
    first_layer.append(np.sum(img_gray[:,j]==gray_list[1]))
    second_layer.append(np.sum(img_gray[:,j]==gray_list[2]))
    third_layer.append(np.sum(img_gray[:,j]==gray_list[3]))

#计算空白的面积
area_blank=0
for item in blank:
    area_blank+=item
    
#计算拉平后图的宽和高
width=np.shape(img_gray)[1]
"""深度的确定方式：基底层最高点到莫霍面的距离，用min()函数来算)"""
#height=int(np.ceil(np.shape(img_gray)[0]-area_blank/width))
height=np.shape(img_gray)[0]
         
#用总列表来表示各层像素点的多少 
layer=[]
layer.append(blank)
layer.append(first_layer)
layer.append(second_layer)
layer.append(third_layer)

#计算缩短量，单位为像素点
shorten=[] #缩短量
for i in range(len(layer)):
    length=0
    for item in layer[i]:
        length+=item
    shorten.append(length/height)

shorten_length=[] #每一期缩短之后的长度
shorten_length.append(np.shape(img_gray)[1])
for i in range(1,len(layer)):
    shorten_length.append(shorten_length[i-1]-shorten[i])

shorten_rate=[] #每一期缩短率
for i in range(len(layer)):
    shorten_rate.append(shorten[i]/shorten_length[3])

shorten_sum=0 #总缩短量
shorten_rate_sum=0 #总缩短率
for i in range(1,len(layer)):
    shorten_sum+=shorten[i]
    shorten_rate_sum+=shorten_rate[i]   
    
rate=[] #总缩短率
rate.append(shorten_rate[1])
rate.append(shorten_rate[1]+shorten_rate[2])
rate.append(shorten_rate[1]+shorten_rate[2]+shorten_rate[3])

#为了计算方便新创建一个缩短率列表，把初期的状态也能用循环表示（作者强迫症）
new_rate=[0] 
for item in rate:
    new_rate.append(item)
    
push_gray,push_rgb=[],[] #灰度值结果和rgb结果
#灰度版本
#拉平之后的状态数组
draw=np.full((height,width),gray_base)
for j in range(np.shape(img_gray)[1]):
    for i in range(layer[1][j]):
        draw[i,j]=gray_list[1]
    for i in range(layer[1][j],layer[1][j]+layer[2][j]):
        draw[i,j]=gray_list[2]
    for i in range(layer[1][j]+layer[2][j],layer[1][j]+layer[2][j]+layer[3][j]):
        draw[i,j]=gray_list[3]
push_gray.append(draw)


#第一次缩短
draw=np.full((height,width),gray_base)
for j in range(np.shape(img_gray)[1]):
    for i in range(layer[2][j]):
        draw[i,j]=gray_list[2]
    for i in range(layer[2][j],layer[2][j]+layer[3][j]):
        draw[i,j]=gray_list[3]
push_gray.append(draw)

#第二次缩短
draw=np.full((height,width),gray_base)
for j in range(np.shape(img_gray)[1]):
    for i in range(layer[3][j]):
        draw[i,j]=gray_list[3]
push_gray.append(draw)

#第三次缩短
draw=np.full((height,width),gray_base)
push_gray.append(draw)
    
#rgb版本
#初始和一二三期
for k in range(len(layer)):
    #rgb数组是三维的,先填充基底
    #考虑了将矩阵行数扩大，为了subplot图好看
    draw=np.full((int(np.floor(height/(1-new_rate[k]))),width,3),color_dict[gray_base]) 
    for i in range(height):
        for j in range(width):
            draw[i,j]=color_dict[push_gray[k][i,j]]
    push_rgb.append(draw.astype(img_rgb.dtype)) #将映射后的矩阵转化为和原图相同的格式
    
##绘图
##灰度版本
#fig_gray=plt.figure() 
##原图
#ax=fig_gray.add_axes([0.15,0.6,0.7,0.5])
#ax.imshow(img_gray,cmap='gray')
##拉平初始状态
#ax=fig_gray.add_axes([0.15,0.45,0.7,0.5])
#ax.imshow(push_gray[0],cmap='gray')
##第一期
#ax=fig_gray.add_axes([0.15,0.3,0.7*(1-rate[0]),0.5])
#ax.imshow(push_gray[1],cmap='gray')
##第二期
#ax=fig_gray.add_axes([0.15,0.15,0.7*(1-rate[1]),0.5])
#ax.imshow(push_gray[2],cmap='gray')
##第三期
#ax=fig_gray.add_axes([0.15,0,0.7*(1-rate[2]),0.5])
#ax.imshow(push_gray[3],cmap='gray_r')

#rgb版本
fig_rgb=plt.figure() 

#原图
ax=fig_rgb.add_axes([0.15,0.6,0.7,0.4])
ax.imshow(img_rgb)
#去掉坐标刻度
ax.set_xticks([])
ax.set_yticks([])
plt.title('基于面积深度法的平衡恢复',fontproperties=font)    
#拉平初始状态+第一期+第二期+第三期
for k in range(len(new_rate)):
    #axes = figure.add_axes([left,bottom,width,height])
    ax=fig_rgb.add_axes([0.15,0.45-k*0.15,0.7*(1-new_rate[k]),0.4])
    ax.imshow(push_rgb[k])
    ax.set_xticks([])
    ax.set_yticks([])
    
"""1km代表unit个像素点（需根据实际比例尺修改）"""
unit=13.55   

#输出重要参数
print('初始长度：%5.2fkm'%(shorten_length[0]/unit))
for i in range(1,len(layer)):
    print('第%d期长度：%5.2fkm,拉张量：%5.2fkm'%(i,shorten_length[i]/unit,shorten[i]/unit))
print('总拉张量：%5.2fkm,拉张率：%4.2f%%'%(shorten_sum/unit,shorten_rate_sum*100))


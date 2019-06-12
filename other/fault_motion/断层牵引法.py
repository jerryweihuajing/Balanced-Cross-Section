# -*- coding: utf-8 -*-
"""
Spyder编辑器

这是一个临时脚本文件
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import weihuajing as whj

class fault():
    def __init__(self,matrix,inclination):
        self.matrix=matrix
        
        
def pick_fault_color():
    fault_color=gray_list[-1]
    return fault_color

def fault_recognition(img_gray,fault_color):
    matrix=[m,n] #这是一个只有断层灰度的矩阵
    return matrix

def pick_iso_fault(matrix,fault_color):
#    1 小于45°
    for i in range(len(img_gray)):
        for j in range(len(img_gray[0])):
            #建立某个数组用于表征断层的像素点坐标
            iso_fault=[] 
            #与上一个点的横或纵坐标的差值不大于1（表示连续）
            if matrix[i,j]==fault_color and iso_fault.append((i,j)):         

def lift_1(img_gray,fault_color):
    for i in range(len(img_gray)):
        for j in range(len(img_gray[0])):
            if img_gray[i,j]==fault_color:
                continue
                 
#读取图片并创建图像矩阵
#控制台中输入文件名
path='fault.bmp'
img_rgb,img_gray=whj.load_create_show(path)

#创建rgb和灰度列表和灰度和rgb的映射字典
rgb_list,gray_list,color_dict=whj.create_list_dict(img_rgb,img_gray)

#获取整张图中所有的gray值
gray_list_full=[]
for i in range(len(img_gray)):
    for j in range(len(img_gray[0])):
        if img_gray[i,j] not in gray_list_full:
            gray_list_full.append(img_gray[i,j])

#计算gray_list_full和gray_list的差集
gray_fault=gray_list_full #断层的gray集合
for i in range(len(gray_list)):
    if gray_list[i] in gray_list_full:
         gray_fault.remove(gray_list[i])
       
gray_fault.remove(254) #删除边界的白色
gray_fault=gray_fault[0] #将数组转化为元素
del gray_list_full #删除这个没有用的变量

'''这一步有点多余'''
#建立一个表示断层位置的矩阵
fault_matrix=np.zeros(np.shape(img_gray))
for i in range(len(fault_matrix)):
    for j in range(len(fault_matrix[0])):
        if img_gray[i,j]==gray_fault:
            fault_matrix[i,j]=1 #存在断层的位置用1来表示
            
#建立两个列表来表示断层两侧的像素点的灰度
#确定左（右）边有点
#且该点[i,j]和左（右）边的点的值不同，即断层和底层的像素点灰度值不同
#记录下该点的坐标（i,j）
fault_left,fault_right=[],[]
for i in range(len(fault_matrix)):
    for j in range(len(fault_matrix[0])):
        if j>0 and j<len(fault_matrix[0])-1:
            if fault_matrix[i,j-1]!=1 and fault_matrix[i,j]==1:
                fault_left.append((i,j))
            if fault_matrix[i,j+1]!=1 and fault_matrix[i,j]==1:
                fault_right.append((i,j))
        
#已知目标层L2的灰度值为
gray_layer_2=92
#在fault_left和fault_right中查找角点，这里需要知道断层是正断层或逆断层

        
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 19:30:11 2019

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于层长守恒的平衡恢复函数库-Corner
"""

import numpy as np
import matplotlib.pyplot as plt

from Module import Pick
from Module import Angle as Ang
from Module import Display as Dis
from Module import Geometry as Geom
from Module import Dictionary as Dict


#============================================================================== 
#高斯卷积核函数
def GaussianKernel(miu,sigma,window_size):
    
    #高斯自变量步长
    interval=1
    
    #判断一维
    if type(window_size) is int:
        
        if window_size%2!=1:
            
            print('ERROR:redefine the window_size')
            
        else:
            
            #定义空的卷积核
            kernel=[]
            
            #臂展
            length=window_size//2
            
            for k in range(window_size):
                
                x=k-length
                
                kernel.append(np.exp(-((x*interval)**2)/2*sigma**2)/(2*np.pi*sigma**2))
            
            return kernel
        
    #判断二维
    if type(window_size) is tuple:
        
        #判断window_size是否为奇数
        if window_size[0]%2!=1 and window_size[1]%2!=1:
            
            print('ERROR:redefine the window_size')
        
        else:
            
            #定义空的卷积核
            kernel=np.zeros((window_size[0],window_size[0]))
            
            #臂展
            length_i=window_size[0]//2
            length_j=window_size[1]//2
            
            y_list=[y for y in range(-length_i,length_i+1)]
            x_list=[x for x in range(-length_j,length_j+1)]

            #给卷积核赋值
            for x in x_list:
                
                j=x+length_j
                
                for y in y_list:
    
                    i=y+length_i
                    
                    kernel[i,j]=np.exp(-((x*interval)**2+(y*interval)**2)/2*sigma**2)/(2*np.pi*sigma**2)
                    
            return kernel
    
#============================================================================== 
#position表示窗口中心的位置，也许有多个点
#[u,v]表示移动的距离
#img_tag表示标签矩阵（灰度）
#window_size表示窗口的大小
def Energy(position,u,v,img_tag,window_size):
    
    #判断window_size是否为奇数
    if window_size%2!=1:
        
        print('ERROR:redefine the window_size')
    
    else:
        
        #窗口内的能量和
        total_energy=0
        
        #核函数，权重
        kernel=GaussianKernel(0,1,(window_size,window_size))
        
        #臂展
        length=window_size//2
        
        x_list=[x for x in range(-length,length+1)]
        y_list=[y for y in range(-length,length+1)]
        
        #迭代计算
        for x in x_list:
            
            for y in y_list:
                
                this_pos=[int(position[0]+y),int(position[1]+x)]
        
                that_energy=(img_tag[int(this_pos[0]+u),int(this_pos[1]+v)]\
                            -img_tag[int(this_pos[0]),int(this_pos[1])])**2
           
                total_energy+=that_energy*kernel[x,y]
             
    return total_energy 

#============================================================================== 
#各个方向移动能量的平均值
def AverageEnergy(which_edge,window_size,img_tag,show=False):
    
    #判断window_size是否为奇数
    if window_size%2!=1:
        
        print('ERROR:redefine the window_size')
    
    else:
        
        #臂展
        length=window_size//2
        
        increasement=[[u,v] for u in range(-length,length+1) for v in range(-length,length+1)]
        
        total_E_u_v=[]
        
        #对每一个点做平移变换咯咯咯
        for this_pos in which_edge:
            
            E_u_v=[]
            
            for this_increasement in increasement:
                
                u,v=this_increasement
                
                E_u_v.append(Energy(this_pos,u,v,img_tag,window_size))
            
            #计算一下平均值
            total_E_u_v.append(np.mean(E_u_v))
            
        #绘图
        if show:

            plt.figure()
            plt.plot(total_E_u_v)
            
        return total_E_u_v
    
#============================================================================== 
#各个方向移动能量的平均值
def MaximalEnergy(which_edge,window_size,img_tag,show=False):
    
    #判断window_size是否为奇数
    if window_size%2!=1:
        
        print('ERROR:redefine the window_size')
    
    else:
        
        #臂展
        length=window_size//2
        
        increasement=[[u,v] for u in range(-length,length+1) for v in range(-length,length+1)]
        
        total_E_u_v=[]
        
        #对每一个点做平移变换咯咯咯
        for this_pos in which_edge:
            
            E_u_v=[]
            
            for this_increasement in increasement:
                
                u,v=this_increasement
                
                E_u_v.append(Energy(this_pos,u,v,img_tag,window_size))
            
            #计算一下平均值
            total_E_u_v.append(np.max(E_u_v))
            
        #绘图
        if show:

            plt.figure()
            plt.plot(total_E_u_v)
            
        return total_E_u_v
    
#==============================================================================
#设计一个求一维数组梯度的函数
def CommonGradient(which_content,show=False):
    
#    which_content=Dict.SortFromStart(which_content,50)[0]
    
    #自己定义一个梯度核函数
    kernel_gradient=[-0.25,-0.5,0,0.5,0.25]  
    
    #定义gauss核函数作为平滑
#    kernel_smooth=[1,1,1,1,1]
    kernel_smooth=GaussianKernel(0,1,5)
    
    #判断kernel的臂展是否为奇数
    if len(kernel_gradient)%2!=1 and len(kernel_smooth)%2!=1:
        
        print('ERROR:redefine the window_size')
    
    else:
        
        #臂展
        kernel_length=len(kernel_gradient)//2
        
        #梯度计算的结果
        gradients=[]
    
        #先来个雏形怎么样咯
        for index in range(kernel_length,len(which_content)-kernel_length):
            
            #初始化它
            that_gradient=0
            
            #这个核内部的数值有哪些
            this_points=[which_content[index+ix] for ix in range(-kernel_length,kernel_length+1)]
            
            #对应相乘
            if len(this_points)==len(kernel_gradient)==len(kernel_smooth):
                
                for k in range(len(this_points)):
                
                    that_gradient+=this_points[k]*kernel_gradient[k]*kernel_smooth[k]
                    
            gradients.append(abs(that_gradient))
               
        #绘图
        if show:

            plt.figure()
            plt.subplot(211),plt.plot(which_content)  
            plt.subplot(212),plt.plot(gradients)   
            
        return gradients

'''增长之后取一部分做计算'''
#==============================================================================
#滑动求梯度方法
#offset:滑动窗口偏移距需要作为输入的参数
def SlideGradient(which_content,offset,show=False):
    
    #留一点边界消除边界效应
    boundary=10
    
    #自己定义一个梯度核函数
    kernel_gradient=[-0.25,-0.5,0,0.5,0.25]  
    
    #定义gauss核函数作为平滑
    kernel_smooth=GaussianKernel(0,1,5)
    
    #判断kernel的臂展是否为奇数
    if len(kernel_gradient)%2!=1 and len(kernel_smooth)%2!=1:
        
        print('ERROR:redefine the window_size')
    
    else:
        
        #臂展
        kernel_length=len(kernel_gradient)//2
        
        #梯度计算的结果
        gradients=[]
        
        #临时content列表
        temp_content=Dict.SortFromStart(which_content,offset)[0]
        
#        print(len(temp_content))
        
        #总的content列表,plus些许边界
        total_content=which_content[:offset]+temp_content+temp_content[:boundary]
        
#        print(len(total_content))
        
        #直接迭代吧
        for index in range(len(which_content)):
            
#            total_content[offset+k]
    
#            print(index)
#            print(kernel_length)
            
            #初始化它
            that_gradient=0
            
            #这个核内部的数值有哪些
            this_points=[total_content[index+offset+ix] for ix in range(-kernel_length,kernel_length+1)]
            
            #对应相乘
            if len(this_points)==len(kernel_gradient)==len(kernel_smooth):
                
                for k in range(len(this_points)):
                
                    that_gradient+=this_points[k]*kernel_gradient[k]*kernel_smooth[k]
                    
            gradients.append(abs(that_gradient))
        
#        print(len(which_content))
#        print(len(gradients))
        
        #绘图
        if show:

            plt.figure()
            plt.subplot(211),plt.plot(temp_content)  
            plt.subplot(212),plt.plot(gradients)   
            
        return gradients
   
#==============================================================================
#检验滑动窗口梯度算法
def CheckGradient(which_content,offset,img_rgb,show=False):
    
    #建立content索引
    x_old=[k for k in range(len(which_content))]
    
    #偏移后的content索引
    x_new=x_old[-offset:]+x_old[:-offset]
    
    #索引的映射关系
    map_x_old_new=dict(zip(x_old,x_new))
            
    #索引和坐标的关系
    map_x_content=dict(zip(list(map_x_old_new.values()),which_content))
    
    #找峰值是没错的呢 哥哥
    #计算harris角点函数梯度
    SlideGradient(AverageEnergy(which_content,5),offset,True)   
      
    #从gradients中提取可疑点观察观察        
    points=Ang.PickPointsFromPlot(5,map_x_content)
      
    #显示吗
    if show:
        
        plt.figure()
        
        for this_pos in points:
            
            Dis.ShowOnePoint(this_pos,img_rgb)  
            
    return points

#==============================================================================
#曲线提高一定阈值进行观察
#threshold:阈值
def PickPeak(which_content,threshold=True,show=False):
    
    #鼠标点击阈值？
    if type(threshold) is bool:
        
        #拾取阈值？
        plt.figure()
        plt.plot(which_content) 
        
        #点击获取曲线中的点的坐标
        point=plt.ginput(1)[0]
        threshold=point[1]
        
        #关闭图片
        plt.close()
        
    #将要表示的点们
    new_content=[]
    
    #遍历所有点，根据值的大小进行判断
    for item in which_content:
        
        if item>threshold:
            
            new_content.append(item)
        
        else:
            
            new_content.append(0)
            
    #显示吗哥，要看看吗？
    if show:
            
        plt.figure()
        plt.plot(new_content,'red')   
        
    return new_content

'''截阈值的方法，多测试几个样本'''
#==============================================================================
#正式得到角点
#energy_mode决定是由average还是maximal函数来计算能量
def GetCorners(which_content,offset,energy_mode,img_tag,img_rgb,show=False):
   
    #滑动窗口求取梯度诶
    #平均值
    if energy_mode is 'mean':
        
        gradients=SlideGradient(AverageEnergy(which_content,5,img_tag),offset)
    
    #最大值法
    if energy_mode is 'max':
        
        gradients=SlideGradient(MaximalEnergy(which_content,5,img_tag),offset)
    
    #压制非极值点点，使它们为0
    peak_content=PickPeak(gradients,True)
    
    #寻找脉冲极值点的办法   
    temp_peak_index=[]
    
    for k in range(len(peak_content)):
        
        if peak_content[k]!=0:
            
            temp_peak_index.append(k)
            
    #极值窗口
    open_length=10
    
    #在这个自定义区间内的都是极值
    temp_peak_index.sort()
    
    #定义一个字典
    #索引和周边索引的对应关系
    map_index_neighbor={}
    
    #索引和他身边被录用的索引   
    map_index_indexes={}
    
    #开始创造其中元素
    for this_index in temp_peak_index:
        
        #单个的索引
        map_index_neighbor[this_index]=[this_index+k for k in range(-open_length,+open_length)]
        
        #被录用的索引(肯定有自己)
        map_index_indexes[this_index]=[]
    
    #判断每个索引和索隐门邻域的对应关系
    for this_index in temp_peak_index:
        
        for this_neighbor in list(map_index_neighbor.values()):
            
            #判断在哪里
            if this_index in this_neighbor:
                
                map_index_indexes[Dict.DictKeyOfValue(map_index_neighbor,this_neighbor)].append(this_index)
                
    #print(map_index_indexes)
    
    #真假索引了
    temp_indexes=list(map_index_indexes.values())
    
    #真实的indexes集合
    indexes=[]
    
    #唯一识别
    map_sum_indexes={}
    
    #迭代合并同类项
    for this_indexes in temp_indexes:
        
        indexes.append(sorted(list(set(this_indexes))))
        
        #它们的和
        map_sum_indexes[sum(indexes[-1])]=indexes[-1]
        
    #print(indexes)
    #print(map_sum_indexes)
    
    #用于加工的indexes列表
    true_indexes=list(map_sum_indexes.values())
    
    #求取小区间里的最大值噢
    #消除偏移距之前的peak索引
    peak_index=[]
    
    for this_indexes in true_indexes:
        
        #建立小区间内的索引与值的对应关系哦
        map_index_value={}
        
        for this_index in this_indexes:
            
            map_index_value[this_index]=gradients[this_index]
            
        #找到最大值噢
        peak_value=np.max(list(map_index_value.values()))
        
        #获取最大值的索引
        peak_index.append(Dict.DictKeyOfValue(map_index_value,peak_value))
    
    #在gradients曲线上显示计算结果
    plt.figure()
    plt.plot(gradients)
    
    #画出峰值点吧
    for this_index in peak_index:
        
        plt.plot(this_index,gradients[this_index],marker='o',color='red')
    
    plt.axis('tight')
    
    #即将消除偏移距
    map_new_old_index=Dict.SortFromStart(which_content,offset)[1]
    
    #还原到真实的叻
    corner_index=[map_new_old_index[this_index] for this_index in peak_index]
    
    #在图像上还原真实的角点儿
    corner_points=[which_content[this_index] for this_index in corner_index]
    
    #显示吧
    if show:
            
        plt.figure()
                
        for this_pos in corner_points:
            
            Dis.ShowOnePoint(this_pos,img_rgb)
            
    return Dict.DictSortByIndex(dict(zip(corner_index,corner_points)),sorted(corner_index))

#============================================================================== 
#暴力增加Corners，从图中获取
def AddCorners(which_layer,total_fractions,corner_amount,img_rgb,show=False):
    
    #从边界中寻找
    which_content=which_layer.edge
    
    #包围layer的faults
    border_faults=Pick.BorderFaults(which_layer,total_fractions)
    
    #结果的集合
    corner_points=[]
    
    #点击获取图像中的点的坐标
    for temp_point in plt.ginput(corner_amount): 
    
        #转化一下
        point=[int(np.round(temp_point[1])),int(np.round(temp_point[0]))]
        
        #计算距离最短的点作为角点
        map_distances_points=Geom.DistancesMap(point,which_content)
        
        #最短的距离 
        corner_points.append(map_distances_points[min(list(map_distances_points.keys()))])
    
    #索引列表
    corner_index=[which_content.index(corner_point) for corner_point in corner_points]
    
    #根据border_faults把点投上来
    #先找最近的fault
    for this_corner_point in corner_points:
        
        #这个点到两个fault的距离列表
        faults_centers=[this_fault.center for this_fault in border_faults]
        
        #计算距离最短的点作为角点
        #该点到fault们的距离列表
        distances_faults=Geom.Distances(this_corner_point,faults_centers)
        
        #建立映射关系
        map_distances_faults=dict(zip(distances_faults,border_faults))
        
        #距离最小的fault是最邻近的
        fault_near_this_corner_point=map_distances_faults[min(distances_faults)]
        
        #
        this_corner_point
    
    
    
    #显示吧
    if show:
            
        plt.figure()
                
        for this_pos in corner_points:
            
            Dis.ShowOnePoint(this_pos,img_rgb)
            
    return dict(zip(corner_index,corner_points))
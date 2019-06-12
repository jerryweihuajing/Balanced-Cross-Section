"""
Created on Fri Nov 23 21:21:09 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Angle
"""

import copy as cp
import numpy as np
import matplotlib.pyplot as plt

from Module import Algebra as Al
from Module import Display as Dis
from Module import Geometry as Geom
from Module import Dictionary as Dict

#============================================================================== 
#一个集合当中离某点的距离为极值的点
def ExtremeFromContent(which_content,which_point,mode,show=False):

#    print('ExtremeFromContent')
    
    #建立点集到某点的距离集合的映射
    map_distance_content=Geom.DistancesMap(which_content,which_point)
    
    #距离列表
    distances=list(map_distance_content.keys())
    
    #先求极值点
    extreme_distances=Al.GetExtremePoints(distances,mode,show)
    
    #极值点的集合
    extreme_points=[]
    
    #把极值转化为坐标
    for this_extreme_distance in extreme_distances:
        
        extreme_points.append(map_distance_content[this_extreme_distance])
     
#    print(extreme_points)
        
    return extreme_points

#==============================================================================
#一个集合当中离某点的距离为单调增减的尽头的点
def FringeFromContent(which_content,which_point,mode,show=False):
    
#    print('FringeFromContent')
    
    #建立点集到某点的距离集合的映射
    map_distance_content=Geom.DistancesMap(which_content,which_point)
    
    #距离列表
    distances=list(map_distance_content.keys())
    
    #再求边缘边界
    fringe_distances=Al.GetFringePoints(distances,mode,show)
    
    #最值点的集合
    fringe_points=[]
    
    #把极值转化为坐标
    for this_fringe_distance in fringe_distances:
        
        fringe_points.append(map_distance_content[this_fringe_distance])
     
#    print(fringe_points)
        
    return fringe_points

#==============================================================================    
#一个集合当中离某点的距离为可疑点的集合：包括极值点和单调递增的尽头   
def SuspiciousFromContent(which_content,which_point,mode,show=False):
    
#    print('SuspiciousFromContent')
    
    #极值
    extreme_points=ExtremeFromContent(which_content,which_point,mode)
    
    #最值
    fringe_points=FringeFromContent(which_content,which_point,mode)
    
    #显示吗
    if show:
        
        #建立点集到某点的距离集合的映射
        map_distance_content=Geom.DistancesMap(which_content,which_point)
        
        #距离列表
        distances=list(map_distance_content.keys())
        
        #计算并显示可疑点
        Al.GetSuspiciousPoints(distances,mode,show)
        
    #合并这俩集合
    return extreme_points+fringe_points
    
#============================================================================== 
#寻找并显示出一个fraction中有没有还不错的Angle
#并在img_rgb这显示    
def AnglesFromFraction(which_fraction,img_rgb,mode='big',show=False,axis=True):
    
#    print('AnglesFromFraction')
    
    """这个复制很有启发意义！！！"""
    #用于显示的rgb矩阵
    temp_img_rgb=cp.deepcopy(img_rgb)
    
    #定义目标点和点集
    that_content=which_fraction.edge
    that_point=which_fraction.center
    
    #可疑角点集合
    that_points=SuspiciousFromContent(that_content,that_point,mode,show)
    
    #显示吗
    if show:
        
        plt.figure()
        
        #显示fraction的边缘和极值点
        which_fraction.ShowEdge(temp_img_rgb,axis)
        
        #逐个显示角点
        for this_pos in that_points:
            
            Dis.ShowOnePoint(this_pos,temp_img_rgb)
        
        #是否显示坐标轴
        if not axis:
            
            plt.axis('off')
            
"""逻辑变量必须放在变量表的最后"""            
#==============================================================================             
#边缘点的索引
#pick_from_img和pick_from_plot为两个调试性质的参数
def EdgeIndex(which_fraction,
              derivative_format,
              index_plot=False,
              derivative_plot=False,
              pick_from_img=False,
              pick_from_plot=False):
    
    #建立which_fraction.edge坐标索引
    x=[k for k in range(len(which_fraction.edge)-1)]
    content=[which_fraction.edge[k] for k in range(len(which_fraction.edge)-1)]
    
    map_x_content=dict(zip(x,content))
    
    #边界位置索引的序列
    index_A=[]
    index_B=[]
    
    #头尾一致
    for k in range(len(which_fraction.edge)-1):
        
        pos_A=which_fraction.edge[k]
        pos_B=which_fraction.edge[k+1]
        
        #生成邻居索引
        index_A.append(Geom.NeighborIndex(pos_A,pos_B)[0])
        index_B.append(Geom.NeighborIndex(pos_A,pos_B)[1])
        
    #轮转的影子索引列表
    another_index_A,map_original_another_x_A=Dict.SortFromStart(index_A,10)
    another_index_B,map_original_another_x_B=Dict.SortFromStart(index_B,10)
    
#    print(len(index_A))
#    print(len(index_B))
#    
#    print(len(another_index_A))
#    print(len(another_index_B))
  
#    print(map_original_another_x_A)
#    print(map_original_another_x_B)
    
    #梯度模式
    if derivative_format is 'gradient':
        
        #从index中找出梯度较大的点
        gradient_A=np.gradient(index_A)
        gradient_B=np.gradient(index_B)
    
        derivative_A=cp.deepcopy(np.array(gradient_A))
        derivative_B=cp.deepcopy(np.array(gradient_B))
        
        #another
        another_gradient_A=np.gradient(another_index_A)
        another_gradient_B=np.gradient(another_index_B)
    
        another_derivative_A=cp.deepcopy(np.array(another_gradient_A))
        another_derivative_B=cp.deepcopy(np.array(another_gradient_B))
        
    #差分格式
    if derivative_format is 'difference':

        #差分计算法
        difference_A=[index_A[k]-index_A[k+1] for k in range(len(index_A)-1)]
        difference_B=[index_B[k]-index_B[k+1] for k in range(len(index_B)-1)]
        
        derivative_A=cp.deepcopy(np.array(difference_A))
        derivative_B=cp.deepcopy(np.array(difference_B))
        
        #another
        another_difference_A=[another_index_A[k]-another_index_A[k+1] for k in range(len(another_index_A)-1)]
        another_difference_B=[another_index_B[k]-another_index_B[k+1] for k in range(len(another_index_B)-1)]
        
        another_derivative_A=cp.deepcopy(np.array(another_difference_A))
        another_derivative_B=cp.deepcopy(np.array(another_difference_B))
    
    #极值大小阈值
    threshold=4
    
    '''使用轮转换位的方法计算角点，然后取并集'''    
    #潜在可疑点    
    points_x_A=list(np.where(abs(derivative_A)>=threshold)[0])
    points_x_B=list(np.where(abs(derivative_B)>=threshold)[0])
    
    #另一半
    another_points_x_A=list(np.where(abs(another_derivative_A)>=threshold)[0])
    another_points_x_B=list(np.where(abs(another_derivative_B)>=threshold)[0])
       
#    print(points_x_A)
#    print(points_x_B)
    
#    print(another_points_x_A)
#    print(another_points_x_B)
    
    '''有问题！！！'''
    """梯度的计算需要加以改进，多点平滑"""
    
    #消除红利
    for k in range(len(another_points_x_A)):
           
        another_points_x_A[k]=map_original_another_x_A[another_points_x_A[k]]
      
    for k in range(len(another_points_x_B)):
                    
        another_points_x_B[k]=map_original_another_x_B[another_points_x_B[k]]   
        
#    print(another_points_x_A)
#    print(another_points_x_B) 
    
    #可以点列表
    points_x_temp=points_x_A+another_points_x_A\
                 +points_x_B+another_points_x_B
     
    #最后取个并集
    points_x=[]
    
    for item in list(set(points_x_temp)):
        
        if item==len(another_derivative_B) or item==len(another_derivative_A):
            
            points_x.append(0)  
        else:
            points_x.append(item+1)
                   
    print(points_x)

    '''再处理一波'''
    
    #从img上获取点做实验
    if pick_from_img:
        
        #返回四个点
        points=PickPointsFromImg(4,which_fraction.edge)
        
        #横坐标哦
        that_x=[content.index(this_point) for this_point in points]   
        
    #显示吗哥
    if index_plot:

        plt.figure()
        
        if pick_from_img:
            
            #纵坐标哦
            index_A_y=[index_A[this_x] for this_x in that_x]
            index_B_y=[index_B[this_x] for this_x in that_x]
            
            #逐个输出可疑点
            for k in range(len(that_x)):

                plt.subplot(211),plt.plot(that_x[k],index_A_y[k],marker='o',color='red')
                plt.subplot(212),plt.plot(that_x[k],index_B_y[k],marker='o',color='red')
       
        #绘制整体曲线
        plt.subplot(211),plt.plot(index_A)
        plt.subplot(212),plt.plot(index_B)
        
        #看看梯度8
        if derivative_plot:
            
            #逐个输出可疑点
            for this_x in points_x:
                
                plt.subplot(211),plt.plot(this_x,index_A[this_x],marker='o',color='red')
                plt.subplot(212),plt.plot(this_x,index_B[this_x],marker='o',color='red')
            
            plt.figure()
            
            #从img上获取点做实验
            if pick_from_img:
                             
                #纵坐标哦
                derivative_A_y=[derivative_A[this_x] for this_x in that_x]
                derivative_B_y=[derivative_B[this_x] for this_x in that_x]
                
                #逐个输出
                for k in range(len(that_x)):
                    
                    plt.subplot(211),plt.plot(that_x[k],derivative_A_y[k],marker='o',color='red')
                    plt.subplot(212),plt.plot(that_x[k],derivative_B_y[k],marker='o',color='red')
           
            #整体曲线
            plt.subplot(211),plt.plot(derivative_A)
            plt.subplot(212),plt.plot(derivative_B)  
            
            #逐个输出可疑点
            for this_x in points_x:
                
                plt.subplot(211),plt.plot(this_x,derivative_A[this_x],marker='o',color='red')
                plt.subplot(212),plt.plot(this_x,derivative_B[this_x],marker='o',color='red')
              
            return [content[this_x] for this_x in points_x]
           
        if pick_from_plot:
            
            return PickPointsFromPlot(4,map_x_content)

'''从图中获取试试'''   
#============================================================================== 
#从曲线中获取数量为amount个
#map_x_content:索引和坐标的关系
def PickPointsFromPlot(amount,map_x_content):
    
    points=[]
    
    for k in range(amount):
              
        #点击获取曲线中的点的坐标
        point=plt.ginput(1)[0]
            
        this_x=int(np.round(point[0]))
        
        that_pos=map_x_content[this_x]
        
        print(list(map_x_content.keys())[this_x],that_pos)
        
        points.append(that_pos)
        
    return points   

#============================================================================== 
#从图像中获取数量为amount个
def PickPointsFromImg(amount,which_content):
    
    points=[]
    
    for k in range(amount):
               
        #点击获取曲线中的点的坐标
        point=plt.ginput(1)[0]
            
        this_point=[int(np.round(point[1])),int(np.round(point[0]))]
        
        #距离最小值
        distances=Geom.Distances(this_point,which_content)

        minimal_distance=min(distances)
        
        #返回该索引及其对应的坐标
        that_point=which_content[distances.index(minimal_distance)]
        
        print(that_point)
        
        points.append(that_point)
        
    return points

'''基本上可以确定是index导数较大的几个点作为角点'''         
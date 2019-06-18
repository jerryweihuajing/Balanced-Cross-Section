# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 14:34:23 2019

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Length
"""

import copy as cp
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import leastsq

from Module import Pick as Pick
from Module import Image as Im
from Module import Corner as Cor
from Module import Geometry as Geom
from Module import Dictionary as Dict

#============================================================================== 
#二次函数的标准形式
def func(params,x):
    
    a,b,c=params
    
    return a*x*x+b*x+c

#============================================================================== 
#误差函数,即拟合曲线所求的值与实际值的差
def error(params,x,y):
    
    return func(params,x)-y

#============================================================================== 
#对参数求解
def slovePara(X,Y):
    
    p0=[10,10,10]

    Para=leastsq(error,p0,args=(X,Y))
    
    return Para

#============================================================================== 
#输出最后的结果
def Fitting(X,Y,show=False):
    
    #二项式系数
    Para=slovePara(X,Y)
    a,b,c=Para[0]
    
    #插出的取值范围
    x=np.linspace(min(X),max(X),max(X)-min(X)) 
    
    #函数式
    y=a*x*x+b*x+c 
    
    #显示吗
    if show:
        
        print("a=",a,"b=",b,"c=",c)
        print("cost:"+str(Para[1]))
        
        print("curve to be solved is:")
        print("y="+str(round(a,2))+"x*x+"+str(round(b,2))+"x+"+str(c))
    
        plt.figure(figsize=(8,6))
        plt.scatter(X,Y,color="green",label="sample data",linewidth=2)
    
        #画拟合直线
        plt.plot(x,y,color="red",label="solution line",linewidth=2)
        
        #绘制图例
        plt.legend() 
        plt.show()
        plt.axis('equal')
    
    return x,y

#============================================================================== 
#基于拟合的点集长度
def FittingContinuousDistance(which_curve_points):
    
    #待拟合的数据
    X=np.array([this_pos[1] for this_pos in which_curve_points])
    Y=np.array([this_pos[0] for this_pos in which_curve_points])
    
    #拟合结果
    J,I=Fitting(X,Y)

    #数量
    if len(J)==len(I):
        
        amount_down=len(J)
    
    #组合成新的content列表
    new_curve_points=[[I[k],J[k]] for k in range(amount_down)]
    
    #计算层长:新/老
    new_curve_length_down=Geom.ContinuousDistance(new_curve_points)
    old_curve_length_down=Geom.ContinuousDistance(which_curve_points)
    
#    print(old_curve_length_down,new_curve_length_down)
    
    #比较长度，拟合之后的长度不能大于原长度的120%,不小于80%
    if 0.8*old_curve_length_down<new_curve_length_down<1.2*old_curve_length_down:
        
        return new_curve_length_down
    else:
        return old_curve_length_down
    
#============================================================================== 
#层长的计算方式：拟合曲线的方法
def FittingCurvedLinesLength(which_layer,img_rgb):
    
    #暴力增加角点
    map_corner_points=Cor.AddCorners(which_layer,4,img_rgb,True)   
    
    #初始化which_layer的角点
    which_layer.corners=list(map_corner_points.values())
                      
    #两条层长上的像素点
    curve_points_up,curve_points_down=Geom.CurvedLinesLength(which_layer.edge,map_corner_points,2,img_rgb)
    
    #下底面
    curve_length_down=FittingContinuousDistance(curve_points_down)
   
    #上顶面
    curve_length_up=FittingContinuousDistance(curve_points_up)
    
    return np.mean([curve_length_down,curve_length_up])

'''老版本'''
#============================================================================== 
#层长恢复核心代码：单个fraciton
def RecoverLength(total_fractions,
                  img_rgb,
                  img_tag,
                  rgb_dict,
                  animation_show=False,
                  show=False):
    
    #拾取出某个目标layer
    which_layer=Pick.PickLayer(total_fractions,img_rgb)
    
    #目标layer的edge
    which_edge=which_layer.edge
    
    '''HarrisM函数有问题'''
    #抓出几个角点
    #map_corner_points=Cor.GetCorners(which_content,100,'mean',img_tag,img_rgb,True)
    
    '''层长恢复'''
    #节省调试时间，直接给出答案
    #暴力增加角点
    map_corner_points=Cor.AddCorners(which_edge,4,img_rgb,True)   
    
    #初始化which_layer的角点
    which_layer.corners=list(map_corner_points.values())
    
    #计算曲线的长度
    layer_length=Geom.CurvedLinesLength(which_edge,map_corner_points,2,img_rgb)
    
    #初始化面积
    which_layer.InitArea()
    
    #层厚度(其实没什么意义)
    layer_thickness=which_layer.area/layer_length
    
    #初始化厚度和长度
    which_layer.thickness=layer_thickness
    which_layer.length=layer_length
    
    #相关联的断层可能多个
    """找出这个layer接壤的fault"""
    '''找到了，处理两侧都有断层的接应点情况'''
    which_faults=Pick.NeighborFault(which_layer,total_fractions)
    
#    print(len(which_faults))
    
    '''一个fault的情况'''
    if len(which_faults)==1:  
        
        #one and only
        which_fault=which_faults[0]
        
        #计算那几个角点哪几个离断层比较近
        corner_points=list(map_corner_points.values())
        
        #计算重心
        fault_center=Geom.CalculateBaryCenter(which_fault.content)
        
        #重心到几个角点的距离
        map_distances_fault2corners=Geom.DistancesMap(fault_center,corner_points)
        
        #距离最小的两个为接应点
        map_attachment_points=Dict.DictSortByIndex(map_distances_fault2corners,sorted(list(map_distances_fault2corners.keys())))
        
        #fraction上的两个接应点
        fraction_attachment_points=list(map_attachment_points.values())[0:2]
        
        #fraction取两个接应点的中点
        fraction_attachment_center=np.round(Geom.CalculateBaryCenter(fraction_attachment_points)).astype(int)
        
        #再去寻找fault上和接应点
        map_distances_attachment2fault=Geom.DistancesMap(fraction_attachment_center,which_fault.edge)
        
        #fault上的接应点
        fault_attachment_point=map_distances_attachment2fault[min(list(map_distances_attachment2fault.keys()))]
        
        #Dis.ShowOnePoint(fault_attachment_point,img_rgb)
        
        '''墙类型的填充函数（模型边界）'''
        #另一端的方向
        directional_offset=which_layer.center[1]-fault_attachment_point[1]
        
        #边界的i坐标
        i_boundary=fault_attachment_point[0]
        
        #左侧
        if directional_offset<0:
            
#            directional_mode='left'
           
            #增长的方向
            step_sign=+1
            
            #边界的j坐标
            j_boundary=fault_attachment_point[1]-layer_length
            
        #右侧
        if directional_offset>0:
            
#            directional_mode='right'   
            
            #增长的方向
            step_sign=-1
            
            #边界的坐标
            j_boundary=fault_attachment_point[1]+layer_length
        
        #边界的坐标
        boundary=np.round([i_boundary,j_boundary]).astype(int)
        
        #断层上接应点的索引
        if fault_attachment_point in which_fault.edge:
            
            fault_attachment_index=which_fault.edge.index(fault_attachment_point)
        
        #计数器
        count=1
        
        #需要描绘的点    
        #第一行
        points_to_draw=[[fault_attachment_point[0],j] for j in range(boundary[1],fault_attachment_point[1],step_sign)]
        
        #用于迭代的总面积
        temp_area=len(points_to_draw)
        
        #循环结束的标志
        flag=(temp_area>=which_layer.area)
        
        #建立一个新的tag矩阵
        img_tag_temp=np.zeros(np.shape(img_tag))
        
        #开始迭代
        while not flag:
            
            #本次迭代需要画出的点
            that_points_to_draw=[]
            
            count+=1
            
            #根据count的奇偶性确定增量的符号
            if count%2==0:
                
                sign=-1
                
            if count%2==1:
                
                sign=1
                
            #单向增量计数器
            index_increment=sign*count//2
        
        #    print(index_increment)
            
            #现在的接应点 
            that_attachment_point=which_fault.edge[fault_attachment_index+index_increment]
            
            #计算这一次迭代面积增量
#            area_increment=np.abs(that_attachment_point[1]-boundary[1])
                       
        #    print(area_increment)  
        #    print(temp_area,which_fraction.area)
            
            Print=False
            
            #图像中填充新增的那一行
            #根据边界与接应点的位置关系进行填充
            if Print:
                
                print('right')
                print(that_attachment_point)
            
    #            img_tag_temp[that_attachment_point[0],boundary[1]:that_attachment_point[1]]=which_fraction.tag    
         
            #将这些点添加至列表
            for j in range(boundary[1],that_attachment_point[1],step_sign):
                
    #            print('plus',j)
                that_points_to_draw.append([that_attachment_point[0],j])
                    
    #        print(img_tag_temp[that_attachment_point[0],boundary[1]:that_attachment_point[1]])
            
            #加进大集合里
            points_to_draw+=that_points_to_draw
            
            if animation_show:
                
                #把它们都绘制出
                for this_point in points_to_draw:
                    
                    img_tag_temp[this_point[0],this_point[1]]=which_layer.tag
                
                #让图片停留几秒钟之后关闭，可以是整数也可以是浮点数
                plt.imshow(Im.Tag2RGB(img_tag_temp,rgb_dict)) 
                plt.pause(1)
                plt.close()
            
            #临时面积
            temp_area=len(points_to_draw)
            
            #更新循环执行的条件
            flag=(temp_area>=which_layer.area)
            
    '''多个fault的情况'''
    if len(which_faults)>1: 
         
        #layer中点
        center=np.array(which_layer.center).astype(int)
    
        #当下接应点
        attachment_point=cp.deepcopy(center)
        
        '''以下内容要进入循环的噢'''
        
        #装所谓坐标的pocket
        pocket=[]
        
        #在layer的edge中找到一个横线确定以前的长度
        for this_pos in which_layer.edge:
            
            if this_pos[0]==attachment_point[0]:
                
                pocket.append(this_pos[1])
#                
#        #pocket中的两个接应点
#        left_attachment_point=[this_pos[0],min(pocket)]
#        right_attachment_point=[this_pos[0],max(pocket)]
#        
#        #将这些点添加至列表
#        for j in range(boundary[1],that_attachment_point[1],step_sign):
#            
##            print('plus',j)
#            that_points_to_draw.append([that_attachment_point[0],j])
#        
#        fitting_interval=FittingInterval(which_layer) 
        
                  
    #把它们都绘制出
    for this_point in points_to_draw:
        
        img_tag_temp[this_point[0],this_point[1]]=which_layer.tag
        
    #显示呗    
    if show:
        
        plt.imshow(Im.Tag2RGB(img_tag_temp,rgb_dict)) 
        
    #改变fraction的content
    which_layer.content=cp.deepcopy(points_to_draw)
    
    #更新which_fraction的一切？
    which_layer.UpdateAll()
    
    return which_layer

#============================================================================== 
#某个两个断层之间的距离列表
def FaultsInterval(which_layer):
        
    #layer中点
    center=np.array(which_layer.center).astype(int)

    #装所谓坐标的pocket
    pocket=[]
    
    #在layer的edge中找到一个横线确定以前的长度
    for this_pos in which_layer.edge:
        
        if this_pos[0]==center[0]:
            
            pocket.append(this_pos[1])
    
#    print(pocket)
     
    return max(pocket)-min(pocket)

'''最新版本'''
#============================================================================== 
#层长恢复完整版
def LengthRecover(total_fractions,
                  img_tag,
                  img_rgb,
                  rgb_dict,
                  show=False,
                  animation=False):
      
    #拾取出某个目标layer
    which_layer=Pick.PickLayer(total_fractions,img_rgb)
        
    #计算曲线的长度
    layer_length=FittingCurvedLinesLength(which_layer,img_rgb)
    
    #初始化面积
    which_layer.InitArea()
    
    #层厚度(其实没什么意义)
    layer_thickness=which_layer.area/layer_length
    
    #初始化厚度和长度
    which_layer.thickness=layer_thickness
    
    #相关联的断层可能多个
    which_faults=Pick.BorderFaults(which_layer,total_fractions)
        
    #找出fault上的某点进行恢复
    #点击获取像素点坐标
    pick_point_pos=plt.ginput(1)[0]
    
    #给出fault上的某个点进行恢复    
    pick_point_temp=[int(pick_point_pos[1]),int(pick_point_pos[0])]
     
    print('')
    print('......')
    print('here comes the attachment point')
    
    #寻找最近的断层
    total_faults=Pick.DeleteLayer(total_fractions)
    
    #由attachment_point找一个合适的fault进行关联
    #找fault上符合条件的最接近的点
    total_faults_edge=[]
    
    #将total_faults中所有的edge提取出来
    for this_fault in total_faults:
        
        total_faults_edge+=this_fault.edge
        
    #找到拾取点最近的点
    attachment_point_temp=Geom.NearestPoint(pick_point_temp,total_faults_edge)
    
    #遍历出真知
    for this_fault in total_faults:
        
        if attachment_point_temp in this_fault.edge:
            
            nearest_fault=cp.deepcopy(this_fault)
            
            break
    
    #在这个最近的fault上寻找接应点
    attachment_point_fault=Geom.NearestPoint(attachment_point_temp,nearest_fault.edge)
    
    #需要描绘的点    
    points_to_draw=[]
    
    #用于迭代的总面积
    temp_area=len(points_to_draw)
    
    #循环结束的标志
    flag=(temp_area>=which_layer.area)
    
    #建立一个新的tag矩阵
    img_tag_temp=np.zeros(np.shape(img_tag))    
    
    #周围的断层只有一个
    if len(which_faults)==1:
        
        #one and only
        which_fault=which_faults[0]
        
        #判断which_fault和which_layer的关系
        #左边界
        if which_layer.center[1]<which_fault.center[1]:
            
            direction='left'
        
        #右边界
        if which_layer.center[1]>which_fault.center[1]:
            
            direction='right'
        
        #开始迭代
        '''循环中'''
        while not flag:
            
            print('')
            print('......')
            print('iteration:length recovering')
            
        #    print(temp_area)
        #    print(attachment_point_fault)
    
            #本次迭代增加点儿
            that_points_to_draw=[]
            
            if direction=='left':
                
                #将这些点添加至列表
                for j in range(attachment_point_fault[1]-int(np.round(layer_length)),attachment_point_fault[1],1):
                    
                    that_point=[attachment_point_fault[0],j]
                    
#                    print('plus',j)
                    
                    if that_point not in which_fault.content:
                        
                        that_points_to_draw.append(that_point)
                    
            #填充
            if direction=='right':
            
                #将这些点添加至列表
                for j in range(attachment_point_fault[1]+int(np.round(layer_length)),attachment_point_fault[1],-1):
                    
                    that_point=[attachment_point_fault[0],j]
                    
#                    print('plus',j)
                    
                    if that_point not in which_fault.content:
                        
                        that_points_to_draw.append(that_point)
                        
            #加进大集合里
            points_to_draw+=that_points_to_draw
            
            #临时面积
            temp_area=len(points_to_draw)
            
            #更新循环执行的条件
            flag=(temp_area>=which_layer.area)
                        
            #改变每次迭代的attachment_point：默认自上而下
            
            #下一个接应点的i坐标
            i_attachment_point=attachment_point_fault[0]+1
            
            #直接在edge里寻找
            for this_pos in nearest_fault.edge:
                
                if this_pos[0]==i_attachment_point:
                    
        #            print('come on')
                
                    #将这个点定义为下一轮的接应点
                    attachment_point_fault=cp.deepcopy(this_pos)
                        
                    break
                
            #动画显示
            if animation:
                
                #把它们都绘制出
                for this_point in points_to_draw:
                    
                    img_tag_temp[this_point[0],this_point[1]]=which_layer.tag
                
                #让图片停留几秒钟之后关闭，可以是整数也可以是浮点数
                plt.imshow(Im.Tag2RGB(img_tag_temp,rgb_dict)) 
                plt.pause(1)
                plt.close()
                    
    #周围的断层不止一个
    if len(which_faults)>1:
        
        #根据横坐标的大小建立字典
        J_faults=[this_fault.center[1] for this_fault in which_faults]
        
        #坐标与fault对象的对应关系
        dict_J_faults=dict(zip(J_faults,which_faults))
            
        #判断fault的左右
        fault_left=dict_J_faults[min(J_faults)]
        fault_right=dict_J_faults[max(J_faults)]
        
        if fault_left.center[1]>fault_right.center[1]:
            
            fault_left=cp.deepcopy(which_faults[1])
            fault_right=cp.deepcopys(which_faults[0])
        
        #开始迭代
        '''循环中'''
        while not flag:
            
            print('')
            print('......')
            print('iteration:length recovering')
            
#            print(temp_area)
#            print(attachment_point_fault)
            
            #本次迭代增加点儿
            that_points_to_draw=[]
            
            #口袋装着fault的纵坐标
            pocket=[]
            
            #左右接应点
            for this_pos in fault_left.edge+fault_right.edge:
                
                if this_pos[0]==attachment_point_fault[0]:
                    
                    pocket.append(this_pos[1])
               
            #将这些点添加至列表
            for j in range(min(pocket),max(pocket)+1,1):
                
                that_point=[attachment_point_fault[0],j]
                
            #    print('plus',j)
                
                '''要在两个断层之间最大高度之内'''
                if that_point not in fault_left.content+fault_right.content:
                    
                    that_points_to_draw.append(that_point)
                    
            #增加的长度
            length_bonus=int(np.round(layer_length-FaultsInterval(which_layer)))
            
            #本次迭代加入点的J坐标最大值
            J_this_iteration=[this_pos[1] for this_pos in that_points_to_draw]
            J_this_iteration_max=max(J_this_iteration)
            
            #增加拉长之后增加的长度对应的像素点,从J_max开始
            for j in range(length_bonus):
                
                that_point=[attachment_point_fault[0],j+J_this_iteration_max+1]
               
            #    print('plus',j)
                
                that_points_to_draw.append(that_point)
            
            #加进大集合里
            points_to_draw+=that_points_to_draw
            
            #临时面积
            temp_area=len(points_to_draw)
            
            #更新循环执行的条件
            flag=(temp_area>=which_layer.area)
                        
            #改变每次迭代的attachment_point：默认自上而下
            
            #下一个接应点的i坐标
            i_attachment_point=attachment_point_fault[0]+1
            
            #直接在edge里寻找
            for this_pos in nearest_fault.edge:
                
                if this_pos[0]==i_attachment_point:
                    
        #            print('come on')
                
                    #将这个点定义为下一轮的接应点
                    attachment_point_fault=cp.deepcopy(this_pos)
                        
                    break
           
            #动画显示
            if animation:
                
                #把它们都绘制出
                for this_point in points_to_draw:
                    
                    img_tag_temp[this_point[0],this_point[1]]=which_layer.tag
                
                #让图片停留几秒钟之后关闭，可以是整数也可以是浮点数
                plt.imshow(Im.Tag2RGB(img_tag_temp,rgb_dict)) 
                plt.pause(1)
                plt.close()
            
    #把它们都绘制出
    for this_point in points_to_draw:
        
        img_tag_temp[this_point[0],this_point[1]]=which_layer.tag
        
    #显示呗    
    if show:
            
        plt.imshow(Im.Tag2RGB(img_tag_temp,rgb_dict)) 
      
    #改变fraction的content
    which_layer.content=cp.deepcopy(points_to_draw)
    
    #更新which_fraction的一切？
    which_layer.UpdateAll()
    
    #关闭当前窗口
    plt.close()
    
    return which_layer
    
#============================================================================== 
#多个layer层长的恢复:多个fractions
def RecoverStratas(total_fractions):
    
    return

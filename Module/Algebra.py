# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 19:38:42 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Algebra
"""

import copy as cp
import numpy as np
import matplotlib.pyplot as plt

from Module import Geometry as Geom
from Module import Dictionary as Dict

#============================================================================== 
#计算列表平均值的函数
def GetAverage(which_data):
    sum_data=0
        
    for item in which_data:
        
        sum_data+=item
        
    return sum_data/len(which_data)

#==============================================================================     
#计算列表中位数的函数
def GetMedian(which_data):
    
    data=sorted(which_data)
    size=len(which_data)
    
    #判断列表长度为偶数
    if size%2==0:   
        
        return (data[size//2]+data[size//2-1])/2
    
    #判断列表长度为奇数    
    if size%2==1:   
        
        return data[(size-1)//2]     
 
#==============================================================================                 
#计算某点某特征值的函数
#which_data表示需要计算的集合
#mode表示计算的模式：average表示平均值，median表示中位数，interpolation表示插值  
#which_chips表示需要计算高度的那个chips
#threshold表示用于计算的自变量的取值范围            
def CalculateThisPoint(which_data,mode,which_chips=None,threshold=None):
    
    #还原成相应的I坐标
    I_which_data=[pos[0] for pos in which_data]
    J_which_data=[pos[1] for pos in which_data]
    
    #平均值
    if mode=='average':
        
        return int(np.round(GetAverage(I_which_data)))
    
    #中位数
    if mode=='median':
        
        return int(np.round(GetMedian(I_which_data)))
    
    """插值比较特殊：可能需要提供坐标？？？"""
    #插值
    if mode=='interpolation':
        
#        print(threshold)
#        print('......')
#        
#        print(which_data)        
#        print('......')
#
#        print(which_chips.content)
#        print('......')
#        
#        print(len(which_chips.content))
#        print('......')
#     
#        print(GetInterpolation(which_data,threshold))
#        print('......')
#        
#        print(len(GetInterpolation(which_data,threshold)))       
#        print('......')
             
        result_interpolation=GetInterpolation(which_data,threshold)
        
        result_final=CrossDataAB(which_chips.content,result_interpolation)
        
#        print(result_final)
#        print('......')
        
        #9.2
        
        """若结果不止一个，或为0，如何处理？？"""        
        #结果为空
        if len(result_final)==0:
            
            #neighbor大法好 
            #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
            neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
            
            #遍历插值结果
            for pos in result_interpolation:
             
                #逆时针遍历邻域内的点
                for item in neighbordict:
                    
                    #遍历新的坐标            
                    new_pos=[pos[0]+item[0],pos[1]+item[1]]
                    
                    if new_pos in which_chips.content: 
                        
                        if new_pos not in result_final:
                            
                            result_final.append(new_pos)     
                            
        #结果不止一个
        if len(result_final)>1:
            
            #计算which_data的中心
            center_which_data=[np.mean(I_which_data),np.mean(J_which_data)]
            
            #中心到各个result的距离
            distance_center2result=[Geom.Distance(this_pos,center_which_data) for this_pos in result_final]
        
            #距离和result建立键值对
            map_distance_center2result=dict(zip(distance_center2result,result_final))
            
            #返回距离最小的哥
            result_final=[map_distance_center2result[min(distance_center2result)]]
        
        #结果就一个,返回其I坐标 
        if len(result_final)==1:
                
#            print(result_final[0])
        
            return result_final[0][0]
        else:           
            return None
 
"""以下部分为计算插值系列函数"""
#============================================================================== 
#二次函数的标准形式
def func(params,x):
    
    a,b,c=params
    
    return a*x**2+b*x+c

#============================================================================== 
#误差函数，即拟合曲线所求的值与实际值的差
def error(params,x,y):
    
    return func(params,x)-y

#============================================================================== 
#对参数求解
def slovePara(X,Y):
    
    #p0里放的是a、b、c的初始值，这个值可以随意指定。
    #往后随着迭代次数增加，a、b、c将会不断变化，使得error函数的值越来越小。
    p0=[10,10,10]
    
    from scipy.optimize import leastsq
    
    #leastsq的返回值是一个tuple
    #它里面有两个元素，第一个元素是a、b、c的求解结果，第二个则为cost function的大小！
    Para=leastsq(error,p0,args=(X,Y))
    
    return Para

#==============================================================================    
#which_data表示参与的坐标
#threshold是拟合出的曲线的自变量上下限列表
def GetInterpolation(which_data,threshold,show=False):
    
    #转化为一维列表
    I_which_data=[pos[0] for pos in which_data]
    J_which_data=[pos[1] for pos in which_data]
    
    #z幻化为np.array对象，便于处理：X为自变量，Y为因变量 
    X=np.array(J_which_data)
    Y=np.array(I_which_data)

    Para=slovePara(X,Y)
    a,b,c=Para[0]
    
#    print(a,b,c)   
 
    #在threshold范围内直接画100个连续点
    amount=max(threshold)-min(threshold)+1
    x=np.linspace(min(threshold),max(threshold),amount) 

#    print(amount)
    
    #函数式
    y=a*x*x+b*x+c 
    
    #是否输出图形
    if show:
        
        #保留两位小数
        a=float('%0.2f'%a)
        b=float('%0.2f'%b)
        c=float('%0.2f'%c)
        
        print("a=",a,"b=",b,"c=",c)
        print("cost:" + str(Para[1]))
        print("求解的曲线是:")
        print("y="+str(round(a,2))+"x*x+"+str(round(b,2))+"x+"+str(c))
    
        plt.figure(figsize=(8,6))
        plt.scatter(X,Y,color="green",label="sample data",linewidth=2)
    
        #画拟合直线
        plt.plot(x,y,color="red",label="solution line",linewidth=2)
        
        #绘制图例
        plt.legend() 
        plt.show()
    
    #输出x和y组成的坐标集合
    return Geom.CombineXY(y,x)

#============================================================================== 
#计算集合data_A和data_B交集
def CrossDataAB(data_A,data_B):
    
    #结果列表
    data_cross=[]
    
    for pos in data_A:
        
        if pos in data_B:
            
            data_cross.append(pos)
    
    return data_cross

"""在找到第一个导数大于0的点时，把前半段补到最后"""
#============================================================================== 
def ReOrder(which_content):
    
    #所有函数值
    values=cp.deepcopy(which_content)
    
    #边缘两个取隔壁和自己的差，中间取隔壁俩的差
    gradients=np.gradient(values)
    
    #遍历寻找第一个这种点
    for k in range(len(gradients)):
        
        if gradients[k]>0:
                    
            break
      
    #重新定义顺序
    return values[k:]+values[:k]    
      
#11.25
#============================================================================== 
#计算一个序列which_content的极值点并显示
#mode:'big','small','both'表示极大值，极小值，所有极值
def GetExtremePoints(which_content,mode='big',show=False):
    
#    print('GetExtremePoints')
    
    #所有函数值
#    values=ReOrder(which_content)
    values=cp.deepcopy(which_content)
    
    #边缘两个取隔壁和自己的差，中间取隔壁俩的差
    gradients=np.gradient(values)
    
    #建立梯度和值的映射关系
    map_values_gradients=dict(zip(values,gradients))
    
    #得到极值的索引
    index_extreme_points=[]
    
    #values用于显示的点
    values_X_Y_to_plot=[] 
    
    #gradients用于显示的点
    gradients_X_Y_to_plot=[] 
    
    #求得的极值列表
    extreme_values=[]
    
#    print(gradients)
#    print(map_values_gradients)
    
    #寻找0极值,去掉首元素
    for k in range(1,len(values)):
           
#        print(gradients[k-1],gradients[k])
        
        #极大值
        if mode=='big':
            
            #左右两边一大一小
            if gradients[k-1]>0>gradients[k]:
                               
                that_value_left=Dict.DictKeyOfValue(map_values_gradients,gradients[k-1])        
                that_value_right=Dict.DictKeyOfValue(map_values_gradients,gradients[k])
                
                that_value=max(that_value_left,that_value_right)
                
            else:
                
                continue
                
        #极小值
        if mode=='small':

            #左右两边一大一小
            if gradients[k-1]<0<gradients[k]:
                
                that_value_left=Dict.DictKeyOfValue(map_values_gradients,gradients[k-1])        
                that_value_right=Dict.DictKeyOfValue(map_values_gradients,gradients[k])
                
                that_value=min(that_value_left,that_value_right)
                
            else:
                
                continue
            
#        #所有极值
#        if mode=='both':
#
#            #左右两边一大一小
#            if gradients[k-1]>0>gradients[k] or gradients[k-1]<0<gradients[k]:
#                
#                that_value_left=Dict.DictKeyOfValue(map_values_gradients,gradients[k-1])        
#                that_value_right=Dict.DictKeyOfValue(map_values_gradients,gradients[k])
#                
#                that_value=max(that_value_left,that_value_right)
                
#        print(that_value_left,that_value_right)
        
        #极值列表上车
        extreme_values.append(that_value)
        
        #该极值索引
        that_index=list(values).index(that_value)
        
        index_extreme_points.append(that_index)
        
        #描绘的点上车吧
        values_X_Y_to_plot.append([that_index,values[that_index]])
        
        gradients_X_Y_to_plot.append([that_index,gradients[that_index]])
        
#    print(extreme_values)  

#    print(distances_X_Y_to_plot)
#    print(gradients_X_Y_to_plot)
    
    #显示吗
    if show:
        
#        print('show')
        
        #绘制值曲线
        plt.figure()
        
        plt.subplot(211)
        plt.plot(values,color='black',linestyle='-') 
        
        for this_X_Y in values_X_Y_to_plot:
            
            plt.scatter(this_X_Y[0],this_X_Y[1],color='red') 
    
        #绘制梯度曲线    
        plt.subplot(212)
        plt.plot(gradients,color='black',linestyle='--')
        
        for this_X_Y in gradients_X_Y_to_plot:
        
            plt.scatter(this_X_Y[0],this_X_Y[1],color='red') 
      
    return extreme_values     

"""
不合理！！！
尝试用折线图点击获取，升华到深度学习
"""
#11.26
#============================================================================== 
#计算一个序列which_content的边界最值点并显示
#mode:'big','small','both'表示边界最大值，最小值，所有最值
def GetFringePoints(which_content,mode='big',show=False):    
    
#    print('GetFringePoints')
    
    #所有函数值
#    values=ReOrder(which_content)
    values=cp.deepcopy(which_content)
    
    #边缘两个取隔壁和自己的差，中间取隔壁俩的差
    gradients=np.gradient(values)
    
    #得到最值的索引
    index_fringe_points=[0,len(values)-1]
    
    #求得的最值列表:面向用例
    fringe_values=[values[this_index] for this_index in index_fringe_points]
    
    #values用于显示的点
    values_X_Y_to_plot=[]
    
    #gradients用于显示的点
    gradients_X_Y_to_plot=[]
    
    for this_index in index_fringe_points:
        
        #描绘的点上车吧
        values_X_Y_to_plot.append([this_index,values[this_index]])
        
        gradients_X_Y_to_plot.append([this_index,gradients[this_index]])
           
    #显示吗
    if show:
        
#        print('show')
        
        #绘制值曲线
        plt.figure()
        
        plt.subplot(211)
        plt.plot(values,color='black',linestyle='-') 
        
        for this_X_Y in values_X_Y_to_plot:
            
            plt.scatter(this_X_Y[0],this_X_Y[1],color='blue') 
    
        #绘制梯度曲线    
        plt.subplot(212)
        plt.plot(gradients,color='black',linestyle='--')
        
        for this_X_Y in gradients_X_Y_to_plot:
        
            plt.scatter(this_X_Y[0],this_X_Y[1],color='blue') 
            
    return fringe_values

#11.26
#============================================================================== 
#计算一个序列which_content的可疑点并显示
#mode:'big','small','both'表示可疑点最大值，最小值，所有最值
def GetSuspiciousPoints(which_content,mode='big',show=False): 
    
#    print('GetSuspiciousPoints')
    
    #所有函数值
#    values=ReOrder(which_content)
    values=cp.deepcopy(which_content)
    
    """还得考虑坐标，否则相同的值有多个坐标"""
    #极值
    extreme_values=GetExtremePoints(values,mode)
    
    #最值
    fringe_values=GetFringePoints(values,mode)

#    print(extreme_values)
#    print(fringe_values)
    
    #可疑值集合:包括极值点和最值点
    suspicious_values=extreme_values+fringe_values
    
    #极值的索引
    index_extreme_points=[]
    
    #用于显示的极值点
    extreme_values_X_Y_to_plot=[]
    
    #计算极值点的索引
    for this_value in extreme_values:
        
        #该极值索引
        that_index=list(values).index(this_value)
        
        index_extreme_points.append(this_value)
    
        #描绘的点上车吧
        extreme_values_X_Y_to_plot.append([that_index,values[that_index]])
        
    #最值的索引
    index_fringe_points=[]  
    
    #用于显示的最值
    fringe_values_X_Y_to_plot=[]  
    
    #计算最值点的索引
    for this_value in fringe_values:
        
        #该极值索引
        that_index=list(values).index(this_value)
        
        index_fringe_points.append(this_value)
    
        #描绘的点上车吧
        fringe_values_X_Y_to_plot.append([that_index,values[that_index]])    
    
    #显示吗
    if show:
       
#        print('show')
        
        #绘制值曲线
        plt.figure()
 
        plt.plot(values,color='black',linestyle='-') 
        
        for this_X_Y in extreme_values_X_Y_to_plot:
            
            plt.scatter(this_X_Y[0],this_X_Y[1],color='red') 
           
        for this_X_Y in fringe_values_X_Y_to_plot:
        
            plt.scatter(this_X_Y[0],this_X_Y[1],color='blue') 
            
    return suspicious_values
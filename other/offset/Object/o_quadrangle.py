# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:48:30 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-quadrangle
"""

import numpy as np

from o_triangle import triangle

#==============================================================================              
#定义四边形类
#==============================================================================  
class quadrangle:
    def __init__(self,ABCD,
                 area=None):
        
        #A,B,C,D是按照顺时针或逆时针的顺序
        self.ABCD=[]
        
        #数组化
        for pos in ABCD:
            self.ABCD.append(np.array(pos))
        
#        print(self.ABCD)
            
#7.5       
    #判断四边形的凹凸
    def ConcaveOrConvex(self):
        
        #转化为数组
        pos_ABCD=[]
        
        for pos in self.ABCD: 
            pos_ABCD.append(list(pos))
            
#        print(pos_ABCD)
        
        #四个顶点的坐标
        pos_A,pos_B,pos_C,pos_D=pos_ABCD
        
        #生成一个列表表示各点在三角形内部与否的逻辑值列表
        bool_point_in_triangle_list=[]
        
        #判断四个点和其他三个点组成的三角形的位置关系
        for pos in pos_ABCD:
            
            #删取一个顶点
            pos_triangle_temp=pos_ABCD.copy()
            pos_triangle_temp.remove(pos)
            
#            print(pos)
#            print(pos_triangle_temp)
     
            #三个顶点生成三角形
            triangle_temp=triangle(pos_triangle_temp)
            
#            print(triangle_temp.area)
            
            #将逻辑值加入列表
            bool_point_in_triangle=triangle_temp.IncludePoint(pos)
            
#            print(bool_point_in_triangle)
            
            bool_point_in_triangle_list.append(bool_point_in_triangle)
        
#        print(bool_point_in_triangle_list)
        
        #判断是否有点不在三角形内
        if True in bool_point_in_triangle_list:   
            return 'concave'
        else:
            return 'convex'    
        
    #只有凸的四边形才有资格讨论顶点的顺序徐
        
    """让任意四个点两两连接，若他们的角点满足一定的条件，可以确定他们是对角"""
    #给四边形四个顶点以正确的链接顺序排序
    def Order(self):
        
        #若四边形凹
        if self.ConcaveOrConvex()=='concave':
            
            #重新给出合理坐标
            print('give the points in order')
        
        if self.ConcaveOrConvex()=='convex':
            
            #排序后的答案
            pos_ABCD_ordered=[]
            
            pos_ABCD=[]
        
            #转化为数组
            for pos in self.ABCD: 
                pos_ABCD.append(np.array(pos))
                
            #四个顶点的坐标
            pos_A,pos_B,pos_C,pos_D=pos_ABCD
             
            #排列组合库
            import itertools
            
            #下标集合
            index_total=[k for k in range(len(pos_ABCD))]
            
            #列表内是总元素，数字是元素数量
            index_list=list(itertools.combinations(index_total,2))
            
            #index表示任意两个点的下标
            for index_MN in index_list:
                
                #MN之外的另外两个拟对角点  
                index_UV=[index for index in index_total if index not in index_MN]
                
#                print(index_MN,index_UV)
                
                #MN表示拟对角线中的其中一条
                pos_M=pos_ABCD[index_MN[0]]
                pos_N=pos_ABCD[index_MN[1]]
                
                #UV表示拟对角线中的其中一条
                pos_U=pos_ABCD[index_UV[0]]
                pos_V=pos_ABCD[index_UV[1]]
#                
#                print(pos_M,pos_N,pos_U,pos_V)
#                print((pos_M-pos_N)[0],(pos_M-pos_N)[1])
                
                #求MN和PQ的交点O     
                #解方程组              
#7.6             
                #先求一些系数
                a_MN=(pos_M-pos_N)[1]/(pos_M-pos_N)[0]
                b_MN=-1
                c_MN=pos_N[1]-pos_N[0]*a_MN
                
                a_UV=(pos_U-pos_V)[1]/(pos_U-pos_V)[0]
                b_UV=-1
                c_UV=pos_V[1]-pos_V[0]*a_UV
                
                #保留2位小数
#                a_MN,b_MN,c_MN=float('%0.2f' %a_MN),float('%0.2f' %b_MN),float('%0.2f '%c_MN)
#                a_UV,b_UV,c_UV=float('%0.2f '%c_UV),float('%0.2f' %b_UV),float('%0.2f' %a_UV)
#              
#                print(a_MN,b_MN,c_MN)
#                print(a_UV,b_UV,c_UV)
          
                import sympy
                
                x=sympy.Symbol('x')
                y=sympy.Symbol('y')
                
                #得到的解是一个数组
                answer=sympy.solve([x*a_MN+y*b_MN+c_MN,x*a_UV+y*b_UV+c_UV],[x,y])
    
                #若两条线平行，那么他们没有交点，因此解坐标不存在
                if answer!=[]:
                    
                    x,y=answer[x],answer[y]
                                           
                    #O为对角线交点
                    pos_O=np.array([x,y])
    
#                    print(pos_O)                      
#                    print(pos_M,pos_O,pos_N)
#                    print(pos_U,pos_O,pos_V)
                    
                    #判断对角线交点在四边形内部还是在反向延长线上
                    #好几种情况:升 降都有可能
                    
                    #MN 
                    pos_MN_max=[max(pos_M[0],pos_N[0]),max(pos_M[1],pos_N[1])]
                    pos_MN_min=[min(pos_M[0],pos_N[0]),min(pos_M[1],pos_N[1])]
            
                    #UV
                    pos_UV_max=[max(pos_U[0],pos_V[0]),max(pos_U[1],pos_V[1])]
                    pos_UV_min=[min(pos_U[0],pos_V[0]),min(pos_U[1],pos_V[1])]
                    
                    #判断坐标在区间内
                    if pos_MN_min[0]<=pos_O[0]<pos_MN_max[0]\
                    and pos_MN_min[1]<=pos_O[1]<pos_MN_max[1]\
                    and pos_UV_min[0]<=pos_O[0]<pos_UV_max[0]\
                    and pos_UV_min[1]<=pos_O[1]<pos_UV_max[1]:
                        
                        #保留两位小数    
                        x=float('%0.2f' %pos_O[0])
                        y=float('%0.2f' %pos_O[1])
                    
                        pos_O=np.array([x,y])
                        
#                        print(pos_O)               
#                        print('correct point')   
                        
                        #输出正确顺序的点
                        pos_ABCD_ordered=[pos_M,pos_U,pos_N,pos_V]
                        
#                        print(pos_ABCD_ordered)
           
                        break  
                    
            #正确答案非空            
            if pos_ABCD_ordered!=[]:    
                return pos_ABCD_ordered
    
    #初始化面积这一属性
    def InitArea(self):
        
        #重新排列
        self.ABCD=self.Order()
        
#        print(self.ABCD)
        
        #转化为数组
        pos_ABCD=[]
        
        for pos in self.ABCD: 
            pos_ABCD.append(list(pos))
        
        #分割成小三角形并计算面积
        
        #这三个点索引为012和023
        point_list_triangle_1=pos_ABCD.copy()
        point_list_triangle_2=pos_ABCD.copy()
        
        #需要删除的点:索引为1和3
        point_triangle_1=pos_ABCD[1]
        point_triangle_2=pos_ABCD[3]
        
        #删除点
        point_list_triangle_1.remove(point_triangle_1)
        point_list_triangle_2.remove(point_triangle_2)
        
        #求面积
        area_triangle_1=triangle(point_list_triangle_1).area
        area_triangle_2=triangle(point_list_triangle_2).area
        
#        print(self.ABCD[:-1])
#        print(self.ABCD[1:])
#        
#        print(area_triangle_1)
#        print(area_triangle_2)
        
        #四边形的总面积
        self.area=np.around(area_triangle_1+area_triangle_2,2)
        
#        print(self.area)
        
    #判断点是否在四边形内部   
    def IncludePoint(self,pos_P):
        
        #方法1:通过四个三角形总面积来判断
        #重新排列
        self.ABCD=self.Order()
           
        #转化为数组
        pos_ABCD=[]
        
        for pos in self.ABCD: 
            pos_ABCD.append(list(pos))
            
#        print(pos_ABCD)  
            
        #转化类型
#        pos_P=np.array(pos_P)
        
#7.9
        #分别计算四个三角形的面积
        #临时列表存放ABCD的坐标
        pos_ABCD_temp=self.ABCD.copy()
        
        #小三角形定则总面积
        total_area_triangle=0
        
        #测点位于小三角形内部的情况逻辑值列表
        list_point_in_triangle=[]
        
        #想办法让首元素顶到尾部
        for k in range(len(pos_ABCD)):
            
            #第一个元素
            first_point=pos_ABCD_temp[0]
            
            #赋值顶点列表
            point_list_triangle=pos_ABCD_temp[0:2]     
            
            #增加被检测点
            point_list_triangle.append(pos_P)
            
            #删除第一个元素并添加至末尾
            pos_ABCD_temp.remove(first_point)
            pos_ABCD_temp.append(first_point)
            
#            print(point_list_triangle)
            
            #小三角形的面积的总面积
            triangle_temp=triangle(point_list_triangle)
            total_area_triangle+=triangle_temp.area
            
            #测点位于小三角形内部的情况
            list_point_in_triangle.append(triangle_temp.IncludePoint(pos_P))
        
        method=2
    
        #方法1:通过四个三角形总面积和四边形面积的关系来判断
        if method==1:
        
            #若小三角形总面积和四边形面积相等，那么说明被检测点在四边形内部
            self.InitArea()
            
#            print(self.area)
#            print(total_area_triangle)
                   
            #由于浮点型，两者在小数点后好几位会有所差别，所以需要四舍五入
            if np.round(total_area_triangle-self.area)==0:
                
                return True
            else:
                return False          
            
        #方法2:通过点在四个三角形的情况来判断
        if method==2:
            
            #只要列表内部不存在False即可判断点在四边形内部
            if False not in list_point_in_triangle:
                
                return True
            else:
                return False      
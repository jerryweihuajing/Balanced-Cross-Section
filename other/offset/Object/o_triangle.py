# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:45:23 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-triangle
"""

import numpy as np

#==============================================================================  
#定义一个三角形的类
#==============================================================================  
class triangle:
    def __init__(self,ABC,
                 area=None):
        
        #ABC表示三角形三个顶点,初始化时就应当定义它
        self.ABC=[]
        
        #数组化
        for pos in ABC:
            self.ABC.append(np.array(pos))
 
        #三个顶点的坐标
        pos_A,pos_B,pos_C=self.ABC
        
        #计算三条边长
        AB=whj.Distance(pos_A,pos_B)
        AC=whj.Distance(pos_A,pos_C)
        CB=whj.Distance(pos_C,pos_B)
        
        a,b,c=CB,AC,AB
        p=(a+b+c)/2

        #area表示三角形面积
        self.area=np.sqrt(p*(p-a)*(p-b)*(p-c))
    
    #判断点是否在三角形内部   
    def IncludePoint(self,pos_P):
        
        #还原ABC坐标
        pos_A,pos_B,pos_C=self.ABC
        
        #向量化
        pos_A=np.array(pos_A)
        pos_B=np.array(pos_B)
        pos_C=np.array(pos_C)
        
        pos_P=np.array(pos_P)
        
        #使用方法2
        method='2'
        
        #方法一：面积法
        if method=='1':
    
            Area_PAB=triangle(pos_A,pos_B,pos_P).area  
            Area_PAC=triangle(pos_A,pos_P,pos_C).area    
            Area_PBC=triangle(pos_P,pos_B,pos_C).area 
            
            Area_ABC=triangle(pos_A,pos_B,pos_C).area
            
            Area_sum=Area_PAB+Area_PAC+Area_PBC
            
            #判断PAB,PAC,PBC的总面积和ABC是否相等   
            if Area_sum==Area_ABC:
                
                return True  
            else:
                return False
        
        #方法二：向量法      
        if method=='2':
            
            #向量法：_AP=u*_AC+v*_AB，其中_AP,_AB,_AC都是向量
            _AP=pos_A-pos_P
            
            _AC=pos_A-pos_C
            _AB=pos_A-pos_B
            
            #解方程组
            #_AP[0]=u*_AC[0]+v*_AB[0]
            #_AP[1]=u*_AC[1]+v*_AB[1]
           
            #计算二元一次方程组
            import sympy
            
            u=sympy.Symbol('u')
            v=sympy.Symbol('v')
            
            #得到的解是一个数组
            answer=sympy.solve([u*_AC[0]+v*_AB[0]-_AP[0],u*_AC[1]+v*_AB[1]-_AP[1]],[u,v])
            
#            print(answer[u],answer[v])
            
            u,v=answer[u],answer[v]
            
            #判断条件：0<=u<=1,0<=v<=1,0<=u+v<=1
            if 0<=u<=1 and 0<=v<=1 and 0<=u+v<=1:
                
                return True  
            else:
                return False   
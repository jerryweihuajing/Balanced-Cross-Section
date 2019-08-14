# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:45:23 2018

@author: Wei Huajing
@company: Ameng Science and Technology Education Co., Ltd
@e-mail: jerryweihuajing@126.com

@title：Object-triangle
"""

import numpy as np

import Geometry as Geom

#==============================================================================  
#define a trinagle class
#==============================================================================  
class triangle:
    def __init__(self,
                 ABC=None,
                 area=None):

        self.ABC=[]

        #transfrom them into np.array
        for pos in ABC:
            
            self.ABC.append(np.array(pos))
 
        #three
        pos_A,pos_B,pos_C=self.ABC
        
        #Calculate three boundary length
        AB=Geom.Distance(pos_A,pos_B)
        AC=Geom.Distance(pos_A,pos_C)
        CB=Geom.Distance(pos_C,pos_B)
        
        #Helen formula
        a,b,c=CB,AC,AB
        p=(a+b+c)/2

        #area: traingle area
        self.area=np.sqrt(p*(p-a)*(p-b)*(p-c))
    
    #judge whether pos_P is inside the triangle  
    def IncludePoint(self,pos_P):
        
        pos_A,pos_B,pos_C=self.ABC
        
        #Vetorization
        pos_A=np.array(pos_A)
        pos_B=np.array(pos_B)
        pos_C=np.array(pos_C)
        
        pos_P=np.array(pos_P)
        
        #vector method
        _AP=pos_A-pos_P
        _AC=pos_A-pos_C
        _AB=pos_A-pos_B

        #Calculate quadratic system of one variable
        import sympy
        
        u=sympy.Symbol('u')
        v=sympy.Symbol('v')
        
        #The solution is an np.array
        answer=sympy.solve([u*_AC[0]+v*_AB[0]-_AP[0],u*_AC[1]+v*_AB[1]-_AP[1]],[u,v])
        
        u,v=answer[u],answer[v]
        
        #Judgement conditions：0<=u<=1,0<=v<=1,0<=u+v<=1
        if 0<=u<=1 and 0<=v<=1 and 0<=u+v<=1:
            
            return True  
        
        else:
            
            return False   
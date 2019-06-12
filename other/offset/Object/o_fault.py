# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:39:38 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-fault
"""

import numpy as np

from Object.o_fraction import fraction

#==============================================================================  
#定义一个fault类，继承fraction类
#重构属性和继承方法，增加inclination表示倾向，polarity属性表示断层的性质
#==============================================================================  
class fault(fraction):
    
    #先继承,后重构
    def __init__(self,id=None,
                 tag=None,
                 part=None,
                 edge=None,
                 content=None,
                 center=None,
                 inclination=None,
                 polarity=None,
                 tilt=None,
                 k=None):  
        
        #继承父类的构造方法
        fraction.__init__(self,id=None,
                          tag=None,
                          part=None,
                          edge=None,
                          content=None,
                          center=None)  
        self.inclination=inclination
        self.polarity=polarity  
        self.tilt=tilt
        self.k=k
    
    #在img_tag中寻找fault两侧的标签为target_tag的顶或底角点    
    def Init(self,img_tag,show=False):
        
        #拾取fault附近的四个角点
        pos_top_left,pos_bottom_left,pos_top_right,pos_bottom_right=self.AngleLeftRight(img_tag)
        
        #根据倾向确定上下盘：用top和bottom点反映倾向
        
        #1 左倾：左为上盘，右边为下盘
        #j_top>j_bottom
        
        #第一个left表示的倾向，第二个left表示断裂的左或右侧
        bool_left_left=pos_top_left[1]>pos_bottom_left[1]       
        bool_left_right=pos_top_right[1]>pos_bottom_right[1]
        
        if bool_left_left and bool_left_right:
            self.inclination='left'
        
        #2 右倾：左为上盘，右边为下盘
        #j_top<j_bottom
        
        #第一个right表示的倾向，第二个right表示断裂的左或右侧
        bool_right_left=pos_top_left[1]<pos_bottom_left[1]       
        bool_right_right=pos_top_right[1]<pos_bottom_right[1]
        
        if bool_right_left and bool_right_right:
            self.inclination='right'
            
        #判断断层极性
        #bottom和top反映的错动距离应当是一样的
        
        #正断：上盘向下，下盘向上，拉张
        #逆断：上盘向上，下盘向下，挤压

        #备用判断方式：横向
        
        if (self.inclination=='left'\
            and pos_top_right[1]>pos_top_left[1]\
            and pos_bottom_right[1]>pos_bottom_left[1])\
        or (self.inclination=='right'\
            and pos_top_right[1]>pos_top_left[1]\
            and pos_bottom_right[1]>pos_bottom_left[1]):    
            
            self.polarity='positive' 
        
        #逆断
        if (self.inclination=='left'\
            and pos_top_right[1]<pos_top_left[1]\
            and pos_bottom_right[1]<pos_bottom_left[1])\
        or (self.inclination=='right'\
            and pos_top_right[1]<pos_top_left[1]\
            and pos_bottom_right[1]<pos_bottom_left[1]):
            
            self.polarity='negative'  
            
        #正式判断方式：纵向
        
        #正断
        if (self.inclination=='left'\
            and pos_top_right[0]<pos_top_left[0]\
            and pos_bottom_right[0]<pos_bottom_left[0])\
        or (self.inclination=='right'\
            and pos_top_right[0]>pos_top_left[0]\
            and pos_bottom_right[0]>pos_bottom_left[0]):    
            
            self.polarity='positive' 
        
        #逆断
        if (self.inclination=='left'\
            and pos_top_right[0]>pos_top_left[0]\
            and pos_bottom_right[0]>pos_bottom_left[0])\
        or (self.inclination=='right'\
            and pos_top_right[0]<pos_top_left[0]\
            and pos_bottom_right[0]<pos_bottom_left[0]):
            
            self.polarity='negative'     
        
        #显示fault信息     
        if show: 
            
            print('')
            print('fault')
            print('part:',self.part)
            print('inclination:',self.inclination)
            print('polarity:',self.polarity)
            
        #初始化倾角
        
        #fault边缘点坐标
        I=[pos[0] for pos in self.edge]
        J=[pos[1] for pos in self.edge]
            
        #用J检索I
        I_J=dict(zip(I,J))
        
        #边缘集合中两侧存在layer_tag的最高点和最低点
        pos_top=np.array([max(I),I_J[max(I)]])
        pos_bottom=np.array([min(I),I_J[min(I)]])
        
        #斜率
        self.k=(pos_top-pos_bottom)[0]/(pos_top-pos_bottom)[1]
    
        #倾角
        self.tilt=180*np.arctan(abs(self.k))/np.pi
         
    """如何找到角点？Fault的edge,左右tag值？"""  
    #拾取fault左右盘的四个角点，并返回
    def AngleLeftRight(self,img_tag):
        
        pos_top_left,pos_bottom_left,pos_top_right,pos_bottom_right=None,None,None,None
        
        #边缘左侧点坐标列表
        edge_left=[]
        
        #边缘右侧点坐标列表
        edge_right=[]
        
        #fault.edge中符合左右tag值的即可 
        for pos in self.edge:
               
            #左右tag值
            pos_left=[pos[0],pos[1]-1]
            pos_right=[pos[0],pos[1]+1]
            
            #左右点集合
            if img_tag[int(pos_left[0]),int(pos_left[1])]!=-1:
                
                edge_left.append(pos_left)
                
            if img_tag[int(pos_right[0]),int(pos_right[1])]!=-1:
                
                edge_right.append(pos_right)      
        
        """增加不存在fault角点的处理机制"""
        
        #左侧点的上下顶点
        I_left=[pos[0] for pos in edge_left]
        J_left=[pos[1] for pos in edge_left]
        
        #两个列表合成字典
        I_J_left=dict(zip(I_left,J_left))
        
        #寻找块体角点
        if I_left!=[]:
            
            pos_top_left=[min(I_left),I_J_left[min(I_left)]]
            pos_bottom_left=[max(I_left),I_J_left[max(I_left)]]

        #右侧点的上下顶点
        I_right=[pos[0] for pos in edge_right]
        J_right=[pos[1] for pos in edge_right]
        
        #两个列表合成字典
        I_J_right=dict(zip(I_right,J_right))
        
        #寻找块体角点
        if I_right!=[]:
            
            pos_top_right=[min(I_right),I_J_right[min(I_right)]]
            pos_bottom_right=[max(I_right),I_J_right[max(I_right)]]
        
        return pos_top_left,pos_bottom_left,pos_top_right,pos_bottom_right
        
    #拾取fault上下盘的四个角点，并返回
    def AngleUpDown(self,target_tag,img_tag):
        
        #获取左右盘的顶点
        pos_top_left,pos_bottom_left,pos_top_right,pos_bottom_right=self.AngleLeftRight(target_tag,img_tag)
       
        #信息初始化
        self.Init(target_tag,img_tag)
        
        #根据倾向的不同确定pos_top_up,pos_bottom_up,pos_top_down,pos_bottom_down
        #即上下盘的角点
        
        #左倾：左是上盘
        if self.inclination=='left':
            
            pos_top_up,pos_bottom_up=pos_top_left,pos_bottom_left
            pos_top_down,pos_bottom_down=pos_top_right,pos_bottom_right
            
        #右倾：右是上盘
        if self.inclination=='right':
            
            pos_top_up,pos_bottom_up=pos_top_right,pos_bottom_right
            pos_top_down,pos_bottom_down=pos_top_left,pos_bottom_left
            
        return pos_top_up,pos_bottom_up,pos_top_down,pos_bottom_down
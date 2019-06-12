# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:32:19 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-layer
"""

from Object.o_fraction import fraction

#==============================================================================  
#定义一个layer类，继承fraction类
#重构属性和继承方法，增加四个layer间灭点（fraction顶点）：
#left_top：左上角
#left_bottom：左下角
#right_top：右上角
#right_bottom：右上角
#==============================================================================  
class layer(fraction):
    
    #先继承,后重构
    def __init__(self,id=None,
                 tag=None,
                 part=None,
                 edge=None,
                 content=None,
                 center=None,
                 length=None,
                 thickness=None,
                 corners=None,
                 angle=None,                
                 top_left_list=None,
                 top_right_list=None,
                 bottom_left_list=None,
                 bottom_right_list=None,  
                 top_left=None,
                 top_right=None,
                 bottom_left=None,
                 bottom_right=None):

        #继承父类的构造方法
        fraction.__init__(self,id=None,
                          tag=None,
                          part=None,
                          edge=None,
                          content=None,
                          center=None,
                          length=None,
                          thickness=None,
                          corners=None)  

        #以下几个列表没啥用
        #拟角点的集合，可能多个
        self.angle=[]
        
        #四个象限的角点集合
        self.top_left_list=[]
        self.top_right_list=[]
        self.bottom_left_list=[] 
        self.bottom_right_list=[]
        
        """角点非常重要"""
        self.top_left=top_left
        self.top_right=top_right 
        self.bottom_left=bottom_left  
        self.bottom_right=bottom_right      
    
    #尝试Harris角点边缘检测
    
    """重写一个Adjust方法，用fault和pad来约束"""
    #最新版初始化角点
    def InitAngle(self,Fault,img_tag,img_rgb,rgb_dict,show=False):
        
        """1 收录layer与pad的边界点"""
    
        #临时角点集合
        Angle_temp=[]
                
        #edge的横纵坐标
        I_edge=[pos[0] for pos in self.edge]
        J_edge=[pos[1] for pos in self.edge]
        
        #找最小值
        J_min=min(J_edge)
        J_max=max(J_edge)
        
        #符合J最值的I列表与临时
        I_max_temp=[]
        I_min_temp=[]
          
        count=0
    
        for J in J_edge:   
            
            #收录两端的点
            if J==J_max:  
                I_max_temp.append(I_edge[count])
        
            if J==J_min:  
                I_min_temp.append(I_edge[count])  
            
            count+=1 
     
        #1表示背景白色   
        I_max=[I for I in I_max_temp if img_tag[I,J_max+1]==1]  
        I_min=[I for I in I_min_temp if img_tag[I,J_min-1]==1]
        
        #max I J 和 min I J 的排列组合
        #J控制左右，I控制上下
        #判断这种点是否存在并收录
        
        if I_max!=[]:
            
            self.bottom_right=[max(I_max),J_max]
            self.top_right=[min(I_max),J_max]
            
            Angle_temp.append(self.bottom_right)
            Angle_temp.append(self.top_right)
            
        if I_min!=[]:    
            
            self.bottom_left=[max(I_min),J_min]
            self.top_left=[min(I_min),J_min]
            
            Angle_temp.append(self.bottom_left)
            Angle_temp.append(self.top_left)
            
        #并创建空列表 
        Angle=[]
    
        #清除相同的点  
        for pos in Angle_temp:
            
            if pos not in Angle:  
                Angle.append(pos)
                
    #    print(len(Angle))
     
        """2 处理fault相关的角点"""
       
        #7.2   
        
        #包围layer的fault
        fault_to_be_boundary=[]
        
        for pos in self.edge:
            
            for this_fault in Fault:    
                
                if [pos[0],pos[1]+1] in this_fault.edge or [pos[0],pos[1]-1] in this_fault.edge:    
                    
                    if this_fault not in fault_to_be_boundary:
                        
                        fault_to_be_boundary.append(this_fault)
     
        J_fault_to_be_boundary=[this_fault.center[1] for this_fault in fault_to_be_boundary]
        
        #建立J和fault对象的索引
        dict_J_fault=dict(zip(J_fault_to_be_boundary,fault_to_be_boundary))  
    
#        print(len(fault_to_be_boundary))
            
        #先把pad相关的点收录进来    
        #先确保非空
    
        #收录某些列坐标
        J_pad_to_be_boundary=[]
        
        if Angle!=[] and len(Angle)!=4:
            
            J_pad_to_be_boundary=[pos[1] for pos in Angle]
            
            #同时符合这两个条件？？？
            
            #取最右的fault
            if max(J_pad_to_be_boundary)>max(J_fault_to_be_boundary):
                
                fault_boundary=dict_J_fault[min(J_fault_to_be_boundary)]
            
            #取最左的fault
            if min(J_pad_to_be_boundary)<min(J_fault_to_be_boundary):
                
                fault_boundary=dict_J_fault[max(J_fault_to_be_boundary)]
        
            """只能处理单个fault的情况"""
            #fault_boundary是锁定layer的fault
            
            #从fault_boundary上找合适的角点
            
            #先判断左右
            #center是按xy？？？
            
            if fault_boundary.center[0]<self.center[0]:
                
                fault_side='left'
              
            if fault_boundary.center[0]>self.center[0]:
                
                fault_side='right'
            
            #fault左右的坐标
            #初始化
            I_left_fault,J_left_fault=[],[]
            I_right_fault,J_right_fault=[],[]
            
            #左
            if fault_side=='left':
                
                for pos in fault_boundary.edge:
                    
                    if img_tag[pos[0],pos[1]+1]==self.tag:
                        
                        I_left_fault.append(pos[0])
                        J_left_fault.append(pos[1]+1)
                
            #右
            if fault_side=='right':
                 
                for pos in fault_boundary.edge:
                    
                    if img_tag[pos[0],pos[1]-1]==self.tag:
                        
                        I_right_fault.append(pos[0])
                        J_right_fault.append(pos[1]-1)
                     
#                #检验一波
#                print(len(I_left_fault),len(J_left_fault))
#                print(len(I_right_fault),len(J_right_fault))
            
            #建立索引咯 
            #左
            if I_left_fault!=[] and J_left_fault!=[]:
                
                I_J_left_fault=dict(zip(I_left_fault,J_left_fault))
                
                self.bottom_left=[max(I_left_fault),I_J_left_fault[max(I_left_fault)]]
                self.top_left=[min(I_left_fault),I_J_left_fault[min(I_left_fault)]]
                
                Angle.append(self.bottom_left)
                Angle.append(self.top_left)
                          
            #右边
            if I_right_fault!=[] and J_right_fault!=[]:  
                
                I_J_right_fault=dict(zip(I_right_fault,J_right_fault))  
        
                self.bottom_right=[max(I_right_fault),I_J_right_fault[max(I_right_fault)]]
                self.top_right=[min(I_right_fault),I_J_right_fault[min(I_right_fault)]]
                
                Angle.append(self.bottom_right)
                Angle.append(self.top_right)
           
        #先把pad相关的点不存在   
        #Angle集合为空
        
        if Angle==[]:
            
            #建立列表
            I_left_fault,J_left_fault=[],[]
            I_right_fault,J_right_fault=[],[]
                 
            #layer边缘点上找出符合要求的点
            for pos in self.edge:
                
                if img_tag[pos[0],pos[1]-1]==-1:
                    
                    I_left_fault.append(pos[0])
                    J_left_fault.append(pos[1]-1)
                    
                if img_tag[pos[0],pos[1]+1]==-1:
                    
                    I_right_fault.append(pos[0])
                    J_right_fault.append(pos[1]+1)
                    
            #建立IJ索引        
            I_J_left_fault=dict(zip(I_left_fault,J_left_fault))
            I_J_right_fault=dict(zip(I_right_fault,J_right_fault))  
            
            #增添四个角点
            self.bottom_left=[max(I_left_fault),I_J_left_fault[max(I_left_fault)]]
            self.bottom_right=[max(I_right_fault),I_J_right_fault[max(I_right_fault)]]
            self.top_left=[min(I_left_fault),I_J_left_fault[min(I_left_fault)]]
            self.top_right=[min(I_right_fault),I_J_right_fault[min(I_right_fault)]]   
            
            #直接重新定义
            Angle=[self.bottom_left,self.bottom_right,self.top_left,self.top_right]
     
        if show:
            
            if len(Angle)==4:
                
                #以下部分可写一个检验模块
                for pos in Angle:
#                    print(pos)
                    
                    #方框标记出角点
                    if pos!=None:
                        whj.ShowOnePoint(pos,3,img_rgb)
            
                plt.imshow(img_rgb)       
            
            #角点数量不为4表示失败    
            else:
                print('insufficient angles')
                
                #显示layer
                self.Show(img_rgb,rgb_dict)  
    
    #7.3
            
    """继承fraction的move方法：子类对父类方法的重写，直接修改"""
    def Move(self,i_offset,j_offset):
        
        #更新content
        for pos in self.content:
            pos[0]+=int(i_offset)
            pos[1]+=int(j_offset)
            
        #更新edge
        for pos in self.edge:
            pos[0]+=int(i_offset)
            pos[1]+=int(j_offset)
 
        #更新center
        y=[pos[0] for pos in self.edge]
        x=[pos[1] for pos in self.edge]
        
        #中点坐标
        center_x=(max(x)+min(x))/2
        center_y=(max(y)+min(y))/2
        
        self.center=(center_x,center_y)
        
        #角点坐标
        self.top_left[0]+=int(i_offset)
        self.top_left[1]+=int(j_offset)
        
        self.top_right[0]+=int(i_offset)
        self.top_right[1]+=int(j_offset)
        
        self.bottom_left[0]+=int(i_offset)
        self.bottom_left[1]+=int(j_offset)
        
        self.bottom_right[0]+=int(i_offset)
        self.bottom_right[1]+=int(j_offset)
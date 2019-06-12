# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 17:22:54 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于断层牵引法的平衡恢复对象库
"""

import copy
import numpy as np
import matplotlib.pyplot as plt
import module_fault_motion as whj

#==============================================================================  
#定义像素点类:横纵坐标和值
#==============================================================================  
class pixel:
    def __int__(self,
                xpos=None,
                ypos=None,
                value=None,
                neighbor=None):
        self.xpos=xpos
        self.ypos=ypos
        self.value=value
        self.neighbor=[]
        #需要动态改变的变量不能定义为他的名字！！！
    
    #找到合适的点之后生成他的邻域
    def GenerateNeighbor(self,img_tag):
        
        method=0
        
        #用这种方法快
        if method==0:
            
            self.neighbor=[]    
            
            #逆时针遍历邻域内的点
            neighbordict={0:(0,-1),
                          1:(1,-1),
                          2:(1,0),
                          3:(1,1),
                          4:(0,1),
                          5:(-1,1),
                          6:(-1,0),
                          7:(-1,-1)}
            
            #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
            for item in list(neighbordict.values()):

                #遍历新的坐标
                new_y=self.ypos+item[0]
                new_x=self.xpos+item[1]
                
                if 0<=new_y<np.shape(img_tag)[0] and 0<=new_x<np.shape(img_tag)[1]:
                    
                    self.neighbor.append(img_tag[new_y,new_x])      
                else:
                    self.neighbor.append(None)

        #这种方法慢        
        if method==1:   
              
            #0
            if img_tag[self.ypos,self.xpos-1]:
                
                self.neighbor.append(img_tag[self.ypos,self.xpos-1]) 
            else:
                self.neighbor.append(None)    
            
            #1    
            if img_tag[self.ypos+1,self.xpos-1]:
                
                self.neighbor.append(img_tag[self.ypos+1,self.xpos-1])        
            else:
                self.neighbor.append(None)
            
            #2    
            if img_tag[self.ypos+1,self.xpos]:
                
                self.neighbor.append(img_tag[self.ypos+1,self.xpos])
            else:
                self.neighbor.append(None)
            
            #3    
            if img_tag[self.ypos+1,self.xpos+1]:
                
                self.neighbor.append(img_tag[self.ypos+1,self.xpos+1])  
            else:
                self.neighbor.append(None)
            
            #4    
            if img_tag[self.ypos,self.xpos+1]:
                
                self.neighbor.append(img_tag[self.ypos,self.xpos+1])             
            else:
                self.neighbor.append(None)
            
            #5    
            if img_tag[self.ypos-1,self.xpos+1]:
                
                self.neighbor.append(img_tag[self.ypos-1,self.xpos+1])           
            else:
                self.neighbor.append(None)
            
            #6    
            if img_tag[self.ypos-1,self.xpos]:
                
                self.neighbor.append(img_tag[self.ypos-1,self.xpos])            
            else:
                self.neighbor.append(None)
            
            #7    
            if img_tag[self.ypos-1,self.xpos-1]:
                
                self.neighbor.append(img_tag[self.ypos-1,self.xpos-1])             
            else:
                self.neighbor.append(None)

#==============================================================================  
#建立一个新的数据结构:用于存放追踪出闭合块体的tag和part,
#content像素点的坐标集合
#center像素点的中心坐标
#edge像素点的边缘坐标集合
#==============================================================================  
class fraction:
    def __init__(self,tag=None,
                 part=None,
                 edge=None,
                 content=None,
                 center=None):
        self.tag=tag
        self.part=part
        self.edge=edge    
        self.content=content
        self.center=center
        
    #在图中显示单个fraction的函数 
    def Show(self,img_rgb,rgb_dict,text=False,output=False):
        
        #显示找到的内容         
        background_rgb=img_rgb[0,0]
        img_temp=np.full(np.shape(img_rgb),background_rgb)
            
        #tag,part,content,center 
        tag=self.tag
        part=self.part
        content=self.content
        center=self.center
            
        #着色
        for item in content:
            
            i,j=item[0],item[1]
            img_temp[i,j]=rgb_dict[tag]   
            
        #在图中显示
        plt.figure()
        plt.imshow(img_temp)
    
        if text:
            #annotate函数:s表示输出的文本，
            plt.annotate(s='tag'+' '+str(tag)+' '+'part'+' '+str(part),
                         #xy表示中心点坐标
                         xy=center,
                         #xycoords表示输出类型，默认为'data'
                         xycoords='data',
                         #fontsize字体
                         fontsize=10,
                         #xytext和textcoords='offset points'对于标注位置的描述和x偏差值
                         textcoords='offset points',
                         #4个字符相当于2个fontsize
                         xytext=(-20,0)) 
        if output:          
            return img_temp
     
    #更新中心点坐标
    def UpdateCenter(self):
        
        #更新center
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]
        
        #中点坐标
        center_I=(max(I)+min(I))/2
        center_J=(max(J)+min(J))/2
        
        self.center=(center_I,center_J)
        
    #fraction移动之后，content坐标和center坐标随之改变 
    #edge和content整体坐标增加（i_offset,j_offset）
    def Move(self,i_offset,j_offset):
        
        #更新content
        for pos in self.content:
            pos[0]+=int(i_offset)
            pos[1]+=int(j_offset)
            
        #更新edge
        for pos in self.edge:
            pos[0]+=int(i_offset)
            pos[1]+=int(j_offset)
 
        self.UpdateCenter()
              
    #fraction的像素点集合的上下左右坐标
    def Threshold(self):

        #求Content中坐标的最大值和最小值
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]

        #上下左右
        left,right,bottom,top=min(J),max(J),max(I),min(I)
        
        return left,right,bottom,top
    
    #9.9
    
    #这里的腐蚀和扩张都是基于content做计算
    #腐蚀运算
    def Erode(self):
        
        #逆时针遍历邻域内的点
        #领域核
        neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
        
        #腐蚀操作后的结果
        new_content=[]
        
        for pos in self.content:
            
            #8邻域
            neighbor=[]    
    
            #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
            for item in neighbordict:
                      
                #遍历新的坐标
                new_i=pos[0]+item[0]
                new_j=pos[1]+item[1]
                
                #前提是这个点的位置是有效的
                if [new_i,new_j] in self.content:
                    
                    neighbor.append(True)          
                else:
                    neighbor.append(False)
                    
            #领域值是否都相等        
            if neighbor==len(neighbor)*[True]:
                
                new_content.append(pos)
        
        #重新定义content
        self.content=new_content
        
    #膨胀运算
    def Expand(self):
      
        #逆时针遍历邻域内的点
        #领域核
        neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
        
        #膨胀操作后的结果
        new_content=[]
        
        for pos in self.content:
            
            #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
            for item in neighbordict:
                
                #遍历新的坐标
                new_i=pos[0]+item[0]
                new_j=pos[1]+item[1]
                
                #增加新的点儿
                if [new_i,new_j] not in self.content:
                    
                    new_content.append([new_i,new_j])
                            
        #重新定义content
        self.content+=new_content
        
    #9.10
    
    """运算速度较慢"""
    #n为运算次数
    #结构闭运算
    def Close(self,n):
        
        #先膨胀
        for k in range(n):    
            self.Expand()

        #后侵蚀
        for k in range(n):    
            self.Erode()
            
    #结构开运算
    def Open(self,n):
        
        #先侵蚀
        for k in range(n):    
            self.Erode()
            
        #后膨胀
        for k in range(n):    
            self.Expand()

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
    def __init__(self,tag=None,
                 part=None,
                 edge=None,
                 content=None,
                 center=None,
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
        fraction.__init__(self,tag=None,
                          part=None,
                          edge=None,
                          content=None,
                          center=None)  

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

#==============================================================================  
#定义一个fault类，继承fraction类
#重构属性和继承方法，增加inclination表示倾向，polarity属性表示断层的性质
#==============================================================================  
class fault(fraction):
    
    #先继承,后重构
    def __init__(self,tag=None,
                 part=None,
                 edge=None,
                 content=None,
                 center=None,
                 inclination=None,
                 polarity=None,
                 tilt=None,
                 k=None):  
        
        #继承父类的构造方法
        fraction.__init__(self,tag=None,
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

#==============================================================================  
#定义plate这个类
#top表示即将被剥去的fraction
#others并表示底下的fraction们（list）
#fractions表示plate包含的所有fraction对象
#content表示fractions的坐标集合
#==============================================================================  
class plate:
    def __init__(self,
                 top=None,
                 others=None,
                 fault=None,
                 fractions=None,
                 content=None):
        self.top=top
        self.others=others
        self.fault=fault
        self.fractions=fractions
        self.content=content
        
    #plate初始化
    def Init(self,fractions):
        
        #定义fractions属性
        self.fractions=fractions
        
        #将输入的fractions分开成顶部fraction和底下的fractions 
        #height为fraction的高度
        depth=[]  
        
        for this_fraction in fractions:
            
            this_fraction.UpdateCenter()
            depth.append(this_fraction.center[0])
        
        #建立一个字典表示fraction的纵坐标和fraciton的对应关系
        height_fractions=dict(zip(depth,fractions))
        
        #深度最浅的是top的fraction  
        self.top=height_fractions[min(depth)]
        
        """不对，应该删除所有tag与之相同的fraction，之后遇到问题再改"""  

        #除了top其余的是others
        temp_fractions=copy.copy(fractions)          
        temp_fractions.remove(self.top)  
        
        self.others=temp_fractions  
        
        #定义content属性
        self.content=[] 
        
        #self.content=content[0]+content[1]+...content[n-1]
        for this_fraction in fractions:
            self.content+=this_fraction.content
    
        #初始化fault属性
        self.fault=[]
        
        #加入fault对象们
        for this_fraction in self.fractions:
            
            if isinstance(this_fraction,fault):
                
                self.fault.append(this_fraction)
            
    #显示plate对象
    def Show(self,img_rgb,rgb_dict,text=False,output=False):
        
        whj.ShowFractions(self.fractions,img_rgb,rgb_dict,text,output)   
        
        
    #plate整体移动函数    
    def Move(self,i_offset,j_offset):
               
        #进行移动，调用类方法，并修改所有参数
        for this_fraction in self.fractions:
            this_fraction.Move(i_offset,j_offset)
            
        #根据修改的参数，重新定义plate对象
        self.Init(self.fractions)
    
    #plate的像素点集合的上下左右坐标
    def Threshold(self):
        
        #求content中坐标的最大值和最小值
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]

        #上下左右
        left,right,bottom,top=min(J),max(J),max(I),min(I)
        
        return left,right,bottom,top
    
    #plate对象转化为fractions
    def Tofractions(self):
        
        #将top和others收录进来
        total_fractions=self.others
        total_fractions.append(self.top)
        
        return total_fractions
    
    #9.4
    
    #plate转化为chip对象的函数 
    #which_fault是划分上下盘的fault
    #width是切片宽度
    #Chip_id是Chip的名字
    def ToChip(self,which_fault,img_tag,width,Chip_id):
        
        #获取fault倾角和斜率
        tilt,k=whj.InitTilt(which_fault)
        
    #    print(k)
        
        #分别取layer中的最大值和最小值
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]
        
        #大偏移距(绝对值)
        J_total_offset=(max(I)-min(I))/abs(k)  
        
        #分段有利于提高计算速度：特殊区段
        n_special=int(np.ceil(J_total_offset/width))
        
        #分成n段：四边形角落多出一块
        n=int(np.ceil((max(J)-min(J)+(J_total_offset))/width))
        
#        print(n)
#        print(n_special)
#        print(n-n_special)
#        print(len(which_plate.content))
        
        #plate中的所偶tag
        tags=[this_fraction.tag for this_fraction in self.Tofractions()]
        total_tag=list(set(tags))
        
    #    print(total_tag)
        
        #总chips对象列表
        total_chips=[]
        
        #创建一个表示平行四边形端点的列表
        that_Chip_node_quadrangle=[]
          
        #大平行四边形四个顶点
    #    print(type(I))
    #    print(type(J))
    
        #斜率分类讨论    
        if k>0:   
            pos_A=[min(I),max(J)]
            pos_B=[max(I),max(J)+J_total_offset]
            
        if k<0:
            pos_A=[min(I),max(J)]
            pos_B=[max(I),max(J)-J_total_offset]
            
    #    print(pos_A,pos_B)
    #    print(len(which_plate.content))
        
        for m in range(n,0,-1): 
            
            #创建一个表示平行四边形端点的列表
            that_chips_node_quadrangle=[]
            
            pos_C=[min(I),pos_A[1]-width]
            pos_D=[max(I),pos_B[1]-width]
            
            ABCD=[pos_A,pos_B,pos_C,pos_D]
            
            #在这四个点横纵坐标的最大范围内进行搜索
            I_quadrangle_point=[pos[0] for pos in ABCD]
            J_quadrangle_point=[pos[1] for pos in ABCD]
            
            I_max=max(I_quadrangle_point)
            I_min=min(I_quadrangle_point)   
            J_max=max(J_quadrangle_point)
            J_min=min(J_quadrangle_point)
             
    #        print(I_max,I_min,J_max,J_min)
            
            this_chip=chip()
            
            #初始化
            this_chip.k=k
            this_chip.part=m
            this_chip.tilt=tilt
            this_chip.inclination=which_fault.inclination
            this_chip.content=[]
      
            #填充横向点
            if k>0:    
                for JJ in range(int(np.ceil(J_max)),int(np.ceil(J_total_offset+J_min)),-1):   
                    
                    that_chips_node_quadrangle.append([I_max,JJ-int(np.ceil(J_total_offset))])
                    that_chips_node_quadrangle.append([I_min,JJ])
                
            if k<0:        
                for JJ in range(int(np.ceil(J_max)),int(np.ceil(J_total_offset+J_min)),-1):   
                    
                    that_chips_node_quadrangle.append([I_min,JJ])
                    that_chips_node_quadrangle.append([I_max,JJ+int(np.ceil(J_total_offset))])
                
    #        print(len(node_quadrangle))
            
            #收录which_plate中的点
            for i in range(I_min,I_max+1):
                
                #用斜率联系IJ
                I_offset=i-I_min
                J_offset=I_offset/k
                
                #收录端点
                start=int(np.round(J_max-J_offset-width))
                end=int(np.round(J_max-J_offset))
                
                that_chips_node_quadrangle.append([i,start])
                that_chips_node_quadrangle.append([i,end])
                
                for j in range(end,start,-1):
                    
                    #根据tag值进行收录
                    if img_tag[i,j] in total_tag:   
                        
                        #增加判断条件
                        if [i,j] in self.content:
                            
                            this_chip.content.append([i,j])
            
#            print(len(this_chip.content))     
            
            #计算下一个平行四边形                
            pos_A[1]-=width
            pos_B[1]-=width                                                
            
            #一个chip分成多个chip
            #这一个小四边形中的所有chip
            total_chip=[]
            
            #将this_chip拆成不同tag的多个部分
            for target_tag in total_tag:
                
                that_chip=chip()
                that_chip.tag=target_tag
                that_chip.k=k
                that_chip.part=m
                that_chip.tilt=tilt
                that_chip.inclination=which_fault.inclination
                that_chip.content=[]
                
                for pos in this_chip.content:
                    
                    #根据tag进行划分
                    if img_tag[pos[0],pos[1]]==target_tag:   
                        
                        that_chip.content.append(pos)
                        
#                print(len(that_chip.content))
                      
                #确保that_chip有点东西才添加它
                if that_chip.content!=[]:
                    
                    total_chip.append(that_chip)
                
            #建立新的chips对象
            that_chips=chips()
            
            #初始化
            that_chips.k=k
            that_chips.part=m
            that_chips.tilt=tilt
            that_chips.total_chip=total_chip      
            that_chips.node_quadrangle=that_chips_node_quadrangle
            that_chips.Init() 
            that_chips.need_to_advanced_regularization=False
            
            #特殊处理区段
            if that_chips.part<n_special or that_chips.part>=n-n_special:
                
                #得有点东西吧
#                if that_chips.content!=[] and that_chips.content!=None:
               
                that_chips.need_to_advanced_regularization=True

#                print(that_chips.part)
                    
#            #检验一波
#            if that_chips.top!=None:
#                
#                print(that_chips.top.tag)
            
            #添加至chips列表
            total_chips.append(that_chips)
            that_Chip_node_quadrangle+=that_chips_node_quadrangle
            
        #建立新的Chip对象
        that_Chip=Chip()
        
        #初始化各属性
        that_Chip.id=Chip_id
        that_Chip.k=k
        that_Chip.tilt=tilt
        that_Chip.total_chips=total_chips
        that_Chip.plate=self
        that_Chip.node_quadrangle=that_Chip_node_quadrangle
        that_Chip.Init()
        that_Chip.UpdateID()
        
        return that_Chip
    
#7.4
        
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
            
#7.11

#==============================================================================                 
#定义平行四边形切片
#==============================================================================  
class chip(fraction):
      
    #先继承,后重构
    def __init__(self,id=None,
                 tag=None,
                 part=None,
                 content=None,
                 center=None,
                 inclination=None,
                 tilt=None,
                 k=None):  
        
        #继承父类的构造方法
        fraction.__init__(self,tag=None,
                          part=None,
                          content=None)  
        
        self.inclination=inclination
        self.tilt=tilt
        self.k=k
        self.id=id
        
    #初始化center
    def InitCenter(self):
        
        if self.content!=[]:
            
            I=[pos[0] for pos in self.content]
            J=[pos[1] for pos in self.content]
            
            I_center=(max(I)+min(I))/2
            J_center=(max(J)+min(J))/2
            
            self.center=[I_center,J_center]
        
    #平移chip对象
    def Move(self,i_offset,j_offset):
        
        #更新content
        for pos in self.content:
            
            pos[0]+=int(i_offset)
            pos[1]+=int(j_offset)
            
    #显示chip对象
    def Show(self,img_rgb,rgb_dict,output=False):
        
        #显示找到的内容         
        background_rgb=img_rgb[0,0]
        img_temp=np.full(np.shape(img_rgb),background_rgb)
             
        #着色
        for pos in self.content:
            img_temp[pos[0],pos[1]]=rgb_dict[self.tag]   
            
        #在图中显示
        plt.figure()
        plt.imshow(img_temp)
        
        if output:
            return img_temp
            
"""写一个分tag描绘的函数"""
#==============================================================================  
#total_chip表示chip列表
#total_chip=[chip_1,chip_2,chip_3...]
#node_quadrangle表示小平行四边形的边界点
#regularization表示是否被矫正过
#==============================================================================  
class chips:
    def __init__(self,id=None,
                 total_chip=None,
                 total_tag=None,
                 content=None,
                 center=None,
                 top=None,
                 others=None,
                 node_quadrangle=None,
                 tilt=None,
                 k=None,
                 regularization=None,
                 need_to_advanced_regularization=None):
        
        self.id=id
        self.total_chip=total_chip
        self.total_tag=total_tag
        self.content=content
        self.center=center
        self.top=top
        self.others=others
        self.node_quadrangle=node_quadrangle
        self.tilt=tilt
        self.k=k
        self.regularization=regularization
        self.need_to_advanced_regularization=need_to_advanced_regularization
        
    #初始化
    def Init(self):
         
        #初始化所有tag
        self.total_tag=[this_chip.tag for this_chip in self.total_chip]
        
#        print(len(self.total_chip))     
#        print(self.total_chip[0].tag)
           
        self.content=[]
        
        for this_chip in self.total_chip:
            
            this_chip.InitCenter()
            self.content+=this_chip.content    
                       
#        print(len(self.content))
#        print(len(self.total_chip))
        
        if self.content!=[]:
            
            I=[pos[0] for pos in self.content]
            J=[pos[1] for pos in self.content]
            
            I_center=(max(I)+min(I))/2
            J_center=(max(J)+min(J))/2
            
            self.center=[I_center,J_center]
            
        #total_chip中删除fault，即刻删除tag为-1的chip
        total_chip_temp=[this_chip for this_chip in self.total_chip if this_chip.tag!=-1]
        
        #建立chip和chip的center的索引        
        depth=[]

        for this_chip in total_chip_temp:
            
            #确保中心存在
            if this_chip.center!=None:              
                depth.append(this_chip.center[0])
                    
#                    if this_chip.center==None:
#                        depth.append(None)
        if depth!=[]:
            
            #建立top和others
            others_temp=self.total_chip.copy()
            
            depth_chip=dict(zip(depth,others_temp))
            
            top_temp=depth_chip[min(depth)]
               
#            若这个chip的content不存在，则重新排序
#            while top_temp==None:
#                    
#                depth.remove(min(depth))
#                others_temp.remove(None)
#                
#                depth_chip=dict(zip(depth,others_temp))
#                
#                top_temp=depth_chip[min(depth)]
            
            #正常情况
            self.top=top_temp
            self.others=[this_chip for this_chip in others_temp if this_chip!=top_temp]
            
#            print(self.top.tag)
                
    #移动(I_offset,J_offset)个单位
    def Move(self,I_offset,J_offset):

        #从属的chip移动
        for this_chip in self.total_chip:
            
            this_chip.Move(I_offset,J_offset)
            
        #center更新
        if self.center!=None:
            
            self.center=[self.center[0]+I_offset,self.center[1]+J_offset]
        

    #显示chips对象
    def Show(self,img_rgb,rgb_dict,output=False):
        
        #显示找到的内容         
        background_rgb=img_rgb[0,0]
        img_temp=np.full(np.shape(img_rgb),background_rgb)
             
        #着色
        for this_chip in self.total_chip:
            
            for pos in this_chip.content:       
               
                img_temp[pos[0],pos[1]]=rgb_dict[this_chip.tag]   
            
        #在图中显示
        plt.figure()
        plt.imshow(img_temp)
        
        if output:
           
            return img_temp      
        
#==============================================================================       
#建立Chip列表
#total_chips=[chips_1,chips_2,chips_3...]
#plate是Chip对应的plate对象
#node_quadrangle表示小平行四边形chips的边界点的集合
#regularization表示是否被矫正过
#fault_content表示tag为fault对象的点的集合
#==============================================================================  
"""增加top和others对象？"""
class Chip:
    def __init__(self,id=None,  
                 total_chips=None,
                 total_tag=None,
                 content=None,
                 center=None,
                 plate=None,
                 node_quadrangle=None,
                 top=None,
                 others=None,
                 fault=None,
                 fault_content=None,
                 tilt=None,
                 k=None,
                 regularization=None):
        
        self.id=id
        self.total_chips=total_chips  
        self.total_tag=total_tag
        self.content=content
        self.center=center
        self.plate=plate
        self.node_quadrangle=node_quadrangle
        self.top=top
        self.others=others
        self.fault=fault
        self.fault_content=fault_content
        self.tilt=tilt
        self.k=k
        self.regularization=regularization
        
    #初始化
    def Init(self):
        
        self.content=[]
        self.total_tag=[]
        
        #初始化Chip的点坐标content
        for this_chips in self.total_chips:
            
            this_chips.Init()
            self.content+=this_chips.content
            
            #初始化Chip包含的所有tag
            for this_chip in this_chips.total_chip:
                
                if this_chip.tag not in self.total_tag:
                    
                    self.total_tag.append(this_chip.tag)
        
        #初始化center
        if self.content!=[]:
            
            I=[pos[0] for pos in self.content]
            J=[pos[1] for pos in self.content]
            
            I_center=(max(I)+min(I))/2
            J_center=(max(J)+min(J))/2
            
            self.center=[I_center,J_center]
            
        """"""
        #初始化top
        self.UpdateTop()
        
        #tag为-1的对象
        #暂时不能将其作为fraction对象
        self.fault_content=[]
        
        #先将fault存为一个大型的content集合，然后膨胀后再对其进行初始化
        
        for this_chips in self.total_chips:

            for this_chip in this_chips.total_chip:
                
                for pos in this_chip.content:
                
                    if this_chip.tag==-1:
                        
                        self.fault_content.append(pos)
        
    #平移一定的距离
    def Move(self,i_offset,j_offset):  
        
        #移动content
        for pos in self.content:
            
            pos[0]+=i_offset
            pos[1]+=j_offset
            
        #移动边框
        for pos in self.node_quadrangle:
            
            pos[0]+=i_offset
            pos[1]+=j_offset
            
        #center更新
        if self.center!=None:
            
            self.center=[self.center[0]+i_offset,self.center[1]+j_offset]
        
    #移动至pos_P的某一侧
    def MoveTo(self,pos_P,side):
        
        self.Init()
        
        #分别计算I,J方向上的移动距离    
        #J_offset是整个Chip统一的
        
#        print(len(self.content))
        
        J_chips=[pos[1] for pos in self.content]

#        print(len(J_chips))        
        
        if side=='left':
            J_offset=pos_P[1]-max(J_chips)-1
        
        if side=='right':
            J_offset=pos_P[1]-min(J_chips)+1
            
        #Chip中的每个chips纵向移动分量不一    
        for this_chips in self.total_chips:

            I_chips=[]
            
            for pos in this_chips.content:
                
                if pos in self.plate.top.content:
                    
                    I_chips.append(pos[0])
                    
            #确保集合非空
            if I_chips!=[]:

                I_offset=pos_P[0]-min(I_chips)
                
                this_chips.Move(I_offset,J_offset)
            
    #显示Chip对象
    def Show(self,img_rgb,rgb_dict,grid='off'):
        
        #显示找到的内容         
        background_rgb=img_rgb[0,0]
        img_temp=np.full(np.shape(img_rgb),background_rgb)
             
        #Chip主体着色
        for this_chips in self.total_chips:
            for this_chip in this_chips.total_chip:
                for pos in this_chip.content:       
                    img_temp[pos[0],pos[1]]=rgb_dict[this_chip.tag]   
        
        #是否存在四边形边框            
        if grid=='on':

            #平行四边形边框
            for pos in self.node_quadrangle:
                img_temp[pos[0],pos[1]]=np.array([0,0,0]) 
            
        #在图中显示
        plt.figure()
        plt.imshow(img_temp)
          
    #更新Chip的id函数
    def UpdateID(self):
        
        #初始化哟
        chips_id=1
        
        #逐层更新
        for this_chips in self.total_chips:
            
            this_chips.id=self.id+'-'+str(chips_id)   
            chips_id+=1
        
#            print(this_chips.id)
            
            #更新chip的id
            for this_chip in this_chips.total_chip:
                
                this_chip.id=this_chips.id+'|'+str(this_chip.tag)
            
#                print(this_chip.id)
      
    #9.4
          
    #正则化
    def Regularize(self,adjustment=True):
        
    #    print(which_Chip.id)
    #    print(which_Chip.top.tag)
    #    print(which_Chip.total_tag)  
           
        #8.16
     
        #通过need_to_advanced_regularization参数计算n_special
        id_list_to_calculate_n_special=[]
        
        for this_chips in self.total_chips:
            
            if this_chips.need_to_advanced_regularization:
                
                id_list_to_calculate_n_special.append(int(this_chips.id.split('-')[1]))
    
#        print(id_list_to_calculate_n_special)  
        
        #8.17
        
        #左区间的起点和终点
        #虽然经过了初始化的处理，但是这几个节点还是需要计算的
        left_external=id_list_to_calculate_n_special[0]
        
        #计算n_special之路
        left_internal=id_list_to_calculate_n_special[0]
                
        for k in range(1,len(id_list_to_calculate_n_special),+1):    
            
#            print(k)
            
            #判断是否连续
            if id_list_to_calculate_n_special[k-1]==id_list_to_calculate_n_special[k]-1:               
               
                left_internal+=1
            
            #若这种连续中止了
            else:
                break
        
        #右区间的起点和终点
        
        right_external=id_list_to_calculate_n_special[-1]
        right_internal=id_list_to_calculate_n_special[-1]
        
        for k in range(len(id_list_to_calculate_n_special)-1,0,-1): 
            
#            print(k)
            
            #判断是否连续
            if id_list_to_calculate_n_special[k-1]==id_list_to_calculate_n_special[k]-1:               
                
                right_internal-=1
                
            #若这种连续中止了
            else:
                break
     
#        print(left_external,left_internal)
#        print(right_external,right_internal)
        
        """第一轮正则化"""
        
        print('')
        
        for this_id in range(left_internal,right_internal):
            
            whj.PreRegularization(self,this_id)
         
        print('......')    
        print('the end of round 1')
        
        """第二轮正则化"""    
    
        print('')
        
        #分段函数,且从某一头取滑动点集
        #分组调试

        #中点
        medium=len(self.total_chips)/2
        
        #左段 
        if medium>=left_internal>=left_external:

            for this_id in range(left_internal,left_external-1,-1):
                
#                print('left')
                
                whj.SubRegularization(self,this_id,'right',adjustment)
            
        #右段    
        if medium<=right_internal<=right_external:
            
            for this_id in range(right_internal,right_external+1,+1):
                
#                print('right')
                
                whj.SubRegularization(self,this_id,'left',adjustment)    
        
        """有问题"""
        #中段
#        for this_id in range(left_internal,right_internal):
#            
#            whj.SubRegularization(self,this_id,'middle',adjustment)
    
        print('......')    
        print('the end of round 2')  
         
#9.5
    
    #更新Chip的top,也可作初始化
    def UpdateTop(self):
    
#        print(which_Chip.total_tag)
        
        total_tag=copy.deepcopy(self.total_tag)
        
        #top不可以是fault
        if -1 in total_tag:
            total_tag.remove(-1)
        
        #所有tag的高度
        total_tag_top=[]
        
        #所有tag的fraction
        total_tag_fraction=[]
        
        for this_tag in total_tag:
            
            this_tag_fraction=fraction()
            this_tag_content=[]
            
            for this_chips in self.total_chips:
    
                for this_chip in this_chips.total_chip:
                    
                    for pos in this_chip.content:
                    
                        if this_tag==this_chip.tag:
                            
                            this_tag_content.append(pos)
                            
            #I坐标取平均，求最小值                
            I_this_tag=[pos[0] for pos in this_tag_content]
            top_I_this_tag=np.mean(I_this_tag)   
            
            this_tag_fraction.content=this_tag_content
            this_tag_fraction.tag=this_tag
            
            #上车上车
            total_tag_top.append(top_I_this_tag)
            total_tag_fraction.append(this_tag_fraction)
                
        #平均I与total_tag的索引
        map_top_total_tag=dict(zip(total_tag_top,total_tag))
        
        #total_tag和content的索引
        map_total_tag_fraction=dict(zip(total_tag,total_tag_fraction))  
              
        #不加这一限制条件说明没有top了
        if total_tag_top!=[]:
            
            #求目标tag值
            target_tag=map_top_total_tag[min(total_tag_top)]   
            
    #        print(target_tag)
            
            #更新top
            top_content=[]
            
            for this_chips in self.total_chips:
                
                for this_chip in this_chips.total_chip:
                    
                    if this_chip.tag==target_tag:
                        
                        top_content+=this_chip.content
            
            #定义top
            self.top=fraction()
            self.top.content=top_content
            self.top.tag=target_tag
            
            #移除top
            del map_total_tag_fraction[map_top_total_tag[min(total_tag_top)]]
        
            #定义pthers
            self.others=list(map_total_tag_fraction.values())
        
        #检验模块
#        print(self.top.tag)
#        
#        for this_fraction in self.others:
#            print(this_fraction.tag)
     
    #将Chip转化为plate
    def ToPlate(self):
        
        pass
    
"""中期后的工作"""

#建立erect,erects,Erect对象解决尖灭问题
class erect(chip):
    
    def __Init__(self,id=None):
        
        #继承chip类的构造方法
        chip.__init__(self,tag=None,
                          part=None,
                          content=None)
  
class erects(chips):
    pass
                
class Erect(Chip):
    pass

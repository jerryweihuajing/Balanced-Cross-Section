# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 19:16:08 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-fraction
"""

import copy as cp
import numpy as np
import matplotlib.pyplot as plt

from Module import Display as Dis

#==============================================================================  
#建立一个新的数据结构:用于存放追踪出闭合块体的tag和part,
#content像素点的坐标集合
#center像素点的中心坐标
#edge像素点的边缘坐标集合
#==============================================================================  
class fraction:
    def __init__(self,id=None,
                 tag=None,
                 part=None,
                 area=None,
                 length=None,
                 thickness=None,
                 edge=None,
                 content=None,
                 center=None,
                 corners=None):
        self.id=id
        self.tag=tag
        self.part=part
        self.area=area
        self.edge=edge    
        self.content=content
        self.center=center
        self.thickness=thickness
        self.length=length
        self.corners=corners
    
    #初始化面积
    def InitArea(self):
        
        self.area=len(self.content)
     
    #初始化id
    def InitId(self):
        
#        print(str(self.tag),str(self.part))

        #更新id哦
        self.id=str(self.tag)+'_'+str(self.part)
   
#        print(self.id)
    
    #初始化中点
    def InitCenter(self):
        
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]
        
        #重心
        center_I=np.mean(I)
        center_J=np.mean(J)
        
        self.center=(center_I,center_J)
        
    #在图中显示单个fraction的函数 
    def Show(self,
             img_rgb,
             rgb_dict,
             text=False,
             axis=True,
             output=False):
        
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
        #是否显示坐标轴
        if not axis:
        
            plt.axis('off')
        
        #是否输出矩阵
        if output:   
            
            return img_temp
    
    #显示fraction对象的边界点
    def ShowEdge(self,img_rgb,axis=True):
        
        #对所有的边界点，赋予全0的rgb值
        for pos in self.edge:
            
            img_rgb[pos[0],pos[1]]=np.array([0,0,0])
            
        plt.imshow(img_rgb)   
        
        #是否显示坐标轴
        if axis:
            
            plt.axis('off') 
            
    #更新中心点坐标
    def UpdateCenter(self):
        
        #更新center
        I=[pos[0] for pos in self.content]
        J=[pos[1] for pos in self.content]
        
        #重心
        center_I=np.mean(I)
        center_J=np.mean(J)
        
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
      
    #3.7
    #先根据content更新edge   
    #测试腐蚀方法可不可行
    def UpdateEdge(self):
        
        #腐蚀前的content
        content_A=cp.deepcopy(self.content)
        
        #腐蚀一下
        self.Erode()
        
        #腐蚀后的content
        content_B=cp.deepcopy(self.content)
        
        #两个集合相减得到新的边缘
        edge_new=[]
        
        #相减运算
        #list不可hash，只能暴力检索咯
        for this_pos in content_A:
            
            if this_pos not in content_B:
                
                edge_new.append(this_pos)
                
        self.edge=edge_new

    #更新一切的函数
    def UpdateAll(self):
        
        self.InitArea()
        self.UpdateCenter()
        self.UpdateEdge()
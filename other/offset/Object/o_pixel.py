# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 21:21:27 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复对象库-pixel
"""

import numpy as np

#==============================================================================  
#定义像素点类:横纵坐标和值
#neighbor表示邻域里的8个像素点点
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
                
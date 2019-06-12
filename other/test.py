# -*- coding: utf-8 -*-
"""
Created on Wed May 23 21:40:02 2018

@author: whj
"""

import numpy as np
import matplotlib.pyplot as plt

#a=np.full((3,3,3),np.array([2,2,3]))
#
##求符合条件的元素数量
#b=len(a[list(a)==np.array([2,2,3])])/np.shape(a)[-1]
#
#1
#595 597
#597 600
#631
#252 252
#252 261

#b=a.copy()
#a[0,:]=1
#
#print(a)
#print(b)

##试验矩阵        
#a=np.full((4,4),-1)
#a[0,0],a[0,3],a[1,0],a[3,0],a[3,3]=1,1,1,1,1
#img_tag=a

#n=pixel()
#n.xpos=0
#n.ypos=0
#n.GenerateNeighbor(a)
#
###试验矩阵 2
##b=np.full((5,5),1)
##
##b[1,1],b[1,2],b[2,2],b[3,1],b[3,3]=-1,-1,-1,-1,-1
##
##img_tag=b

#
#import module_fault_motion as whj
#
#a=whj.fault()
#
#a.tag=1
#
#
#print(a.tag)

#img=np.random.rand(10,10)
#img[2:7,2:7]=(5+np.random.rand(5,5))
#
#
#Iy=np.gradient(img,axis=0)
#Ix=np.gradient(img,axis=1)
#
#plt.figure()
#plt.imshow(img) 

#plt.figure()
#plt.imshow(Iy) 
#
#plt.figure()
#plt.imshow(Ix) 

#拉平
#Ix=Ix.flatten()
#Iy=Iy.flatten()

#显示散点图
#plt.figure()
#plt.scatter(Ix,Iy,linewidths=1)
#plt.axis('equal')

#权重矩阵
#w=np.full((3,3),0.5)
#w[1,1]=1
#w[0,-1],w[0,0],w[-1,-1],w[-1,0]=0.25,0.25,0.25,0.25


#a=np.array([[1,2],[2,3]])
#b=np.array([[1,1],[2,2]])
#
#print(a*b)
#
##np.dot别乱用
#print(np.dot(a,b))
#

#(x,y)视为起点
#(x,y)点移动u,v

#def Explode(Ix,Iy,w):
#    
#    #建立结果矩阵
#    E=np.zeros((np.shape(Ix)[1],np.shape(Iy)[0]))
#        
#    for u in range(1,9):
#        for v in range(1,9):
#            
#            Ix_window=Ix[u-1:u+2,v-1:v+2]
#            Iy_window=Iy[u-1:u+2,v-1:v+2]
#            
#            E[u,v]=np.sum(((u*Ix_window+v*Iy_window)**2)*w)
#   
#    return E
#    
#plt.figure()
#
#img_E=Explode(Ix,Iy,w)
#
#plt.imshow(img_E) 

      


#腐蚀
def Erosion(img,target):
    
    new_img=np.zeros(np.shape(img))
    
    #逆时针遍历邻域内的点
    #领域核
    neighbordict={0:(0,-1),
                  1:(1,-1),
                  2:(1,0),
                  3:(1,1),
                  4:(0,1),
                  5:(-1,1),
                  6:(-1,0),
                  7:(-1,-1)}
    
    for i in range(np.shape(img)[0]):
        for j in range(np.shape(img)[1]):  
            
            #仅作用于前景
            if img[i,j]==target:
                    
                neighbor=[]    
        
                #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
                for item in list(neighbordict.values()):
                    
                    #遍历新的坐标
                    new_i=i+item[0]
                    new_j=j+item[1]
                    
                    if 0<=new_i<np.shape(img)[0] and 0<=new_j<np.shape(img)[1]:
                        neighbor.append(img[new_i,new_j])
                    else:
                        neighbor.append(None)
                        
                #领域值是否都相等        
                if neighbor==[img[i,j]]*8:
                    new_img[i,j]=img[i,j]
    
    return new_img
     

#膨胀运算
#target为前景的rgb或灰度值
def Expand(img,target):
    
    new_img=np.zeros(np.shape(img))     
    
    #逆时针遍历邻域内的点
    #领域核
    neighbordict={0:(0,-1),
                  1:(1,-1),
                  2:(1,0),
                  3:(1,1),
                  4:(0,1),
                  5:(-1,1),
                  6:(-1,0),
                  7:(-1,-1)}
    
    for i in range(np.shape(img)[0]):
        for j in range(np.shape(img)[1]):  
          
            #仅作用于前景
            if img[i,j]==target:
                new_img[i,j]=img[i,j]
                
                #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
                for item in list(neighbordict.values()):
                    
                    #遍历新的坐标
                    new_i=i+item[0]
                    new_j=j+item[1]
                    
                    #重复赋值                
                    if 0<=new_i<np.shape(img)[0] and 0<=new_j<np.shape(img)[1]:
                        new_img[new_i,new_j]=img[i,j]

    return new_img
    
    
##初始化图像
#img=np.zeros((10,10))
#
##前景rgb灰度值
#target=1
#
##定义前景
#img[3:8,3:8]=target
#
#plt.figure() 
#plt.imshow(img-Erosion(img,1))
#
#plt.figure() 
#plt.imshow(Expand(img,1)-img)

import module_fault_motion as whj

#输入图片的路径
path=r'C:\Users\whj\Desktop\Spyder\平衡恢复\例\opne.bmp'

#导入图片，生成rgb数组
img1=whj.LoadImage(path)
img2=whj.LoadImage(path)

target=23

n=8

for k in range(n):
    img1=Erosion(img1,target)

for k in range(n):    
    img1=Expand(img1,target)
    
plt.figure()
plt.imshow(img1)

for k in range(n):    
    img2=Expand(img2,target)
    
for k in range(n):
    img2=Erosion(img2,target)

plt.figure()
plt.imshow(img2)

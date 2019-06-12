# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 16:05:41 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于位移量守恒的平衡恢复函数库-Target
"""

import copy as cp
import numpy as np

#跨文件夹导入包
import sys
sys.path.append('.')

from Object.o_pixel import pixel
from Object.o_layer import layer
from Object.o_fault import fault

import Module.Dictionary as Dict  
import Module.Display as Dis

"""
填充方法：
1 填充边界内的点，向内侵蚀
2 阿华算法：IJ交织（已改进，解决了拾取本不该属于集合里的点的问题）
"""
"""算的太慢!!!,只能缩小尺寸"""  
#==============================================================================  
#提取出tag值的像素点坐标的集合
def PickSomething(img_rgb,
                  img_tag,
                  this_tag,
                  rgb_dict,
                  show=False,
                  axis=True,
                  text=False,
                  output=False):
    
    #content_sum=Content[0]+Content[1]+...
    content_sum=[]   
    
    #method=1代表方法1，method=2代表方法2
    method=2    
    
    #复制生成临时的img_tag,用于标记已上色的像素点
    temp_img_tag=cp.deepcopy(img_tag)   
    
    #是否继续遍历的标志   
    content_flag=this_tag in temp_img_tag  
    
    #块体tag a part b的重心坐标
    Center={}      
    
    #Center字典增加一个新的tag列表
    Center[this_tag]=[]  
    
    #that_fractions是生成的fraction对象的集合
    that_fractions=[]   
    
#    #已知对象数量时可以这么干
#    number=3
#    for kk in range(number):
    
    """1 内部膨胀的方法增加像素点"""  
    if method==1: 
        
        #以下部分进行循环
        while content_flag: 
            
            #fault像素点集合的生成
            content=[]
            
            #寻找第一个特征值值点
            fault_edge,content_flag=Find1stPixel(this_tag,img_tag,content_sum)   
            
            #追踪fault的边界
            fault_edge=EdgeTracing(this_tag,fault_edge,img_tag)
            
            #内部膨胀的方法增加像素点    
            neighbordict={0:(0,-1),
                          1:(1,-1),
                          2:(1,0),
                          3:(1,1),
                          4:(0,1),
                          5:(-1,1),
                          6:(-1,0),
                          7:(-1,-1)}
            
            #将边界存入fault列表当中
            new_edge=fault_edge
            content+=new_edge
    
            #只要每一轮添加的点的数量不为0就执行循环
            while len(new_edge):  
                
                #上一轮添加的点
                last_edge=new_edge
                
                #这一轮新添加的点坐标的列表
                new_edge=[]
                
                for k in range(len(last_edge)):
                    
                    #建立新的pixel对象
                    temp_pixel=pixel()
                    temp_pixel.ypos=last_edge[k][0]
                    temp_pixel.xpos=last_edge[k][1]  
                    
                    #生成邻居列表,起始迭代邻居的索引
                    temp_pixel.GenerateNeighbor(img_tag)   
                    
                    for i in range(len(neighbordict)): 
                        
                        #判断标签为tag
                        if temp_pixel.neighbor[i]==this_tag:
                            
                            #邻居的坐标
                            new_y=temp_pixel.ypos+neighbordict[i][0]
                            new_x=temp_pixel.xpos+neighbordict[i][1]
                            
                            pos=[new_y,new_x]
                            
                            #新的点在不在fault列表内
                            if pos not in new_edge:
                                
                                new_edge.append(pos)  
                                
                #将新捕捉的点存入fault列表当中                
                content+=new_edge            
  
    """2 阿华法增加像素点"""
    if method==2:
        
        #以下部分进行循环
        while content_flag:  
            
#        已知个数的情况
#        number=2
#        for kk in range(number):  
            
            #装逼用 
            print('')
            print('...')
            print('......')
            print('.........')
            print('tag',this_tag,'part',len(that_fractions),':')
            
            #寻找第一个特征值值点
            edge=Find1stPixel(this_tag,img_tag,content_sum)

            #追踪content的边界
            edge=EdgeTracing(this_tag,edge,img_tag)
            
            #this_fraction表示正在处理的fraction
            
            #如果tag=-1,则fraction为fault
            if this_tag==-1:
                
                this_fraction=fault()  
            else:
                this_fraction=layer()     
            
            #对tag属性赋值
            this_fraction.tag=this_tag  
       
            #给part属性赋值
            this_fraction.part=len(that_fractions)
            
            #给edge属性赋值
            this_fraction.edge=edge
               
            #求对象的范围矩阵
            #left right bottom top 这几个重要的参数
            I=list(set([pos[0] for pos in edge]))
            J=list(set([pos[1] for pos in edge]))
            
            #增加边缘
#            for item in edge:       
#               
#                if item[0] not in I: 
#                    
#                    I.append(item[0])
#                    
#                if item[1] not in J:
#                    
#                    J.append(item[1])
                    
            #初始生成的I,J不是按顺序的，需要对其进行排序
            I.sort()
            J.sort() 
               
            left,right=min(J),max(J)
            bottom,top=min(I),max(I)
            
            #获取块体的中点
            center_x=np.mean(J)
            center_y=np.mean(I)
            
            #标注的坐标，即块体Content[part]的中点
            center=(center_x,center_y)
            
            #对center属性赋值
            this_fraction.center=center
                        
            Center[this_tag].append(center)
            
            #建立某特殊的数据结构，用于存放像素点的行对应的列
            row_column=[]
            column_row=[]
            
            """is和==不一样"""         
            for i in range(top-bottom+1):
                
                #行对应的列的列表
                column=[]
                
                for item in edge:
                   
                    if item[0]==I[i]:
                        
                        column.append(item[1])
                
                column.sort()
                
                #列表添加至大列表当中
                row_column.append(column)
        
            for j in range(right-left+1):
                
                #列对应的行的列表
                row=[]
                
                for item in edge:
                    
                    if item[1]==J[j]:
                        
                        row.append(item[0])
                
                row.sort()
                
                #列表添加至大列表当中
                column_row.append(row)   
            
            #检验这两个数组的正确性
            sum_i,sum_j=0,0
            
            for item in row_column:
                
                sum_j+=len(item)
                
            for item in column_row:
                
                sum_i+=len(item)
            
            #设置验证门槛
            #J
            if sum_j==len(edge):
               
                print('row_column is OK')
                flag_j=True
                
            #I
            if sum_i==len(edge):
               
                print('column_row is OK')
                flag_i=True
                
            #IJ
            if sum_j==sum_i:
                
                if flag_i and flag_j:
                    
                    flag=True
                    
            if flag is True:
                """
                注意：
                过一个点做垂线和水平线可能会碰到交点是三个以上，如果其中有轮廓线的切点，就会出现判断失误 
                
                设置节点：
                每个节点两段点之间遍历，若符合tag要求即加入集合当中
                """     
                #在row_column和column_row当中建立合适的节点，将相邻的像素点用其中头尾节点来表示   
               
                #content像素点集合
                content=[]   
                   
                #row_column               
                row_column_node=[] 
                for r in range(len(row_column)):

                    #要删除的列表
                    column_to_delete=[]
                        
                    if len(row_column[r])>2:
                        
                        #元素数量大于2时才成立                      
                        for c in range(1,len(row_column[r])-1):               

                            bool_former=(row_column[r][c+1]-row_column[r][c]==1)        
                            bool_latter=(row_column[r][c]-row_column[r][c-1]==1)
                                  
                            #直接删除中间元素        
                            if bool_former and bool_latter:
                                
                                #建立需要删除元素的列表
                                column_to_delete.append(row_column[r][c])
      
                    #要增加的节点列表
                    column_node=[]
                    
                    """若不加这步骤，则没法把孤苦伶点的点收录进来"""
                    if len(row_column[r])==1:
                       
                        column_node=row_column[r]*2
                        
                    else:   
                        #将某些元素删除
                        
                        for item in row_column[r]:
                            
                            if item not in column_to_delete:
                                
                                column_node.append(item)

                    row_column_node.append(column_node)

                #修复方法
                fix=False
                
                #确认是否存在两个以下的节点
                if fix:                      
                   
                    for item in row_column_node:
                       
                        if len(item)!=2:
                           
                            print(item)                       
                
                #进行轮廓内部填充 
                fashion='new'
                
                #老办法，用于检验，在不特殊的情况下能得到正确答案
                #如果只有两个节点时直接用老方法填充，比较快
                if fashion=='old':
                    
                    for i in range(top-bottom+1): 
                        
                        for j in range(right-left+1):
                            
                            #用abcd代替更简便
                            a,b=min(row_column[i]),max(row_column[i])
                            c,d=min(column_row[j]),max(column_row[j])
                            
                            #绝对坐标
                            absolute_i=bottom+i
                            absolute_j=left+j
                            
                            #判断是否在区域内
                            if a<=absolute_j<=b and c<=absolute_i<=d:
                                
                                pos=[absolute_i,absolute_j]
                                content.append(pos) 
                                
                                #对上色过的像素点赋予tag=0
                                temp_img_tag[int(pos[0]),int(pos[1])]=0  
                                
                #适用于所有情况                
                if fashion=='new':
                    
                    for i in range(top-bottom+1):  
                        
                        #行坐标欸
                        row=bottom+i
    
                        #列坐标                 
                        for ii in range(len(row_column_node[i])-1):
                            
                            #这个列坐标区间内的tag进行判断
                            #column=(row_column[i][ii],row_column[i][ii+1])
                            
                            start_j=row_column_node[i][ii]
                            stop_j=row_column_node[i][ii+1]
                            
                            #如果区间内全是符合tag的点，则加如集合
                            
                            """用向量进行赋值速度快"""
                            if list(img_tag[row,start_j:stop_j])==[this_tag]*(stop_j-start_j):
                                
                                #对上色过的像素点赋予tag
                                temp_img_tag[row,start_j:stop_j]=0
    
                                for column in range(start_j,stop_j):
                                    
                                    pos=[row,column]
                                    
                                    if pos not in content:
                                        content.append(pos) 
                 
                            #确保边缘被收录
                            for column in row_column_node[i]: 
                                
                                pos=[row,column]
                            
                                if pos not in content:
                                   
                                    content.append(pos) 
                                    
                                    #对上色过的像素点赋予tag=0
                                    temp_img_tag[int(pos[0]),int(pos[1])]=0
                
                #复制结果
                content_row_column=cp.deepcopy(content)
 
                #重新定义content像素点集合
                content=[] 
                
                #column_row               
                column_row_node=[] 
                
                for c in range(len(column_row)):
                    
                    #要删除的列表
                    row_to_delete=[]
                      
                    if len(column_row[c])>2:
                        
                        #元素数量大于2时才成立  
                        for r in range(1,len(column_row[c])-1):               

                            bool_former=(column_row[c][r+1]-column_row[c][r]==1)        
                            bool_latter=(column_row[c][r]-column_row[c][r-1]==1)
                                  
                            #直接删除中间元素                                
                            if bool_former and bool_latter:
                                
                                #建立需要删除元素的列表
                                row_to_delete.append(column_row[c][r])
      
                    #要增加的节点列表
                    row_node=[]
                    
                    #把孤苦伶点的点收录进来
                    if len(column_row[c])==1:
                        
                        row_node=column_row[c]*2
                        
                    else:   
                        
                        #将某些元素删除                      
                        for item in column_row[c]:
                            
                            if item not in row_to_delete:
                               
                                row_node.append(item)

                    column_row_node.append(row_node)
                
                #进行轮廓内部填充 
                #适用于所有情况
                for j in range(right-left+1):  
                    
                    #行坐标欸
                    column=left+j

                    #列坐标                 
                    for jj in range(len(column_row_node[j])-1):
                        
                        #这个列坐标区间内的tag进行判断
                        #row=(column_row[j][jj],column_row[j][jj+1])
                        
                        start_i=column_row_node[j][jj]
                        stop_i=column_row_node[j][jj+1]
                        
                        #如果区间内全是符合tag的点，则加如集合
                        
                        """用向量进行赋值速度快"""
                        if list(img_tag[start_i:stop_i,column])==[this_tag]*(stop_i-start_i):
                            
                            #对上色过的像素点赋予tag
                            temp_img_tag[start_i:stop_i,column]=0

                            for row in range(start_i,stop_i):
                                
                                pos=[row,column]
                                
                                if pos not in content:
                                   
                                    content.append(pos) 
             
                        #确保边缘被收录
                        for row in column_row_node[j]: 
                            
                            pos=[row,column]
                        
                            if pos not in content:
                                
                                content.append(pos) 
                                
                                #对上色过的像素点赋予tag=0
                                temp_img_tag[int(pos[0]),int(pos[1])]=0  
                                
                #复制结果
                content_column_row=cp.deepcopy(content)
                
                #互相验证两种收集模式的结果：比较两集合结果是否相等       
                verification=True             
                
                for item in content_column_row:
                    
                    if item not in content_row_column:
                        
                        verification=False
                       
                if verification:     
                   
                    #判断结果的count
                    count_for_judge=0
                    
                    #判断content是否包含了edge
                    for item in edge:
                        
                        if item in content:
                           
                            count_for_judge+=1
                    
                    #判断列表长度是否相等        
                    if count_for_judge==len(edge):
                        
                        print('content includes edge')
                    
                    #对content属性赋值
                    this_fraction.content=content
                    
#                    print(len(this_fraction.content))
                    
                    #初始化id
                    this_fraction.InitId()
                    this_fraction.InitCenter()
                    
                    #content_sum=Content[0]+Content[1]+...
                    content_sum+=content
                    
                    #Content[0],Content[1]是每个块体像素点的集合
                    that_fractions.append(this_fraction)
                                             
                    #判断循环是否需要中止：1和2代表不同方法       
                    method_for_stop=2
                    
                    """1 判断条件为新的img_tag是否还存在标签值"""
                    #这种方法要特别久 
                    if method_for_stop==1:     
                        
                        #符合条件的tag不在content_sum中的数量
                        count_for_stop=0
                        
                        for i in range(np.shape(img_tag)[0]):
                            
                            for j in range(np.shape(img_tag)[1]):
                                
                                if img_tag[i,j]==this_tag:
                                    
                                    pos=[i,j]
                                    if pos not in content_sum:
                                       
                                        count_for_stop+=1
                                    
                        #循环结束的判断条件               
                        if count_for_stop==0:
                            
                            #继续遍历的标志关闭
                            content_flag=False
                                
                    """2 判断条件为temp_img_tag是否存在tag"""  
                    if method_for_stop==2: 
                        
                        content_flag=this_tag in temp_img_tag
                    
                        if content_flag:
                            
                            print('picking is not complete')
                            
                        #判断类型并输出
                        else:                      
                           
                            if isinstance(this_fraction,fault):
                                
                                name='fault'
                                
                            if isinstance(this_fraction,layer):
                                
                                name='layer'    
                            
                            print(name,'id:',this_fraction.id)
                            print('everything is OK')
        
    #检查'everything is OK'是否成立
    check=False
    
    if check:   
        
        count=0      
        
        for i in range(np.shape(temp_img_tag)[0]):
            
            for j in range(np.shape(temp_img_tag)[1]):
                
                if temp_img_tag[i,j]==this_tag:
                    
                    count+=1   
                    
        print(count) 
        
    #显示一下Content的位置
    if show:
        
        Dis.ShowFractions(that_fractions,img_rgb,rgb_dict,axis,text,output)
              
    return that_fractions

#==============================================================================     
"""
连通成分标记：基于链码的边界追踪算法
从左往右，从上到下遍历所有像素点
每个点的[i,j-1]方向为下标0的邻域，顺时针每个点的下标依次为0-7
循环遍历，直到起点与终点的坐标相同
"""  
def Find1stPixel(tag,img_tag,content):
    
    #fault边缘点坐标集合
    edge=[]   
    
    #开启标志
    flag=True  
    
    #寻找值为tag的点的集合 
    for j in range(np.shape(img_tag)[1]):
        
        if flag==False:
            
            break  
        
        for i in range(np.shape(img_tag)[0]):   
            
            if img_tag[i,j]==tag:
                
                #第一个tag点的位置
                pos=[i,j] 
                
                #判断新的的点是否存在与fault矩阵当中
                if pos not in content:
                    
                    edge.append(pos)
                    flag=False
                    
                    break    
    return edge

"""
以下情况需要特殊处理：
1 S[k-1]邻域内的第一个点已在边缘集合当中，则访问下一个点 OK
2 S[k]邻域内只有一个边缘点，即上一个点S[k-1],则访问S[k-1]邻域内下一个点 OK  
3 S[K]从上一个目标点是S[k-1]逆时针进行遍历 OK
""" 
#============================================================================== 
#寻找自己的第一个符合要求的邻居像素,要追踪的像素值为tag
#第一个满足tag的pixel对象
def Find1stNeighbor(tag,flag_stop,edge,img_tag,index):
    
    #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
    #邻域的索引和横纵坐标的索引（绝对索引）
    neighbordict={0:(0,-1),
                  1:(1,-1),
                  2:(1,0),
                  3:(1,1),
                  4:(0,1),
                  5:(-1,1),
                  6:(-1,0),
                  7:(-1,-1)}
    
    #以最后一个edge点为指针进行检索
    first_pixel=pixel()
    first_pixel.ypos=edge[-1][0]
    first_pixel.xpos=edge[-1][1]
    
    #3 S[K]从上一个目标点是S[k-1]逆时针进行遍历
    #重新规划索引new_index后一个索引和前一个索引呈对角关系
    #若索引大于4，归化

    if index<4:
        
        new_index=index+4
        
    else:
        
        new_index=index-4
        
    new_neighbordict=Dict.DictSortFromStart(neighbordict,new_index)
    
    #生成邻居列表,起始迭代邻居的索引
    first_pixel.GenerateNeighbor(img_tag)
    
    #邻域内邻居数量
    count=0

    for i in range(len(new_neighbordict)):
        
        #获取目标点的索引,转化为绝对索引
        index=list(new_neighbordict.keys())[i]
        
        #符合tag的点计数
        if first_pixel.neighbor[index]==tag:
            
            count+=1
            
            #建立新的pixel对象
            temp_pixel=pixel()
            temp_pixel.ypos=first_pixel.ypos+new_neighbordict[index][0]
            temp_pixel.xpos=first_pixel.xpos+new_neighbordict[index][1]
            pos=[temp_pixel.ypos,temp_pixel.xpos]
   
            #判断目标点和起点是否相同,不能是第一个点
            if i>0 and pos==edge[0]:
               
                flag_stop=True
                edge.append(pos)
                
                break
            
            #1 S[k-1]邻域内的第一个点已在边缘集合当中，则访问下一个点    
            if pos not in edge:
                
                edge.append(pos)
                
                break  
            
            #*2 S[k]邻域内只有一个边缘点，即上一个点S[k-1],则访问S[k-1]邻域内下一个点
            if len(edge)>1 and pos==edge[-2] and count==1 and i==7:
               
                edge.append(pos)
                
                break
                   
    return edge,index,flag_stop

#==============================================================================  
#在img_tag中根据edge[0]追踪边界,要追踪的像素标签值为tag
def EdgeTracing(tag,edge,img_tag):
    
    #初始化循环中止判别标志
    flag_stop=False
    
    #初始化绝对索引
    index=-4
    
    #进行第一次邻居搜索
    edge,index,flag_stop=Find1stNeighbor(tag,flag_stop,edge,img_tag,index) 
    
    while len(edge)>1 and flag_stop is False:
        
        edge,index,flag_stop=Find1stNeighbor(tag,flag_stop,edge,img_tag,index) 
    
    return edge

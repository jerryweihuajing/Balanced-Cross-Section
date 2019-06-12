# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 13:34:08 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于断层牵引法的平衡恢复函数库
"""

import copy
import numpy as np
import matplotlib.pyplot as plt
import object_fault_motion as o

"""
1) 调用函数中的函数不需要输入函数命名  
2) copy和deepcopy的差别：是否改变地址
"""    
       
#============================================================================== 
#输入路径path，读取图片，生成图片的rgb和灰度矩阵函数
#参数show表示图片预览参数：默认为None，rgb表示开启rgb预览，gray表示灰度预览
def LoadImage(load_path,show=False):
    
    img_rgb=plt.imread(load_path) 
    
    if show: 
        #显示rgb图像
        plt.figure()
        plt.imshow(img_rgb) 
#        plt.axis('off')
        
    return img_rgb

#改变输入图像的尺寸：增加m行n列
def AddPadding(img_rgb,m,n,show=False):
    
    #改变图像的尺寸
    new_img_rgb_shape=(np.shape(img_rgb)[0]+m,
                       np.shape(img_rgb)[1]+n,
                       np.shape(img_rgb)[2])

    #这种定义背景方式最奏效
    #背景色
    background_rgb=np.array([255,255,255],dtype=np.uint8)
        
    #new_img_rgb视为底图
    new_img_rgb=np.full(new_img_rgb_shape,background_rgb)  
    
    #着色
    mm,nn=int(np.floor(m/2)),int(np.floor(n/2))
    
    new_img_rgb[mm:-mm,nn:-nn]=img_rgb[:,:]
    
    if show: 
        #显示rgb图像
        plt.figure()
        plt.imshow(new_img_rgb) 
#        plt.axis('off')
        
    return new_img_rgb

#==============================================================================    
#生成基础列表和字典
def GenerateListAndDict(img_rgb):
    
    #获取图中的所有地层rgb值
    layer_rgb_list=[]
    
    #well
    well=int(np.shape(img_rgb)[1]/2)
    j=well
    
    for i in range(np.shape(img_rgb)[0]):
        
        if list(img_rgb[i,j]) not in layer_rgb_list:
            
            layer_rgb_list.append(list(img_rgb[i,j]))
    
    #将矩阵拉长      
    img_rgb=img_rgb.reshape(1,np.shape(img_rgb)[0]*np.shape(img_rgb)[1],3)
    
    #获取三通道值
    img_r=img_rgb[:,:,0]
    img_g=img_rgb[:,:,1]
    img_b=img_rgb[:,:,2]
    
    #建立集合
    set_r=list(set(img_r[0]))
    set_g=list(set(img_g[0]))
    set_b=list(set(img_b[0]))
    
    #判断rgb三通道值的数量是否相等
    if len(set_r)==len(set_g)==len(set_b):
        
        #判断是否差一个断层颜色   
        if len(set_r)-len(layer_rgb_list)==1: 
            
            #图像中的所有rgb-图中的所有地层rgb值
            fault_rgb=[] 
            
            #删去layer_rgb_list有的元素，set_r,set_g,set_b与layer_rgb_list的差为断层rgb
            for item in layer_rgb_list:
                
                set_r.remove(item[0])
                set_g.remove(item[1])
                set_b.remove(item[2])
                
        #断层的rgb值
        fault_rgb=[set_r[-1],set_g[-1],set_b[-1]]
    
        #如果拾取的well刚好涉及到断层,需要通过几何特性来判断
        """这里选取像素点最少的颜色为断层的rgb值"""
        if len(set_r)==len(layer_rgb_list):
            
            #各种颜色像素点数量的字典
            rgb_number_dict={}
            
            for k in range(len(layer_rgb_list)):
                
                rgb_number_dict[k]=np.sum(img_rgb==layer_rgb_list[k])
                
            #比较像素点数量的多少    
            key=list(rgb_number_dict.keys())
            value=list(rgb_number_dict.values())
            
            #得到断层的rgb值
            fault_rgb=layer_rgb_list[key[value.index(min(value))]]
            layer_rgb_list.remove(fault_rgb)
        
        #生成rgb_dict,包括layer和fault
        rgb_dict={}
        
        for i in range(len(layer_rgb_list)):
            
            rgb_dict[i+1]=layer_rgb_list[i]
            
        #索引-1代表断层fault
        rgb_dict[-1]=fault_rgb
        
    else:
        print('ERROR:重新填充')
           
    return fault_rgb,layer_rgb_list,rgb_dict

#9.12

#生成字典的初始化函数
def InitDict(img_rgb):
    
    rgb_list=[]
    
    for i in range(np.shape(img_rgb)[0]):
        
        for j in range(np.shape(img_rgb)[1]):
            
            if list(img_rgb[i,j].astype(int)) not in rgb_list:
                
                rgb_list.append(list(img_rgb[i,j].astype(int)))
                
    #判断背景色
    if [255,255,255] in rgb_list:            
        rgb_list.remove([255,255,255])    
         
    #各种颜色像素点数量的字典
    rgb_number_dict={}
    
    for k in range(len(rgb_list)):
        
        rgb_number_dict[k]=np.sum(img_rgb==rgb_list[k])
        
    #比较像素点数量的多少    
    key=list(rgb_number_dict.keys())
    value=list(rgb_number_dict.values())
    
    #得到断层的rgb值
    fault_rgb=rgb_list[key[value.index(min(value))]]
    
    #只有layer的rgb
    import copy
    
    layer_rgb_list=copy.deepcopy(rgb_list)
    
    #删除fault的rgb
    layer_rgb_list.remove(fault_rgb)
    
    #生成rgb_dict,包括layer和fault
    rgb_dict={}
    
    for i in range(len(layer_rgb_list)):
        
        rgb_dict[i+1]=layer_rgb_list[i]
        
    #索引-1代表断层fault
    rgb_dict[-1]=fault_rgb
    
    #0代表背景色
    rgb_dict[0]=[255,255,255]
    
    #转化为img_tag
    img_tag=RGB2Tag(img_rgb,rgb_dict)
    
    #基底tag
    base_tag=GetBaseTag(img_tag)
    
    #基底egb
    base_rgb=rgb_dict[base_tag]
    
    #删除并重命名
    del rgb_dict[base_tag]
    
    #base_tag的索引定义为-2
    rgb_dict[-2]=base_rgb
    
    return rgb_dict

#============================================================================== 
#字典按value搜索key
def DictKeyOfValue(dictionary,value):
    
    keys=list(dictionary.keys())
    values=list(dictionary.values())
    
    #要查询的值为value
    key=keys[values.index(value)]
    
    return key

#获取字典子集的函数，从索引start到索引stop,不包括索引stop
def DictSlice(dictionary,start,stop):
    
    keys=list(dictionary.keys())
    values=list(dictionary.values())  
    
    new_dict={}
    
    for i in range(start,stop):
        new_dict[keys[i]]=values[i]
        
    return new_dict

#以start为起始索引，将字典重新排序
def DictSortFromStart(dictionary,start):
    
    #两个字典切片
    new_dict_1=DictSlice(dictionary,start,len(dictionary))
    new_dict_2=DictSlice(dictionary,0,start)
    
    #建立新的索引列表
    keys=[]
    
    for item in list(new_dict_1.items()):
        keys.append(item[0])
        
    for item in list(new_dict_2.items()):
        keys.append(item[0])
        
    #建立新的值列表 
    values=[]
    
    for item in list(new_dict_1.items()):
        values.append(item[1])
        
    for item in list(new_dict_2.items()):
        values.append(item[1])
        
    #建立新的字典
    new_dict={}
    
    for k in range(len(dictionary)):
        new_dict[keys[k]]=values[k]
        
    return new_dict

#10.16   
#============================================================================== 
#将字典转化为频率统计字典   
def List2FrequencyDict(which_list):
    
    #建立集合列表
    element_list=list(set(which_list))
    
    #初始化频率列表
    frequency_list=[]
    
    #统计频率
    for this_element in element_list:
        
        that_frequency=0
        
        for element in which_list:
            
            if this_element==element:
                
                that_frequency+=1
        
        #将所有频数组合成列表
        frequency_list.append(that_frequency)
    
    #返回一个出现元素及其对应频率的列表
    return dict(zip(element_list,frequency_list))
             
#定义一个列表中某值出现的函数
def CalculateFrequency(which_list,which_value):
    
    if which_value not in which_list:
        
        print('ERROR:the value not in this list')
        
        return
    
    if which_value in which_list:
        
        map_element_frequency=List2FrequencyDict(which_list)
    
        return map_element_frequency[which_value]
    
#计算出列表中出现频率最高的元素的函数
def MostFrequentElement(which_list):
    
    #频率统计字典
    map_element_frequency=List2FrequencyDict(which_list)
    
    #最大频率
    the_frequency=max(list(map_element_frequency.values()))
    
    return DictKeyOfValue(List2FrequencyDict(which_list),the_frequency)

#9.6
#==============================================================================     
#补色变换
def ReverseRGB(img_rgb):
    
    return np.array([255,255,255]-img_rgb,dtype=np.uint8) 

#由img_rgb生成img_tag
def RGB2Tag(img_rgb,rgb_dict,show=False):
    
    img_tag=np.zeros((np.shape(img_rgb)[0],np.shape(img_rgb)[1]))
    
    #给img_tag矩阵赋值
    for i in range(np.shape(img_tag)[0]):
        
        for j in range(np.shape(img_tag)[1]):
            
            img_tag[i,j]=DictKeyOfValue(rgb_dict,list(img_rgb[i,j].astype(int)))
    
    #显示
    if show:
        plt.figure()
        plt.imshow(img_tag,cmap='gray')
         
    return img_tag

#由img_tag生成img_rgb
def Tag2RGB(img_tag,rgb_dict,show=False):
    
    img_rgb=np.zeros((np.shape(img_tag)[0],np.shape(img_tag)[1],3))

    #给img_rgb矩阵赋值
    for i in range(np.shape(img_rgb)[0]):
        
        for j in range(np.shape(img_rgb)[1]):
            
#            print(img_tag[i,j])
#            print(rgb_dict[int(img_tag[i,j])])

            #注意dtype，必须是uint8才能正常显示RGB
            img_rgb[i,j]=np.array(rgb_dict[img_tag[i,j]])
    
    #转化为正确输出格式      
    img_rgb=np.array(img_rgb,dtype=np.uint8)  
      
    #显示
    if show:
        
        plt.figure()
        plt.imshow(img_rgb)
        
    return img_rgb

#9.13

#计算出基底base tag的函数 设计一个
#计算base_tag的方法
def GetBaseTag(img_tag):
    
    """从图像末尾进行扫描，获取到的非背景色的tag或rgb就是"""
    for i in range(np.shape(img_tag)[0]-1,0,-1):
        
        #只要不是全空白那就一定是它咯
        if list(img_tag[i])!=list(img_tag[-1]):  
            
            break
    
    #取中间值
    return img_tag[i,int(np.shape(img_tag)[1]/2)]

#9.12
#============================================================================== 
#初始化所有的fractions
def Initfractions(img_rgb,img_tag,rgb_dict,text=False,show=False,base='off'):
    
    #面积最大的tag
    base_tag=GetBaseTag(img_tag)
    
    #拾取出tag为2,3,4的层
    import copy
    
    fraction_rgb_dict=copy.deepcopy(rgb_dict)
    
    #删除空白rgb索引
    del fraction_rgb_dict[0]
    
    #图像中的所有fraction对象列表
    total_fractions=[]
    
    #拾取断层和地层并显示
    for this_tag in list(fraction_rgb_dict.keys()):
    
        #是否要基底的那个tag
        if base=='off':
    
            if this_tag==base_tag:
                
                continue
        
        that_fraction=PickSomething(img_rgb,img_tag,this_tag,rgb_dict)
        
        total_fractions+=that_fraction
    
    #显示total_fractions
    if show:
        ShowFractions(total_fractions,img_rgb,rgb_dict,text)
        
    return total_fractions
 
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
    first_pixel=o.pixel()
    first_pixel.ypos=edge[-1][0]
    first_pixel.xpos=edge[-1][1]
    
    #3 S[K]从上一个目标点是S[k-1]逆时针进行遍历
    #重新规划索引new_index后一个索引和前一个索引呈对角关系
    #若索引大于4，归化

    if index<4:
        new_index=index+4
    else:
        new_index=index-4
        
    new_neighbordict=DictSortFromStart(neighbordict,new_index)
    
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
            temp_pixel=o.pixel()
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

#根据fault_edge[0]追踪边界,要追踪的像素标签值为tag
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

#============================================================================== 
#显示某个列表中的所有像素点
def ShowSomething(img_rgb,something,tag,rgb_dict,output=False):  
    
    #显示找到的集合
    background_rgb=img_rgb[0,0]
    img_temp=np.full(np.shape(img_rgb),background_rgb)
    
    #赋予目标对象的位置
    for item in something:
        
        i,j=item[0],item[1]
        img_temp[i,j]=rgb_dict[tag]   
        
    #在图中显示
    plt.figure()
    plt.imshow(img_temp)
#    plt.axis('off')
    
    if output:
        return img_temp
    
"""设计通过显示tag和part显示块体的函数"""
#写一个同时能显示很多tag像素点的函数，混合tag，显示对象为fraction对象的集合
#显示多个fraction对象的函数
def ShowFractions(fractions,img_rgb,rgb_dict,text=False,output=False):
    
    #显示找到的内容
    background_rgb=img_rgb[0,0]
    img_temp=np.full(np.shape(img_rgb),background_rgb)
    
    #在图中显示
    plt.figure()
    
    #赋予目标对象的位置
    for this_fraction in fractions:
        
        #tag,part,content,center      
        tag=this_fraction.tag
        part=this_fraction.part
        content=this_fraction.content
        center=this_fraction.center
    
        #着色
        for pos in content:
            i,j=pos[0],pos[1]
            img_temp[i,j]=rgb_dict[tag] 
            
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

    plt.imshow(img_temp)
#    plt.axis('off')
    
    if output:
        return img_temp
    
#显示多个plate对象的函数
#plates是plate对象组成的列表
def ShowPlates(plates,img_rgb,rgb_dict,text=False,output=False):
        
    #建立总fractions列表
    total_fractions=[]
    
    #遍历plates中的每一个plate
    for this_plate in plates:

        #将每一个fraction对象都放进来
        total_fractions+=this_plate.fractions
        
    #显示
    ShowFractions(total_fractions,img_rgb,rgb_dict,text,output)  
    
#==============================================================================     
"""算的太慢!!!,只能缩小尺寸"""    
"""
填充方法：
1 填充边界内的点，向内侵蚀
2 阿华算法：IJ交织（已改进，解决了拾取本不该属于集合里的点的问题）
"""
#提取出tag值的像素点坐标的集合
def PickSomething(img_rgb,img_tag,tag,rgb_dict,show=False,text=False,output=False):
    
    #content_sum=Content[0]+Content[1]+...
    content_sum=[]   
    
    #method=1代表方法1，method=2代表方法2
    method=2    
    
    #复制生成临时的img_tag,用于标记已上色的像素点
    temp_img_tag=copy.deepcopy(img_tag)   
    
    #是否继续遍历的标志   
    content_flag=tag in temp_img_tag  
    
    #块体tag a part b的重心坐标
    Center={}      
    
    #Center字典增加一个新的tag列表
    Center[tag]=[]  
    
    #fractions是fraction对象的集合
    fractions=[]   
    
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
            fault_edge,content_flag=Find1stPixel(tag,img_tag,content_sum)   
            
            #追踪fault的边界
            fault_edge=EdgeTracing(tag,fault_edge,img_tag)
            
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
                    temp_pixel=o.pixel()
                    temp_pixel.ypos=last_edge[k][0]
                    temp_pixel.xpos=last_edge[k][1]  
                    
                    #生成邻居列表,起始迭代邻居的索引
                    temp_pixel.GenerateNeighbor(img_tag)   
                    
                    for i in range(len(neighbordict)): 
                        
                        #判断标签为tag
                        if temp_pixel.neighbor[i]==tag:
                            
                            #邻居的坐标
                            new_y=temp_pixel.ypos+neighbordict[i][0]
                            new_x=temp_pixel.xpos+neighbordict[i][1]
                            pos=[new_y,new_x]
                            
                            #新的点在不在fault列表内
                            if pos not in o.fault:
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
            print('tag',tag,'part',len(fractions),':')
            
            #寻找第一个特征值值点
            edge=Find1stPixel(tag,img_tag,content_sum)

            #追踪content的边界
            edge=EdgeTracing(tag,edge,img_tag)
            
            #this_fraction表示正在处理的fraction
            
            #如果tag=-1,则fraction为fault
            if tag==-1:
                this_fraction=o.fault()    
            else:
                this_fraction=o.layer()     
            
            #对tag属性赋值
            this_fraction.tag=tag  
       
            #给part属性赋值
            this_fraction.part=len(fractions)
            
            #给edge属性赋值
            this_fraction.edge=edge
            
            #求对象的范围矩阵
            #left right bottom top 这几个重要的参数
            I=[]
            J=[]
            
            for item in edge:       
                if item[0] not in I: 
                    I.append(item[0])
                    
                if item[1] not in J:
                    J.append(item[1])
                    
            #初始生成的I,J不是按顺序的，需要对其进行排序
            I.sort()
            J.sort() 
               
            left,right=min(J),max(J)
            bottom,top=min(I),max(I)
            
            #获取块体的中点
            center_x=(left+right)/2
            center_y=(bottom+top)/2
            
            #标注的坐标，即块体Content[part]的中点
            center=(center_x,center_y)
            
            #对center属性赋值
            this_fraction.center=center
                        
            Center[tag].append(center)
            
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
                            if list(img_tag[row,start_j:stop_j])==[tag]*(stop_j-start_j):
                                
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
                content_row_column=copy.deepcopy(content)
 
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
                        if list(img_tag[start_i:stop_i,column])==[tag]*(stop_i-start_i):
                            
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
                content_column_row=copy.deepcopy(content)
                
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
                    
                    #content_sum=Content[0]+Content[1]+...
                    content_sum+=content
                    
                    #Content[0],Content[1]是每个块体像素点的集合
                    fractions.append(this_fraction)
                                      
                    #判断循环是否需要中止：1和2代表不同方法       
                    method_for_stop=2
                    
                    """1 判断条件为新的img_tag是否还存在标签值"""
                    #这种方法要特别久 
                    if method_for_stop==1:     
                        
                        #符合条件的tag不在content_sum中的数量
                        count_for_stop=0
                        for i in range(np.shape(img_tag)[0]):
                            for j in range(np.shape(img_tag)[1]):
                                if img_tag[i,j]==tag:
                                    pos=[i,j]
                                    if pos not in content_sum:
                                        count_for_stop+=1
                                    
                        #循环结束的判断条件               
                        if count_for_stop==0:
                            content_flag=False
                                
                    """2 判断条件为temp_img_tag是否存在tag"""  
                    if method_for_stop==2: 
                        content_flag=tag in temp_img_tag
                    
                        if content_flag:
                            print('picking is not complete')
                        else:                      
                            print('everything is OK')
        
    #检查'everything is OK'是否成立
    check=False
    if check:          
        count=0            
        for i in range(np.shape(temp_img_tag)[0]):
            for j in range(np.shape(temp_img_tag)[1]):
                if temp_img_tag[i,j]==tag:
                    count+=1            
        print(count) 
        
    #显示一下Content的位置
    if show:
        ShowFractions(fractions,img_rgb,rgb_dict,text,output)
                
    return fractions

#==============================================================================                     
#处理掉total_fractions中所有fault对象的函数
def DeleteFault(total_fractions):
    
    #结果fractions列表
    result_fractions=[]
    
    for this_fraction in total_fractions:   
        
        if type(this_fraction) is not o.fault:
            
            result_fractions.append(this_fraction)
        
    return result_fractions  

#9.14

#从图像中获取断层
def FaultFrom(total_fractions,img_rgb,show=False):
    
    print('')
    print('here comes a new fault')
    print('......')
    print('please pick the fault')
    
    #点击获取像素点坐标
    fault_point_pos=plt.ginput(1)[0]

    print('......')
    print('picking the fault')
    
    #注意反过来，因为是xy坐标
    pos_xy=[int(fault_point_pos[0]),int(fault_point_pos[1])]
    
    import copy
    
    pos_IJ=copy.deepcopy(pos_xy)
    
    #IJ形式是xy形式的颠倒
    pos_IJ.reverse()
    
    #所有fault的列表
    total_faults=[]
    
    #这个点到所有fault的距离列表
    distance_total_faults=[]
    
    #建立所有fault的列表
    #计算这个点到fault中心的远近
    for this_fraction in total_fractions:
        
        if isinstance(this_fraction,o.fault):
            
            #上车上车
            total_faults.append(this_fraction)
     
            #计算距离
            distance_this_fault=Distance(this_fraction.center,pos_xy)
            distance_total_faults.append(distance_this_fault)
    
    #队距离和fault对象建立索引你关系
    map_distance_total_faults=dict(zip(distance_total_faults,total_faults))
    
    for this_fault in total_faults:
    
        #首先直接判断是否位于content内部
        if pos_IJ in this_fault.content:

            print('......')
            print('picking of the fault is over')
            
            if show:
                ShowEdge(this_fault,img_rgb)
                
            return this_fault
               
    #其次如果第一下没点上，通过计算距离远近来判断
    that_fraction=map_distance_total_faults[min(distance_total_faults)]

    print('......')
    print('picking of the fault is over')
    
    if show:
        ShowEdge(this_fraction,img_rgb)
        
    return that_fraction

#============================================================================== 
"""移动plate相关函数"""
#通过fault来确定上下盘
#tag_layer是需要抽取layer的tag
#now_img_tag表示现在tag矩阵
#total_fractions是需要拆分的fraction集合
def PickUpAndDown(fault,total_fractions,now_img_tag,img_rgb,rgb_dict,
                  show=False,text=False,output=False):   
    
    layer_tag=list(rgb_dict.keys())
    
    #删除背景tag
    layer_tag.remove(0)
    
    #删除fault的tag
    layer_tag.remove(-1)
    
    #删除基底tag
    base_tag=GetBaseTag(now_img_tag)
    layer_tag.remove(base_tag)

    #从fractions中删除fault
    total_fractions_temp=copy.copy(total_fractions)
    total_fractions_temp.remove(fault)
    
    #先确定上盘由fault.edge来确定
    #左右tag列表
    tag_left,tag_right=[],[]  
  
    #fault.edge中符合左右tag值的即可 
    for pos in fault.edge:
        
        #左右tag值坐标
        pos_right=[pos[0],pos[1]+1]   
        pos_left=[pos[0],pos[1]-1]
        
        #左右tag
        tag_left.append(now_img_tag[pos_left[0],pos_left[1]])   
        tag_right.append(now_img_tag[pos_right[0],pos_right[1]])  
    
    #成为集合，转为列表
    tag_left=list(set(tag_left))  
    tag_right=list(set(tag_right))
    
    #删除不符合layer_tag的元素
    #左
    tag_left_temp=[]
    
    for tag in tag_left:
        if tag in layer_tag:
            tag_left_temp.append(tag)           
    #右
    tag_right_temp=[]
    
    for tag in tag_right:
        if tag in layer_tag:
            tag_right_temp.append(tag)
    
    tag_left,tag_right=tag_left_temp,tag_right_temp
       
    """
    很关键：确定上下盘分别是哪些fractions
    上下盘和左右盘的关系由倾向确定
    左倾：上盘是左
    右倾：上盘是右
    确定左右以后，根据center的位置确定total_fractions中哪些上哪些下
    """
    
    #先求出左右盘的fractions
    #左右盘fractions列表
    fractions_left=[]
    fractions_right=[]

    for this_fraction in total_fractions:
        #左盘
        if this_fraction.center[0]<fault.center[0]:
            fractions_left.append(this_fraction)
            
        #右盘
        if this_fraction.center[0]>fault.center[0]:
            fractions_right.append(this_fraction)
               
    #上下盘的fractions
    fractions_up,fractions_down=[],[]

    #初始化倾向
    fault.Init(now_img_tag)  
    
    #左倾：左是上盘
    if fault.inclination=='left':
        
        fractions_up=copy.deepcopy(fractions_left)
        fractions_down=copy.deepcopy(fractions_right)
        
    #右倾：右是上盘
    if fault.inclination=='right':
        
        fractions_up=copy.deepcopy(fractions_right)
        fractions_down=copy.deepcopy(fractions_right)
        
    #建立上下盘的plate对象
    plate_up=o.plate()
    plate_down=o.plate()
    
    #并进行初始化
    plate_up.Init(fractions_up)
    plate_down.Init(fractions_down)
    
    #显示    
    if show:
        
        #上下盘分别
        plate_up.Show(img_rgb,rgb_dict,text,output)
        plate_down.Show(img_rgb,rgb_dict,text,output)
        
        #合照
        plates=[plate_up,plate_down]
        ShowPlates(plates,img_rgb,rgb_dict,text,output)
        
    return plate_up,plate_down

#============================================================================== 
#写一个大函数，表示参与移动的上下盘
def MovePlate(plate_up,plate_down,fault,img_tag,mode,show=False):
    
    #top的tag作为目标
    if plate_up.top.tag==plate_down.top.tag:
        
        target_tag=plate_up.top.tag
    
    #如果两侧top的tag不等，那么要找较新的layer作为tag
    else:
        #上下盘others的tag集合
        plate_up_others_tag,plate_down_others_tag=[],[]
        
        #给以上列表赋值
        for this_fraction in plate_up.others:
            
            plate_up_others_tag.append(this_fraction.tag)
            
        for this_fraction in plate_down.others:
            
            plate_down_others_tag.append(this_fraction.tag)
            
        #判断方法:
        #1) up的top在down的others里:down的top
        if plate_up.top.tag in plate_down_others_tag:
            
            target_tag=plate_down.top.tag
            
        #2) down的top在up的others里:up的top
        if plate_down.top.tag in plate_up_others_tag:
            
            target_tag=plate_up.top.tag  

    #根据tag找角点，
    pos_top_up,pos_bottom_up,pos_top_down,pos_bottom_down=fault.AngleUpDown(target_tag,img_tag)
    
    #根据mode分别使用bottom和top模式
    #以top点位基准
    if mode=='top':
        i_offset=pos_top_up[0]-pos_top_down[0]
        j_offset=pos_top_up[1]-pos_top_down[1]
        
    #以bottom点位基准
    if mode=='bottom':
        i_offset=pos_bottom_up[0]-pos_bottom_down[0]
        j_offset=pos_bottom_up[1]-pos_bottom_down[1]  

    #up在前移动-,down移动+
    #假设移动相同的距离或是其他大小
    plate_up.Move(-np.ceil(i_offset/2),-np.ceil(j_offset/2)) 
    plate_down.Move(np.ceil(i_offset/2),np.ceil(j_offset/2)) 
     
    return plate_up,plate_down  
    
#计算plates面积   
#plates表示所有plate
def Area(plates,target_tag,img_rgb,rgb_dict):
    
    #临时矩阵
    img_temp=np.full(np.shape(img_rgb),img_rgb[0,0])  
    
    #所有plate的content着色
    for this_plate in plates:
        
        for this_fraction in this_plate.fractions:
            
            for pos in this_fraction.content:
                
                i,j=pos[0],pos[1]
                img_temp[i,j]=rgb_dict[this_fraction.tag]       
    
    #计算fractions的面积
    area=len(img_temp[img_temp==rgb_dict[target_tag]])/np.shape(img_rgb)[-1]
    
    return area

#确定top和bottom模式
def ChooseMode(plates,fault,target_tag,img_tag,img_rgb,rgb_dict):
    
    #复制生成两种模式各自的自变量
    plates_top=copy.deepcopy(plates)
    plates_bottom=copy.deepcopy(plates)
    
    #移动
    plates_top=MovePlate(plates_top[0],plates_top[1],fault,img_tag,'top')
    plates_bottom=MovePlate(plates_bottom[0],plates_bottom[1],fault,img_tag,'bottom')

    #移动后面积
    area_top=Area(plates_top,target_tag,img_rgb,rgb_dict)
    area_bottom=Area(plates_bottom,target_tag,img_rgb,rgb_dict)
    
    #模式和面积的对应关系
    mode_area_dict={'top':area_top,'bottom':area_bottom}
    area_deficit=abs(area_top-area_bottom)
    
    #正断：取小
    if fault.polarity=='positive':
        
        mode=DictKeyOfValue(mode_area_dict,min(list(mode_area_dict.values())))  
        
        print('\nto thicken the layer',area_deficit)
        
    #逆断：取大
    if fault.polarity=='negative':
        
        mode=DictKeyOfValue(mode_area_dict,max(list(mode_area_dict.values())))  
        
        print('\nto fill the gap',area_deficit)
        
    return mode 

"""how to thicken and fill?"""

#正式地移动plate函数
def TrueMove(plate_up,plate_down,fault,target_tag,
             img_tag,img_rgb,rgb_dict,show=False,text=False,output=False):
    
    #计算移动模式
    true_mode=ChooseMode([plate_up,plate_down],fault,target_tag,img_tag,img_rgb,rgb_dict)
    
#    print(true_mode)
    
    #正式地移动
    plates=MovePlate(plate_up,plate_down,fault,img_tag,true_mode)
    
    if show:        
        #复制plates 
        plates_to_show=copy.deepcopy(plates)   
        
        ShowPlates(plates_to_show,img_rgb,rgb_dict,text,output)
        
        #显示单独层
        fractions_to_show=[]
        
        #将所有plate对象平移并显示
        for this_plate in plates:
            
#            显示顶部
            fractions_to_show.append(this_plate.top)
#            
#            #显示底部
#            fractions_to_show+=this_plate.others

        ShowFractions(fractions_to_show,img_rgb,rgb_dict,text,output)
        
    return plates

#============================================================================== 
#给所有layer对象赋予角点
#输入layer_tag,遍历
#对total_fractions进行操作
def PickAngle(total_fractions,img_tag):
    
    #建立layer对象集合
    Layer=[]
    
    #建立layer的tag集合
    layer_tag=[]
    
    #建立fault对象集合
    Fault=[]
    
    for this_fraction in total_fractions:
        
        if type(this_fraction) is o.layer:
            Layer.append(this_fraction)
            layer_tag.append(this_fraction.tag)
            
        if type(this_fraction) is o.fault:
            Fault.append(this_fraction)
            
    #转化为列表        
    layer_tag=list(set(layer_tag))    
    
    #全世界所有的angle点
    Angle_temp=[]

    """1 收录layer与pad的边界点"""
    
    for this_layer in Layer:
                    
        #edge的横纵坐标
        I_edge=[pos[0] for pos in this_layer.edge]
        J_edge=[pos[1] for pos in this_layer.edge]
        
        #找最小值
        J_min=min(J_edge)
        J_max=max(J_edge)
        
        #符合J最值的I列表与临时
        I_max_temp=[]
        I_min_temp=[]
        
        I_max=[]
        I_min=[]
                     
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
        
        #判断这种点是否存在
        if I_max!=[]:
            Angle_temp.append([max(I_max),J_max])
            Angle_temp.append([min(I_max),J_max])
               
        if I_min!=[]:    
            Angle_temp.append([max(I_min),J_min])
            Angle_temp.append([min(I_min),J_min])
           
    """2 收录layer与fault的边界点"""    
    
    for target_tag in layer_tag:
        
        for this_fault in Fault:

            #边缘左侧点坐标列表
            edge_left=[]
            
            #边缘右侧点坐标列表
            edge_right=[]
            
            #fault.edge中符合左右tag值的即可 
                   
            for pos in this_fault.edge:
                        
                #左右tag值
                pos_left=[pos[0],pos[1]-1]
                pos_right=[pos[0],pos[1]+1]
                
                #左右点集合
                if img_tag[pos_left[0],pos_left[1]]==target_tag:
                    edge_left.append(pos_left)
                    
                if img_tag[pos_right[0],pos_right[1]]==target_tag:
                    edge_right.append(pos_right)      
                
            #左侧点的上下顶点
            I_left=[pos[0] for pos in edge_left]
            J_left=[pos[1] for pos in edge_left]
            
            #右侧点的上下顶点
            I_right=[pos[0] for pos in edge_right]
            J_right=[pos[1] for pos in edge_right] 
            
            #不完全统计
                     
            #左侧有点的情况   
            if I_left!=[] and J_left!=[]:    
                            
                #两个列表合成字典
                I_J_left=dict(zip(I_left,J_left))
                
                #寻找块体角点
                pos_top_left=[min(I_left),I_J_left[min(I_left)]]
                pos_bottom_left=[max(I_left),I_J_left[max(I_left)]]
                
                Angle_temp.append(pos_top_left)
                Angle_temp.append(pos_bottom_left)

            #右侧有点的情况  
            if I_right!=[] and J_right!=[]:   

                #两个列表合成字典
                I_J_right=dict(zip(I_right,J_right))
                
                #寻找块体角点
                pos_top_right=[min(I_right),I_J_right[min(I_right)]]
                pos_bottom_right=[max(I_right),I_J_right[max(I_right)]]
            
                Angle_temp.append(pos_top_right)
                Angle_temp.append(pos_bottom_right)             

    #并创建空列表 
    Angle=[]

    #清除相同的点  
    
    for pos in Angle_temp:
        
        if pos not in Angle:  
            Angle.append(pos)
            
    """在获取了潜在角点之后，对每个layer赋予真实角点，没分到角点的启用max-min机制生成角点"""  
    
    return Angle

#============================================================================== 
#标记某个点            
def ShowOnePoint(pos,length_of_side,img_rgb):
    
    #对正方形边赋值
    img_rgb[pos[0]-length_of_side,pos[1]-length_of_side:pos[1]+length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]+length_of_side,pos[1]-length_of_side:pos[1]+length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]-length_of_side:pos[0]+length_of_side,pos[1]-length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]-length_of_side:pos[0]+length_of_side,pos[1]+length_of_side]=np.array([0,0,0])
    
    #对正方形角赋值
    img_rgb[pos[0]-length_of_side,pos[1]-length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]+length_of_side,pos[1]-length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]-length_of_side,pos[1]+length_of_side]=np.array([0,0,0])
    img_rgb[pos[0]+length_of_side,pos[1]+length_of_side]=np.array([0,0,0])
    
    return img_rgb

def ShowAllAngle(Angle,length_of_side,img_rgb):

    #在角点处画正方形：上下length_of_side个像素点
    #pos[0]-10:pos[0]+10,pos[1]-10:pos[1]+10
    for pos in Angle:   
        
        img_rgb=ShowOnePoint(pos,length_of_side,img_rgb)

    plt.imshow(img_rgb)

#将总角点分配给各个layer 
def DistributeAngle(Angle,Layer):
    
    #遍历每一个Angle坐标
    for pos in Angle:
        
        #遍历每一个layer对象
        for this_layer in Layer:          
            if pos in this_layer.edge:
                
                #将拟角点集合中添加这个坐标
                this_layer.angle.append(pos)
                
                break
            
#显示fraction对象的边界点
def ShowEdge(fraction,img_rgb):
    
    #对所有的边界点，赋予全0的rgb值
    for pos in fraction.edge:
        
        img_rgb[pos[0],pos[1]]=np.array([0,0,0])
        
    plt.imshow(img_rgb)   
          
#用于检验并显示某个layer的角点
def CheckAngle(which_layer,length_of_side,img_rgb):
    
#    #打印每一个点的坐标
#    print(which_layer.angle)
#    print(len(which_layer.angle))
    
    #标记出所有的角点
    for pos in which_layer.angle:   
        img_rgb=ShowOnePoint(pos,length_of_side,img_rgb)
    
    #对所有的边界点，赋予全0的rgb值    
    for pos in which_layer.edge:
        img_rgb[pos[0],pos[1]]=np.array([0,0,0])    
        
    plt.imshow(img_rgb) 
    
#==============================================================================     
#写调整angle的函数
#事后将其写进类里
#计算两点之间的距离
def Distance(pos_A,pos_B):
    
    #判断pos_A,pos_B的数据类型，无论如何都转化为np.array
    if type(pos_A) is not np.array:
        pos_A=np.array(pos_A)
    
    if type(pos_B) is not np.array:
        pos_B=np.array(pos_B)
  
    return np.sqrt(np.sum((pos_A-pos_B)**2))

#调整layer的angle
#低版本
def AdjustAngle(which_layer,img_rgb):
     
    #确保角点数量大于4
    if len(which_layer.angle)>=4:
        
        pos_center=[which_layer.center[1],which_layer.center[0]]
        
        #然后以center为中心把layer分成四个象限
        #把angle分配到4个list当中
        
        for pos_angle in which_layer.angle:
    
            #下
            if pos_angle[0]>pos_center[0]:
                        
                #左 下
                if pos_angle[1]<pos_center[1]:  
                    which_layer.bottom_left_list.append(pos_angle)
                    
                #右 下 
                if pos_angle[1]>pos_center[1]:               
                    which_layer.bottom_right_list.append(pos_angle)
                    
            #上
            if pos_angle[0]<pos_center[0]:
                        
                #左 上
                if pos_angle[1]<pos_center[1]:  
                    which_layer.top_left_list.append(pos_angle)
                    
                #右 上
                if pos_angle[1]>pos_center[1]:               
                    which_layer.top_right_list.append(pos_angle)
    #6.28
    
        #遍历四个角angle列表,计算和中心的距离
        
        #距离列表   
        all_distance=[[],[],[],[]]
        
        #四个角点列表
        all_list=[which_layer.bottom_left_list,
                  which_layer.bottom_right_list,
                  which_layer.top_left_list,
                  which_layer.top_right_list]
        
        #四个最终角点
        all_angle=[]
        
        for k in range(len(all_distance)):
            
            #遍历角点列表
            for pos_angle in all_list[k]:
                
                #距离列表赋值
                all_distance[k].append(Distance(pos_angle,pos_center))
            
            if all_distance[k]!=[]:
                
                #建立距离和点的索引
                distance_angle=dict(zip(all_distance[k],all_list[k]))
                
                #对layer对象中的四大angle进行赋值
                all_angle.append(distance_angle[max(all_distance[k])])
        
            #若不符合条件，添加一个None
            
            else: 
                all_angle.append(None)
                   
        #赋值给类属性
        which_layer.bottom_left,\
        which_layer.bottom_right,\
        which_layer.top_left,\
        which_layer.top_right\
        =all_angle
           
    #6.29
              
        """解决角点扎堆问题：退而求其次法
        若某点为None，用which_layer.angle中的其他点来做替代"""
        #应当将两种方法合而为一
              
        #建立左右部分角点列表
        left_angle=[pos for pos in which_layer.angle if pos[1]<pos_center[1]] 
        right_angle=[pos for pos in which_layer.angle if pos[1]>pos_center[1]] 
        
        #左右深度
        left_depth=[pos[0] for pos in left_angle]
        right_depth=[pos[0] for pos in right_angle]
        
        #建立深度与角点坐标的列表
        left_depth_angle=dict(zip(left_depth,left_angle))
        right_depth_angle=dict(zip(right_depth,right_angle))
        
        #逐个点描述比较稳妥
        
        #左下
        if which_layer.bottom_left==None:
            which_layer.bottom_left=left_depth_angle[max(left_depth)]
            
        #右下
        if which_layer.bottom_right==None:
            which_layer.bottom_right=right_depth_angle[max(right_depth)]
        
        #左上
        if which_layer.top_left==None:
            which_layer.top_left=left_depth_angle[max(left_depth)]
            
        #右上
        if which_layer.top_right==None:
            which_layer.top_right=right_depth_angle[max(right_depth)]   
            
        #重新定义（作图需要）
        all_angle=[which_layer.bottom_left,
                   which_layer.bottom_right,
                   which_layer.top_left,
                   which_layer.top_right]
        
        #以下部分可写一个检验模块
        print('')
        
        #显示中心
        ShowOnePoint([int(pos_center[0]),int(pos_center[1])],3,img_rgb)
        
        #检查这些点的位置
        for pos in all_angle:
            print(pos)
            
            #方框标记出角点
            if pos!=None:
                ShowOnePoint(pos,3,img_rgb)
                
        plt.imshow(img_rgb)

    else:
        print('insufficient angles')
        
#7.3 
        
"""计算多边形面积，判断点是否在多边形内部相关问题"""       
#==============================================================================         
#计算三角形面积的函数(海伦公式)
#pos_A,pos_B,pos_C为三角形三个顶点
def AreaTriangle(ABC):
    
    pos_A,pos_B,pos_C=ABC
    
    #计算三条边长
    AB=Distance(pos_A,pos_B)
    AC=Distance(pos_A,pos_C)
    CB=Distance(pos_C,pos_B)
    
    a,b,c=CB,AC,AB
    p=(a+b+c)/2
    
    return np.sqrt(p*(p-a)*(p-b)*(p-c))

#判断点P在三角形内的函数
#pos_P是参与判断的点
#ABC是三角形的三个顶点列表，即ABC=[pos_A,pos_B,pos_C]
def PointInTriangle(pos_P,ABC):
    
    #还原ABC坐标
    pos_A,pos_B,pos_C=ABC
    
    #向量化
    pos_A=np.array(pos_A)
    pos_B=np.array(pos_B)
    pos_C=np.array(pos_C)
    
    pos_P=np.array(pos_P)
    
    #使用方法2
    method='2'
    
    #方法一：面积法
    if method=='1':

        Area_PAB=AreaTriangle(pos_A,pos_B,pos_P)    
        Area_PAC=AreaTriangle(pos_A,pos_P,pos_C)   
        Area_PBC=AreaTriangle(pos_P,pos_B,pos_C)
        
        Area_ABC=AreaTriangle(pos_A,pos_B,pos_C)
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
       
        import sympy
        u=sympy.Symbol('u')
        v=sympy.Symbol('v')
        
        #得到的解是一个数组
        answer=sympy.solve([u*_AC[0]+v*_AB[0]-_AP[0],u*_AC[1]+v*_AB[1]-_AP[1]],[u,v])
        
#        print(answer[u],answer[v])
        
        u,v=answer[u],answer[v]
        
        #判断条件：0<=u<=1,0<=v<=1,0<=u+v<=1
        if 0<=u<=1 and 0<=v<=1 and 0<=u+v<=1:
            return True  
        else:
            return False
        
#==============================================================================         
#判断四边形的凹凸
def ConcaveOrConvexOfQuadrangle(ABCD):
    
    pos_ABCD=[]
    
    #转化为数组
    for pos in ABCD: 
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
        
#        print(pos)
#        print(pos_triangle_temp)
 
        #三个顶点生成三角形
        triangle_temp=o.triangle(pos_triangle_temp)
        
#        print(triangle_temp.area)
        
        #将逻辑值加入列表
        bool_point_in_triangle=triangle_temp.IncludePoint(pos)
        
#        print(bool_point_in_triangle)
        
        bool_point_in_triangle_list.append(bool_point_in_triangle)
    
#    print(bool_point_in_triangle_list)
    
    #判断是否有点不在三角形内
    if True in bool_point_in_triangle_list:   
        return 'concave'
    else:
        return 'convex'    
    
#给四边形四个顶点以正确的链接顺序排序
def OrderOfQuadrangle(ABCD):
    
    #若四边形凹
    if ConcaveOrConvexOfQuadrangle(ABCD)=='concave':
        
        #重新给出合理坐标
        print('give the points in order')
    
    if ConcaveOrConvexOfQuadrangle(ABCD)=='convex':
        
        #排序后的答案
        pos_ABCD_ordered=[]
        
        pos_ABCD=[]
    
        #转化为数组
        for pos in ABCD: 
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
            
#            print(index_MN,index_UV)
            
            #MN表示拟对角线中的其中一条
            pos_M=pos_ABCD[index_MN[0]]
            pos_N=pos_ABCD[index_MN[1]]
            
            #UV表示拟对角线中的其中一条
            pos_U=pos_ABCD[index_UV[0]]
            pos_V=pos_ABCD[index_UV[1]]
               
#            print(pos_M,pos_N,pos_U,pos_V)
#            print((pos_M-pos_N)[0],(pos_M-pos_N)[1])
            
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
#            a_MN,b_MN,c_MN=float('%0.2f' %a_MN),float('%0.2f' %b_MN),float('%0.2f '%c_MN)
#            a_UV,b_UV,c_UV=float('%0.2f '%c_UV),float('%0.2f' %b_UV),float('%0.2f' %a_UV)
#          
#            print(a_MN,b_MN,c_MN)
#            print(a_UV,b_UV,c_UV)
      
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

#                print(pos_O)                      
#                print(pos_M,pos_O,pos_N)
#                print(pos_U,pos_O,pos_V)
                
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
#                    print(pos_O)               
#                    print('correct point')   
                    
                    #输出正确顺序的点
                    pos_ABCD_ordered=[pos_M,pos_U,pos_N,pos_V]
                    
#                    print(pos_ABCD_ordered)     
                    
                    break     
                
        #正确答案非空         
        if pos_ABCD_ordered!=[]:    
            return pos_ABCD_ordered
      
#计算四边形面积的函数
def AreaQuadrangle(ABCD):
    
    #重新排列
    ABCD=OrderOfQuadrangle(ABCD)
    
#    print(ABCD)
    
    #转化为数组
    pos_ABCD=[]
    
    for pos in ABCD: 
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
    area_triangle_1=AreaTriangle(point_list_triangle_1)
    area_triangle_2=AreaTriangle(point_list_triangle_2)
        
#        print(ABCD[:-1])
#        print(ABCD[1:])
#        
#        print(area_triangle_1)
#        print(area_triangle_2)
    
    #四边形的总面积
    area_quadrangle=np.around(area_triangle_1+area_triangle_2,2)
    
#        print(area)
    
    return area_quadrangle
          
#判断点是否在四边形内的函数
#pos_P是检测点，ABCD为四边形的四个顶点
def PointInQuadrangle(pos_P,ABCD):

    #重新排列
    ABCD=OrderOfQuadrangle(ABCD)
         
    #转化为数组
    pos_ABCD=[]
    
    for pos in ABCD: 
        pos_ABCD.append(list(pos))
        
#    print(pos_ABCD)  
        
    #转化类型
#    pos_P=np.array(pos_P)
        
#7.9
    
    #分别计算四个三角形的面积
    #临时列表存放ABCD的坐标
    pos_ABCD_temp=ABCD.copy()
    
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
        
#        print(point_list_triangle)
              
        #小三角形的面积的总面积
        total_area_triangle+=AreaTriangle(point_list_triangle)
        
        #测点位于小三角形内部的情况
        list_point_in_triangle.append(PointInTriangle(pos_P,point_list_triangle))
    
    method=2
    
    #方法1:通过四个三角形总面积和四边形面积的关系来判断
    if method==1:
        
        #若小三角形总面积和四边形面积相等，那么说明被检测点在四边形内部
        area_quadrangle=AreaQuadrangle(ABCD)
        
#        print(area_quadrangle)
#        print(total_area_triangle)
#           
        #由于浮点型，两者在小数点后好几位会有所差别，所以需要四舍五入
        if np.round(total_area_triangle-area_quadrangle)==0:
            
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
        
#==============================================================================     
#对layer进行填坑或补齐
def FillGap(plate_up,plate_down,img_rgb,rgb_dict,show=False,output=False):
    
    plates=[plate_up,plate_down]
    
    #被填充的点
    gap=[]
    
    #以下为四个角点
    ABCD=[plate_up.top.bottom_right,\
    plate_down.top.bottom_left,\
    plate_up.top.top_right,\
    plate_down.top.top_left]
    
#    print(ABCD)
    
    #在这四个点横纵坐标的最大范围内进行搜索
    I=[pos[0] for pos in ABCD]
    J=[pos[1] for pos in ABCD]
    
    I_max,I_min=max(I),min(I) 
    J_max,J_min=max(J),min(J)
    
#    print(I_max,I_min,J_max,J_min)
    
    #判断是否在该四边形内部
    for i in range(I_min,I_max+1):
        for j in range(J_min,J_max+1):
#            print(whj.PointInQuadrangle([i,j],ABCD))
            #需要计算一段时间
            if PointInQuadrangle([i,j],ABCD):
                gap.append([i,j])
    
    if show:
        #最顶层的点集合
        content=[]
        
        for this_plate in plates:
            
            content+=this_plate.top.content
            target_tag=this_plate.top.tag
            
        content+=gap    
        
        #print(len(content))
        
        #显示
        ShowSomething(img_rgb,content,target_tag,rgb_dict,output)
    
    return gap    

#7.10
#==============================================================================     
#初始化fault倾角函数
def InitTilt(fault):
    
    #fault边缘点坐标
    I=[pos[0] for pos in fault.edge]
    J=[pos[1] for pos in fault.edge]
    
    #用J检索I
    I_J=dict(zip(I,J))
    
    #边缘集合中两侧存在layer_tag的最高点和最低点
    #由于纵坐标I是自上而下增长的，为描述方便，将其取相反数
    pos_top=np.array([-min(I),I_J[min(I)]])
    pos_bottom=np.array([-max(I),I_J[max(I)]])
    
#    print(pos_bottom)
#    print(pos_top)
    
    #斜率
    k=(pos_top-pos_bottom)[0]/(pos_top-pos_bottom)[1]
    
    #倾角
    tilt=180*np.arctan(abs(k))/np.pi
  
    return tilt,k

#============================================================================== 
#plate对象转化为fractions
def Plate2Fractions(plate):
    
    #将top和others收录进来
    total_fractions=plate.others
    total_fractions.append(plate.top)
    
    return total_fractions

#将plate对象沿着倾角方向切片
#which_layer是被转化的layer
#which_fault是划分上下盘的fault
#width是切片宽度
def Layer2Chip(which_layer,which_fault,width,img_tag):

    #获取fault倾角和斜率
    tilt,k=InitTilt(which_fault)
    
    #取绝对值方便计算
    k=abs(k)
  
    #分别取layer中的最大值和最小值
    I=[pos[0] for pos in which_layer.edge]
    J=[pos[1] for pos in which_layer.edge]

    #分成n段：四边形角落多出一块
    n=int(np.ceil((max(J)-min(J)+(max(I)-min(I))/k)/width))
    
    #chip总坐标列表
    total_chip=[]
    
    #总chip对象列表
    Chip=[]
 
    #大平行四边形四个顶点
    pos_A=[min(I),max(J)+(max(I)-min(I))/k]
    pos_B=[max(I),max(J)]
      
    for m in range(n): 
        
        pos_C=[min(I),pos_A[1]-width]
        pos_D=[max(I),pos_A[1]-width]
        
        ABCD=[pos_A,pos_B,pos_C,pos_D]
        
        #在这四个点横纵坐标的最大范围内进行搜索
        I_quadrangle_point=[pos[0] for pos in ABCD]
        J_quadrangle_point=[pos[1] for pos in ABCD]
        
        I_max=max(I_quadrangle_point)
        I_min=min(I_quadrangle_point)            
        J_max=max(J_quadrangle_point)
        J_min=min(J_quadrangle_point)
        
#        print(I_max,I_min,J_max,J_min)
        
        this_chip=o.chip()
        
        #初始化
        this_chip.k=k
        this_chip.part=m
        this_chip.tilt=tilt
        this_chip.tag=which_layer.tag
        this_chip.inclination=which_fault.inclination
        this_chip.content=[]
            
        #分段有利于提高计算速度
        n_special=np.ceil((max(I)-min(I))/k)
        
        #头尾
        if 0<=n<n_special or n-n_special<=n:
            
            #判断是否在该四边形内部
            for i in range(I_min,I_max+1):
                
                #用斜率联系IJ
                I_offset=i-I_min
                J_offset=I_offset/k
                
                for j in range(int(np.round(J_min-J_offset)),
                               int(np.round(J_max-J_offset)+1)):
                
                    if [i,j] in which_layer.content:
                            this_chip.content.append([i,j])
                            
        #中间
        if n_special<=n<n-n_special:  
           
            for i in range(I_min,I_max+1):
                
                #用斜率联系IJ
                I_offset=i-I_min
                J_offset=I_offset/k
                
                for j in range(int(np.round(J_min-J_offset)),
                               int(np.round(J_max-J_offset)+1)):
                                    
                    if img_tag[i,j]==this_chip.tag:
                        this_chip.content.append([i,j])
                            
            pos_A[1]-=width
            pos_B[1]-=width                                      
            
            #7.11
                     
#            print(len(this_chip.content))
            
            #集合成大列表
            total_chip+=this_chip.content
            Chip.append(this_chip)

    return total_chip,Chip

#8.14
#============================================================================== 
#更新Chip的id函数
def UpdateID(which_Chip):
    
    #初始化哟
    chips_id=1
    
    #逐层更新
    for this_chips in which_Chip.total_chips:
        
        this_chips.id=which_Chip.id+'-'+str(chips_id)
        chips_id+=1
        
#8.12
#==============================================================================        
"""
case1：如果top没有怎么办？连接在同一层的高度
#chips的Init函数有问题，没法得到正确的top和others ok
case2：写一个完整的移动函数
case3：研究收缩和膨胀
#再写一个layer填充函数
case4：给chip也命名？ok
case5：对补充出来的点进行平滑（美观） ok
case6：如何在top缺失的情况下将每一层桥接 ok
#对chips和Chip都建立top和others的chip和chips 
""" 
#多个chip移动函数
def ChipMove(Chip,this_layer):
    
    total_chip=[]
    
    for this_chip in Chip:
        
        if this_chip.content!=[]:
                    
            #对chip对象作移动处理
            I_chip=[pos[0] for pos in this_chip.content]
              
            #移动参照点
            I_layer=[pos[0] for pos in this_layer.edge]
            
            #移动距离
            I_offset_chip=min(I_layer)-min(I_chip)
            
#            print(len(this_chip.content))
#            print(I_offset_chip)
            
            #移动chip
            this_chip.Move(I_offset_chip,0)
            
            total_chip+=this_chip.content
            
    return total_chip,Chip 
           
#==============================================================================     
#写一个plate转化为chip对象的函数
#which_plate是被转化的plate
#which_fault是划分上下盘的fault
#width是切片宽度
def Plate2Chip(which_plate,which_fault,img_tag,width,Chip_id):
    
    #获取fault倾角和斜率
    tilt,k=InitTilt(which_fault)
    
#    print(k)
    
    #分别取layer中的最大值和最小值
    I=[pos[0] for pos in which_plate.content]
    J=[pos[1] for pos in which_plate.content]
    
    #大偏移距(绝对值)
    J_total_offset=(max(I)-min(I))/abs(k)  
    
    #分段有利于提高计算速度：特殊区段
    n_special=int(np.ceil(J_total_offset/width))
    
    #分成n段：四边形角落多出一块
    n=int(np.ceil((max(J)-min(J)+(J_total_offset))/width))
    
#    print(n)
#    print(n_special)
#    print(len(which_plate.content))
    
    #plate中的所偶tag
    tags=[this_fraction.tag for this_fraction in which_plate.Tofractions()]
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
    
    for m in range(n): 
        
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
        
        this_chip=o.chip()
        
        #初始化
        this_chip.k=k
        this_chip.part=m
        this_chip.tilt=tilt
        this_chip.inclination=which_fault.inclination
        this_chip.content=[]
  
        #填充横向点
        if k>0:    
            for JJ in range(int(np.ceil(J_total_offset+J_min)),int(np.ceil(J_max))):   
                
                that_chips_node_quadrangle.append([I_max,JJ-int(np.ceil(J_total_offset))])
                that_chips_node_quadrangle.append([I_min,JJ])
            
        if k<0:        
            for JJ in range(int(np.ceil(J_total_offset+J_min)),int(np.ceil(J_max))):   
                
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
            
            for j in range(start,end):
                
                #根据tag值进行收录
                if img_tag[i,j] in total_tag:   
                    
                    #增加判断条件
                    if [i,j] in which_plate.content:
                        
                        this_chip.content.append([i,j])
        
#        print(len(this_chip.content))     
        
        #计算下一个平行四边形                
        pos_A[1]-=width
        pos_B[1]-=width                                                
        
        #一个chip分成多个chip
        #这一个小四边形中的所有chip
        total_chip=[]
        
        #将this_chip拆成不同tag的多个部分
        for target_tag in total_tag:
            
            that_chip=o.chip()
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
                    
#            print(len(that_chip.content))
                  
            #确保that_chip有点东西才添加它
            if that_chip.content!=[]:
                
                total_chip.append(that_chip)
            
        #建立新的chips对象
        that_chips=o.chips()
        
        #初始化
        that_chips.k=k
        that_chips.part=m
        that_chips.tilt=tilt
        that_chips.total_chip=total_chip      
        that_chips.node_quadrangle=that_chips_node_quadrangle
        that_chips.Init() 
        that_chips.need_to_advanced_regularization=False
        
        #特殊处理区段
        if m<n_special or m>=n-n_special:
            
            #得有点东西吧
            if that_chips.content!=[]:    
                if that_chips.content!=None:                  
                
                        that_chips.need_to_advanced_regularization=True
        
#        #检验一波
#        if that_chips.top!=None:
#            
#            print(that_chips.top.tag)
        
        #添加至chips列表
        total_chips.append(that_chips)
        that_Chip_node_quadrangle+=that_chips_node_quadrangle
        
    #建立新的Chip对象
    that_Chip=o.Chip()
    
    #初始化各属性
    that_Chip.id=Chip_id
    that_Chip.k=k
    that_Chip.tilt=tilt
    that_Chip.total_chips=total_chips
    that_Chip.plate=which_plate
    that_Chip.node_quadrangle=that_Chip_node_quadrangle
    that_Chip.Init()
    that_Chip.UpdateID()
    
    return that_Chip

#Chips表示Chip对象列表
def ShowChips(Chips,img_rgb,rgb_dict,grid='off'):
    
    #显示找到的内容         
    background_rgb=img_rgb[0,0]
    img_temp=np.full(np.shape(img_rgb),background_rgb)
    
    #给像素点赋予rgb值
    for this_Chip in Chips:
         
        #Chip的颜色
        for this_chips in this_Chip.total_chips:
            
            for this_chip in this_chips.total_chip:
                
                for pos in this_chip.content:
                    
                    img_temp[int(pos[0]),int(pos[1])]=rgb_dict[this_chip.tag]
        
        #网格表示
        if grid=='on':
        
            #平行四边形边框
            for pos in this_Chip.node_quadrangle:
                
                img_temp[int(pos[0]),int(pos[1])]=np.array([0,0,0])      
            
    #在图中显示
    plt.figure()
    plt.imshow(img_temp)
    
#8.11
#==============================================================================    
#写一个Chip移动的函数
def ChipRegularization(which_Chip,adjustment=True):
    
    print('')
    
#    print(which_Chip.id)
#    print(which_Chip.top.tag)
#    print(which_Chip.total_tag)  
    
    """第一轮正则化""" 
   #第一步将平行四边形中的点都挪到node_quadrangle顶部    
   #切成chips一个个移动好吧
    for this_chips in which_Chip.total_chips:
       
#        print(len(this_chips.content))
#        print(len(this_chips.node_quadrangle))
          
        #确保平行四边形内有content
        if this_chips.content==None:
            continue
        
        if this_chips.content==[]:
            continue
        
        if this_chips.top.tag!=which_Chip.top.tag:
            continue
        
        if this_chips.need_to_advanced_regularization:    
            continue
        
#        print(this_chips.top.tag)
        
        #横纵坐标
        I_this_chips_content=[pos[0] for pos in this_chips.content]
        I_this_chips_node_quadrangle=[pos[0] for pos in this_chips.node_quadrangle]
        
        #this_chips中的J最高点
        I_this_chips_top_content=min(I_this_chips_content)
        I_this_chips_top_node_quadrangle=min(I_this_chips_node_quadrangle)
        
        #i,j方向上的移动距离
        i_offset=I_this_chips_top_node_quadrangle-I_this_chips_top_content
        j_offset=int(np.floor(-i_offset/which_Chip.k))
        
        this_chips.Move(i_offset,j_offset)
        
        #正则化完成的标志
        this_chips.regularization=True
        
#        print('round 1')
        
    print('......')    
    print('the end of round 1')

    #8.16
 
    """第二轮正则化"""    

    print('')
    
    #通过need_to_advanced_regularization参数计算n_special
    id_list_to_calculate_n_special=[]
    
    for this_chips in which_Chip.total_chips:
        
        if this_chips.need_to_advanced_regularization:
            
            id_list_to_calculate_n_special.append(int(this_chips.id.split('-')[1]))

#    print(id_list_to_calculate_n_special)  
    
    #计算n_special之路
    n_special=id_list_to_calculate_n_special[0]
    
    for k in range(len(id_list_to_calculate_n_special)):    
        
        #判断是否连续
        if id_list_to_calculate_n_special[k]==id_list_to_calculate_n_special[k+1]-1:               
            n_special+=1
        
        #若这种连续中止了
        else:
            break
    
#    print(n_special)

    #8.17
    
    #虽然经过了初始化的处理，但是这几个节点还是需要计算的
    #左区间的起点和终点
    left_external=1
    left_internal=n_special
    
    #右区间的起点和终点
    right_external=id_list_to_calculate_n_special[-1]
    right_internal=id_list_to_calculate_n_special[-1]-n_special+1
 
#    print(left_start,left_end)
#    print(right_start,right_end)
    
    #分段函数,且从某一头取滑动点集
    #分组调试
    
    #左段 
    for this_id in range(left_internal,left_external-1,-1):
        
        SubRegularization(which_Chip,this_id,'right',adjustment)
        
    #右段    
    for this_id in range(right_internal,right_external+1,+1):
        
        SubRegularization(which_Chip,this_id,'left',adjustment)    
    
    """有问题"""
    #中段
    for this_id in range(left_internal,right_internal):
        
        SubRegularization(which_Chip,this_id,'middle',adjustment)

    print('......')    
    print('the end of round 2')

#9.18
#============================================================================== 
"""第一轮正则化""" 
def PreRegularization(which_Chip,this_id):

    #第一步将平行四边形中的点都挪到node_quadrangle顶部    
    #切成chips一个个移动好吧
    this_chips_id=which_Chip.id+'-'+str(this_id)
    
    #找到这个chips
    this_chips=SearchByID([which_Chip],this_chips_id)
    
#        print(len(this_chips.content))
#        print(len(this_chips.node_quadrangle))
          
    #确保平行四边形内有content
    if this_chips.content==None:             
        return
    
    if this_chips.content==[]:
        return
    
    if this_chips.top.tag!=which_Chip.top.tag:
        return
#            
    if this_chips.need_to_advanced_regularization:    
        return
    
#    print(this_chips.top.tag)
    
    #横纵坐标
    I_this_chips_content=[pos[0] for pos in this_chips.content]
    I_this_chips_node_quadrangle=[pos[0] for pos in this_chips.node_quadrangle]
    
    #this_chips中的J最高点
    I_this_chips_top_content=min(I_this_chips_content)
    I_this_chips_top_node_quadrangle=min(I_this_chips_node_quadrangle)
    
    #i,j方向上的移动距离
    i_offset=I_this_chips_top_node_quadrangle-I_this_chips_top_content
    j_offset=int(np.floor(-i_offset/which_Chip.k))
    
    this_chips.Move(i_offset,j_offset)
    
    #正则化完成的标志
    this_chips.regularization=True
    
#    print('round 1')
        
#9.2   

#功能细化
#mode表示左中右
"""第二轮正则化""" 
def SubRegularization(which_Chip,this_id,mode,adjustment):
    
    this_chips_id=which_Chip.id+'-'+str(this_id)
    
    #找到这个chips
    this_chips=SearchByID([which_Chip],this_chips_id)
    
#    print(this_chips.id)
#    print('round 2 '+mode) 

    #确保平行四边形内有content
    if this_chips.content==None or this_chips.content==[]:
        return 
    
    #如果不需要这一步，那就滚吧
    if not this_chips.need_to_advanced_regularization:    
        return 
    
    #调整端点
    if adjustment:
        
        #横纵坐标
        I_this_chips_content=[pos[0] for pos in this_chips.content]
        
        I_this_chips_node_quadrangle=[pos[0] for pos in this_chips.node_quadrangle]
        
        #this_chips中的J最高点
        I_this_chips_top_content=min(I_this_chips_content)
        I_this_chips_top_node_quadrangle=min(I_this_chips_node_quadrangle)
        
        #i,j方向上的移动距离
        i_offset=I_this_chips_top_node_quadrangle-I_this_chips_top_content
        j_offset=int(np.floor(-i_offset/which_Chip.k))
        
        this_chips.Move(i_offset,j_offset)
        
        #正则化完成的标志
        this_chips.regularization=True   
        
    #从这里开始使用chipsNearby函数
    chips_nearby=chipsNearby(which_Chip,this_chips,3,mode)

#    print(len(chips_nearby))
    
    #8.31
    
    #chips_nearby所有的id列表
    chips_nearby_id=[this_near_chips.id for this_near_chips in chips_nearby]

#    print(chips_nearby_id)

    #寻觅chips_nearby的两个端点chips
    chips_nearby_id_int=[int(this_near_chips_id.split('-')[1]) for this_near_chips_id in chips_nearby_id]
    
#    print(chips_nearby_id_int)
    
    #chips_nearby的端点
    limit_chips_nearby=[]
    
    #用于计算limit的content内容
    content_limit_chips_nearby=[]
    
    #chips_nearby内部端点的id
    max_id_internal=which_Chip.id+'-'+str(max(chips_nearby_id_int))
    min_id_internal=which_Chip.id+'-'+str(min(chips_nearby_id_int))
    
    #chips_nearby外部端点的id
    max_id_external=which_Chip.id+'-'+str(max(chips_nearby_id_int)+1)
    min_id_external=which_Chip.id+'-'+str(min(chips_nearby_id_int)-1)
    
    id_limit_chips_nearby=[max_id_internal,min_id_internal,
                           max_id_external,min_id_external]
    
#    print(id_limit_chips_nearby)
    
    #判断存在性
    for this_limit_id in id_limit_chips_nearby:
        
        if SearchByID([which_Chip],this_limit_id) is not None:
            
            #chips上船
            limit_chips_nearby.append(SearchByID([which_Chip],this_limit_id))
            
            #content上船
            if this_limit_id==max_id_external or this_limit_id==min_id_external:
                
                content_limit_chips_nearby+=limit_chips_nearby[-1].content
             
    #检验这几个id好吧
#    print([item.id for item in limit_chips_nearby])
  
    #9.1
    
#    print(len(content_limit_chips_nearby))
    
    #用于计算的threshold
    J_content_limit_chips_nearby=[pos[1] for pos in content_limit_chips_nearby]    
    
    limit=[max(J_content_limit_chips_nearby),min(J_content_limit_chips_nearby)]
    
#    print(limit)
    
    #8.24
    
    #计算相邻chips的所有tag集合
    total_tag_chips_nearby=[]
    
    #计算各层的最高点
    for this_near_chips in chips_nearby:
        
        if len(this_near_chips.content)==0:
            continue
        
        total_tag_this_near_chips=[this_chip.tag for this_chip in this_near_chips.total_chip]
       
        #每个chips的tag集合
        total_tag_chips_nearby+=total_tag_this_near_chips
        
#    print('check 1')
    
    #如果啥都没有那也别玩了
    if total_tag_chips_nearby==[]:
        return 
    
#    print('check 2')
    
    #将其取集合运算并转化为列表
    total_tag_chips_nearby=list(set(total_tag_chips_nearby))
    
#    print(total_tag_chips_nearby)
    
    #更正
    total_tag_this_chips=[]
    
    for this_chip in this_chips.total_chip:
        
        if this_chip.content==[] or this_chip.content==None:
            continue
        
        total_tag_this_chips.append(this_chip.tag)
        
#    print(total_tag_this_chips)    
      
    """权利的交接"""
    import copy
    total_tag_chips_nearby=copy.deepcopy(total_tag_this_chips)
    
    #total_tag对应的下家
    total_tag_chips_nearby_total_chip=[]
    
    #建立不同tag的dict组成的列表  
    for this_tag in total_tag_chips_nearby:
        
        #this_tag在nearby中所有的chip的集合
        this_tag_chips_nearby_total_chip=[]
        
        for this_near_chips in chips_nearby:
            
            this_chip_id=this_near_chips.id+'|'+str(this_tag)
            
#            print(this_chip_id)
            
            this_chip=SearchByID([which_Chip],this_chip_id)            
            this_tag_chips_nearby_total_chip.append(this_chip)
        
        #建立索引:map表示映射关系          
        total_tag_chips_nearby_total_chip.append(this_tag_chips_nearby_total_chip)
        
    #建立map的集合
    total_map=dict(zip(total_tag_chips_nearby,total_tag_chips_nearby_total_chip))
   
#    print(total_map)
#    print(list(total_map.keys()))
    
    #8.25
            
    #用于存储所有的this_tag_top_chips_nearby的列表
    top_total_tag=[]
    
    for this_tag in list(total_map.keys()):
        
        #chips_nearby中每个tag的chip的最高点I的集合    
        I_top_this_tag_chips_nearby=[]
        
        #以及I_J的集合
        I_J_top_this_tag_chips_nearby=[]
        
        for this_chip in total_map[this_tag]:
            
            #确保非空
            if this_chip==None:
                continue         
            
            if this_chip.content!=[] or this_chip.content!=None:

                I_this_chip=[pos[0] for pos in this_chip.content]   
                J_this_chip=[pos[1] for pos in this_chip.content]  
                
                #建立索引
                map_I_J_this_chip=dict(zip(I_this_chip,J_this_chip))
                
                I_top_this_chip=min(I_this_chip)
                J_top_this_chip=map_I_J_this_chip[I_top_this_chip]
                
                I_top_this_tag_chips_nearby.append(I_top_this_chip)
                I_J_top_this_tag_chips_nearby.append([I_top_this_chip,J_top_this_chip])
        
        #8.28
        
#        print(I_top_this_tag_chips_nearby)
#        print(I_J_top_this_tag_chips_nearby)
        
        #如果top_this_tag_chips_nearby为空：不可以让分母为0对吧
        if I_top_this_tag_chips_nearby==[] or I_J_top_this_tag_chips_nearby==[]:
            
            #要添加进列表的值
            top_this_tag=None
        
        #无异常就正常计算  
        #一般情况下使用插值
        else:                           
            top_this_tag=CalculateThisPoint(I_J_top_this_tag_chips_nearby,
                                            'interpolation',
                                            this_chips,
                                            limit)
            #特殊情况下使用平均值
            if top_this_tag==None:
                
                 top_this_tag=CalculateThisPoint(I_J_top_this_tag_chips_nearby,
                                                 'average')
            
        top_total_tag.append(top_this_tag)
        
#    print(top_total_tag)  
    
    #建立this_tag和this_tag_top的索引
    map_total_tag_top=dict(zip(total_tag_chips_nearby,top_total_tag))
  
#    print(list(map_total_tag_top.values()))
#    print(map_total_tag_top)
#    print(this_chips.top.tag)
    
    new_top_this_chips=min(map_total_tag_top.values())
    
    #计算咯
    #计算this_chips各个tag的chip相应的最高I值
    if this_chips.content!=[]:
        
#        print('good')
        
        I_this_chips=[pos[0] for pos in this_chips.content]
        now_top_this_chips=min(I_this_chips)
        
#        print(this_chips.id)
#        print(new_top_this_chips)
#        print(now_top_this_chips)
                  
        #i,j方向上的移动距离
        i_offset=new_top_this_chips-now_top_this_chips
        j_offset=int(np.floor(-i_offset/which_Chip.k))
    
#        print(i_offset,j_offset)
        
        this_chips.Move(i_offset,j_offset)
        
        I_this_chips=[pos[0] for pos in this_chips.content]
        now_top_this_chips=min(I_this_chips)
        
#        print(now_top_this_chips)
        
        #正则化完成的标志
        this_chips.regularization=True         
               
#8.16
#==============================================================================             
#搜索相邻10个参数的函数
#which_Chip表示这件事发生在某个Chip中
#which_chips表示被搜索的chips
#amount表示参与计算的点的数量
#side表示该chips位于整体chips的什么位置
def chipsNearby(which_Chip,which_chips,amount,side):
    
    #计算which_Chip里chips的id上下限
    total_chips_id=[int(this_chips.id.split('-')[1]) for this_chips in which_Chip.total_chips]
    
    #上下限id
    chips_id_max=which_Chip.id+'-'+str(max(total_chips_id))
    chips_id_min=which_Chip.id+'-'+str(min(total_chips_id))
    
#    print(chips_id_max,chips_id_min)
    
    #最终结果得到集合
    chips_nearby=[]
    
    #处理顶部异常的chips
    if which_chips.need_to_advanced_regularization:
        
        start_chips_id=int(which_chips.id.split('-')[1])
        
        #初始化左右id,用split函数分别取id的前后半段
        left_id=which_chips.id.split('-')[0]+'-'+str(start_chips_id)
        right_id=which_chips.id.split('-')[0]+'-'+str(start_chips_id)
        
        #count大于amount时停止
        count=0
        
        #左端的chips们的相应参数由其右端的中间参数集合得到
        if side=='left':
            
            while count<amount:
                            
                left_id=which_Chip.id+'-'+str(int(left_id.split('-')[1])-1)
                
                #到顶了就结束
                if left_id==chips_id_min:
                    break
                
                #前提是他们存在呢
                if SearchByID([which_Chip],left_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],left_id))
                    
#                    print('left')
                    
        #右端的chips们的相应参数由其左端的中间参数集合得到
        if side=='right':
            while count<amount:
                
                right_id=which_Chip.id+'-'+str(int(right_id.split('-')[1])+1)
                
                #到头了就结束
                if right_id==chips_id_max:
                    break
                
                #判断存在这样一个事物
                if SearchByID([which_Chip],right_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],right_id))
                    
#                    print('right')
                    
        #两头增长，数量为amount时停止，取的平均
        if side=='middle':
            while count<amount:
                
                #左右开弓
                left_id=which_Chip.id+'-'+str(int(left_id.split('-')[1])-1)
                right_id=which_Chip.id+'-'+str(int(right_id.split('-')[1])+1)
                
                #到顶了就结束
                if left_id==chips_id_min or right_id==chips_id_max:
                    break
                
                #前提是他们存在呢
                if SearchByID([which_Chip],left_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],left_id))
                    
#                    print('middle-left')
                    
                #判断存在这样一个事物
                if SearchByID([which_Chip],right_id) is not None:
                    
                    count+=1
                    chips_nearby.append(SearchByID([which_Chip],right_id))
                    
#                    print('middle-right')
                    
    return chips_nearby
   
#8.15
#============================================================================== 
#写一个通过id搜索chips的函数
#Chips为本场比赛的Chip集合
def SearchByID(Chips,ID):
    
    #可搜索Chip chips chip
    #搜索Chip
    for this_Chip in Chips:
        if this_Chip.id==ID:
            return this_Chip
    
    #搜索chips    
    if '-' in ID and '|' not in ID:
        for this_Chip in Chips:
            for this_chips in this_Chip.total_chips:
                if this_chips.id==ID:
                    return this_chips
                
    #搜索chip
    if '-' in ID and '|' in ID:
        for this_Chip in Chips:
            for this_chips in this_Chip.total_chips:
                for this_chip in this_chips.total_chip:
                    if this_chip.id==ID:
                        return this_chip

#8.25
#============================================================================== 
#计算列表平均值的函数
def GetAverage(which_data):
    sum_data=0
        
    for item in which_data:
        sum_data+=item
        
    return sum_data/len(which_data)
    
#计算列表中位数的函数
def GetMedian(which_data):
    
    data=sorted(which_data)
    size=len(which_data)
    
    #判断列表长度为偶数
    if size%2==0:   
        return (data[size//2]+data[size//2-1])/2
    
    #判断列表长度为奇数    
    if size%2==1:   
        return data[(size-1)//2]     
                 
#计算某点某特征值的函数
#which_data表示需要计算的集合
#mode表示计算的模式：average表示平均值，median表示中位数，interpolation表示插值  
#which_chips表示需要计算高度的那个chips
#threshold表示用于计算的自变量的取值范围            
def CalculateThisPoint(which_data,mode,which_chips=None,threshold=None):
    
    #还原成相应的I坐标
    I_which_data=[pos[0] for pos in which_data]
    J_which_data=[pos[1] for pos in which_data]
    
    #平均值
    if mode=='average':
        return int(np.round(GetAverage(I_which_data)))
    
    #中位数
    if mode=='median':
        return int(np.round(GetMedian(I_which_data)))
    
    """插值比较特殊：可能需要提供坐标？？？"""
    #插值
    if mode=='interpolation':
        
#        print(threshold)
#        print('......')
#        
#        print(which_data)        
#        print('......')
#
#        print(which_chips.content)
#        print('......')
#        
#        print(len(which_chips.content))
#        print('......')
#     
#        print(GetInterpolation(which_data,threshold))
#        print('......')
#        
#        print(len(GetInterpolation(which_data,threshold)))       
#        print('......')
             
        result_interpolation=GetInterpolation(which_data,threshold)
        
        result_final=CrossDataAB(which_chips.content,result_interpolation)
        
#        print(result_final)
#        print('......')
        
        #9.2
        
        """若结果不止一个，或为0，如何处理？？"""        
        #结果为空
        if len(result_final)==0:
            
            #neighbor大法好 
            #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
            neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
            
            #遍历插值结果
            for pos in result_interpolation:
             
                #逆时针遍历邻域内的点
                for item in neighbordict:
                    
                    #遍历新的坐标            
                    new_pos=[pos[0]+item[0],pos[1]+item[1]]
                    
                    if new_pos in which_chips.content: 
                        
                        if new_pos not in result_final:
                            
                            result_final.append(new_pos)     
                            
        #结果不止一个
        if len(result_final)>1:
            
            #计算which_data的中心
            center_which_data=[np.mean(I_which_data),np.mean(J_which_data)]
            
            #中心到各个result的距离
            distance_center2result=[Distance(this_pos,center_which_data) for this_pos in result_final]
        
            #距离和result建立键值对
            map_distance_center2result=dict(zip(distance_center2result,result_final))
            
            #返回距离最小的哥
            result_final=[map_distance_center2result[min(distance_center2result)]]
        
        #结果就一个,返回其I坐标 
        if len(result_final)==1:
                
#            print(result_final[0])
        
            return result_final[0][0]
        
        else:
            return None

#8.29
        
"""以下部分为计算插值系列函数"""
#二次函数的标准形式
def func(params,x):
    
    a,b,c=params
    
    return a*x**2+b*x+c

#误差函数，即拟合曲线所求的值与实际值的差
def error(params,x,y):
    return func(params,x)-y

#对参数求解
def slovePara(X,Y):
    
    #p0里放的是a、b、c的初始值，这个值可以随意指定。
    #往后随着迭代次数增加，a、b、c将会不断变化，使得error函数的值越来越小。
    p0=[10,10,10]
    
    from scipy.optimize import leastsq
    #leastsq的返回值是一个tuple
    #它里面有两个元素，第一个元素是a、b、c的求解结果，第二个则为cost function的大小！
    Para=leastsq(error,p0,args=(X,Y))
    
    return Para
    
#which_data表示参与的坐标
#threshold是拟合出的曲线的自变量上下限列表
def GetInterpolation(which_data,threshold,show=False):
    
    #转化为一维列表
    I_which_data=[pos[0] for pos in which_data]
    J_which_data=[pos[1] for pos in which_data]
    
    #z幻化为np.array对象，便于处理：X为自变量，Y为因变量 
    X=np.array(J_which_data)
    Y=np.array(I_which_data)

    Para=slovePara(X,Y)
    a,b,c=Para[0]
    
#    print(a,b,c)   
 
    #在threshold范围内直接画100个连续点
    amount=max(threshold)-min(threshold)+1
    x=np.linspace(min(threshold),max(threshold),amount) 

#    print(amount)
    
    #函数式
    y=a*x*x+b*x+c 
    
    #是否输出图形
    if show:
        
        #保留两位小数
        a=float('%0.2f'%a)
        b=float('%0.2f'%b)
        c=float('%0.2f'%c)
        
        print("a=",a,"b=",b,"c=",c)
        print("cost:" + str(Para[1]))
        print("求解的曲线是:")
        print("y="+str(round(a,2))+"x*x+"+str(round(b,2))+"x+"+str(c))
    
        plt.figure(figsize=(8,6))
        plt.scatter(X,Y,color="green",label="sample data",linewidth=2)
    
        #画拟合直线
        plt.plot(x,y,color="red",label="solution line",linewidth=2)
        
        #绘制图例
        plt.legend() 
        plt.show()
    
    #输出x和y组成的坐标集合
    return CombineXY(y,x)
 
"""拿抛物线和chip作一个交集的运算"""

#8.30 

#定义一个组合对应位置x和y坐标的函数
#to_int表示是否取整,默认为True
def CombineXY(x,y,to_int=True):
    
    #转为列表
    list(x),list(y)
    
    #输出结果的列表
    that_data=[]
    
    for k in range(len(x)):
        
        #如果取整
        if to_int:    
            that_x=int(np.round(x[k]))
            that_y=int(np.round(y[k]))
        
        else:
            that_x=x[k]
            that_y=y[k]
            
        that_data.append([that_x,that_y])
        
    return that_data

#定义过(x0,y0),斜率为k的像素点集合
#threshold是自变量取值范围[x_min,x_max]
def GenerateLineList(x0,y0,k,threshold):
         
    #自变量x的取值范围为
    x=np.linspace(min(threshold),max(threshold),max(threshold)-min(threshold)+1) 
    y=(x-x0)*k+y0
    
    return CombineXY(x,y)

#计算集合data_A和data_B交集
def CrossDataAB(data_A,data_B):
    
    #结果列表
    data_cross=[]
    
    for pos in data_A:
        if pos in data_B:
            data_cross.append(pos)
    
    return data_cross

#计算chips和曲线的交集坐标
#parameters表示多项式的系数集合
"""其实不用专门写这一个函数"""
def Convey(chips,data_curve):
    
    #chips的content和data_curve的交集
     return CombineXY(chips.content,data_curve) 
 
#==============================================================================        
#更新Chip的top
def ChipUpdateTop(which_Chip):

#    print(which_Chip.total_tag)
    
    #top不可以是fault
    if -1 in which_Chip.total_tag:
        which_Chip.total_tag.remove(-1)
    
    #所有tag的高度
    total_tag_top=[]
    
    #所有tag的fraction
    total_tag_fraction=[]
    
    for this_tag in which_Chip.total_tag:
        
        this_tag_fraction=o.fraction()
        this_tag_content=[]
        
        for this_chips in which_Chip.total_chips:

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
    map_top_total_tag=dict(zip(total_tag_top,which_Chip.total_tag))
    
    #total_tag和content的索引
    map_total_tag_fraction=dict(zip(which_Chip.total_tag,total_tag_fraction))  
          
    #求目标tag值
    target_tag=map_top_total_tag[min(total_tag_top)]   
    
#    print(target_tag)
    
    #更新top
    top_content=[]
    
    for this_chips in which_Chip.total_chips:
        
        for this_chip in this_chips.total_chip:
            
            if this_chip.tag==target_tag:
                
                top_content+=this_chip.content
    
    #定义top
    which_Chip.top=o.fraction()
    which_Chip.top.content=top_content
    which_Chip.top.tag=target_tag
    
    #移除top
    del map_total_tag_fraction[map_top_total_tag[min(total_tag_top)]]

    #定义pthers
    which_Chip.others=list(map_total_tag_fraction.values())
    
    #检验模块
#    print(which_Chip.top.tag)
#    
#    for this_fraction in which_Chip.others:
#        print(this_fraction.tag)
    
#9.6
#==============================================================================     
"""把开闭运算的结果坐标存在列表里并设置背景色"""
#target为前景的灰度值
#腐蚀运算
#由像素点计算的情况
def ImgErode(img,target):
    
    #逆时针遍历邻域内的点
    #领域核
    neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
    neighbordict.remove((0,0))

    #背景tag
    background_tag=img[0,0]
    new_img_tag=np.full(np.shape(img),background_tag)
    
    for i in range(np.shape(img)[0]):
        
        for j in range(np.shape(img)[1]):  
            
            #仅作用于前景
            if img[i,j]==target:
                    
                neighbor=[]    
        
                #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
                for item in neighbordict:
                    
                    #遍历新的坐标
                    new_i=i+item[0]
                    new_j=j+item[1]
                    
                    if 0<=new_i<np.shape(img)[0] and 0<=new_j<np.shape(img)[1]:
                        
                        neighbor.append(img[new_i,new_j])
                    else:
                        neighbor.append(None)
                        
                #领域值是否都相等        
                if neighbor==[img[i,j]]*len(neighbor):
                    
                    new_img_tag[i,j]=img[i,j]
                    
    #计算结果
    result_content=[]
                
    for i in range(np.shape(new_img_tag)[0]):
        
        for j in range(np.shape(new_img_tag)[1]): 
            
            #加入列表当中   
            if new_img_tag[i,j]==target:
                
                result_content.append([i,j])
                
    return new_img_tag,result_content
    
#由content计算    
def ContentErode(content):   
    
    #逆时针遍历邻域内的点
    #领域核
    neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
    neighbordict.remove((0,0))

    #计算后的结果列表
    new_content=[]
    
    for pos in content:
        
        neighbor=[]    
        
        #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
        for item in neighbordict:
            
            #遍历新的坐标
            new_i=pos[0]+item[0]
            new_j=pos[1]+item[1]
            
            #前提是这个点的位置是有效的
            if [new_i,new_j] in content:
                
                neighbor.append(True)          
            else:
                neighbor.append(False)
                
        #领域值是否都相等        
        if neighbor==len(neighbor)*[True]:
            
            new_content.append(pos)
            
    return new_content
    
#img膨胀运算
def ImgExpand(img,target):
    
    #逆时针遍历邻域内的点
    #领域核
    neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
    neighbordict.remove((0,0))
    
    #背景tag
    background_tag=img[0,0]
    new_img_tag=np.full(np.shape(img),background_tag)
    
    for i in range(np.shape(img)[0]):
        
        for j in range(np.shape(img)[1]):  
          
            #仅作用于前景
            if img[i,j]==target:
                new_img_tag[i,j]=img[i,j]
                
                #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
                for item in neighbordict:

                    #遍历新的坐标
                    new_i=i+item[0]
                    new_j=j+item[1]
                    
                    #重复赋值                
                    if 0<=new_i<np.shape(img)[0] and 0<=new_j<np.shape(img)[1]:
                        
                        new_img_tag[new_i,new_j]=img[i,j]
                            
    #计算结果
    result_content=[]
                
    for i in range(np.shape(new_img_tag)[0]):
        
        for j in range(np.shape(new_img_tag)[1]): 
            
            #加入列表当中   
            if new_img_tag[i,j]==target:
                
                result_content.append([i,j])
                
    return new_img_tag,result_content
    
 
#content膨胀运算
def ContentExpand(content):
    
    #逆时针遍历邻域内的点
    #领域核
    neighbordict=[(i,j) for i in [-1,0,1] for j in [-1,0,1]]
    neighbordict.remove((0,0))
    
    #膨胀操作后的结果
    new_content=[]
    
    for pos in content:
        
        #[i,j-1],[i+1,j-1],[i+1,j],[i+1,j+1],[i,j+1],[i-1,j+1],[i-1,j],[i-1,j-1]
        for item in neighbordict:
            
            #遍历新的坐标
            new_i=pos[0]+item[0]
            new_j=pos[1]+item[1]
            
            #增加新的点儿
            if [new_i,new_j] not in content:
                
                new_content.append([new_i,new_j])
                        
    #增加new_content
    new_content+=content
            
    return new_content

#9.19
#==============================================================================     
#target_tag为要做处理的tag
#n为迭代次数
#由像素矩阵计算   
#结构闭运算
def ImgClose(img_rgb,rgb_dict,background_rgb,target_tag,n,show=False):
    
    #转化为单通道
    new_img_tag=RGB2Tag(img_rgb,rgb_dict)
 
#    print(np.shape(new_img_tag))
    
    #初始化new_content
    new_content=[]
    
    for i in range(np.shape(new_img_tag)[0]):
        
        for j in range(np.shape(new_img_tag)[1]):
            
            if new_img_tag[i,j]==target_tag:
                
                new_content.append([int(i),int(j)])
    
    #必须有执行次数.若n=0，则不执行咯
    if n:   
        #先膨胀
        for k in range(n):    
            new_img_tag,new_content=ImgExpand(new_img_tag,target_tag)
    
        #后侵蚀
        for k in range(n):
            new_img_tag,new_content=ImgErode(new_img_tag,target_tag)    
         
    #    print(np.shape(new_img_rgb))
    
    #着色
    new_img_rgb=np.full(np.shape(img_rgb),background_rgb)

    for pos in new_content:    
        new_img_rgb[pos[0],pos[1]]=rgb_dict[target_tag]
        
    #显示计算结果
    if show:
        plt.figure()
        plt.imshow(new_img_rgb)
 
    return new_img_rgb,new_content
    
#由列表计算    
def ContentClose(content,n,show=False):    

    #先膨胀
    for k in range(n):    
        content=ContentExpand(content)

    #后侵蚀
    for k in range(n):
        content=ContentErode(content)    
        
    return content
        
#结构开运算
#由像素矩阵计算    
def ImgOpen(img_rgb,rgb_dict,background_rgb,target_tag,n,show=False):
    
    #转化为单通道
    new_img_tag=RGB2Tag(img_rgb,rgb_dict)
    
    #初始化new_content
    new_content=[]
    
    for i in range(np.shape(new_img_tag)[0]):
        
        for j in range(np.shape(new_img_tag)[1]):
            
            if new_img_tag[i,j]==target_tag:
                
                new_content.append([int(i),int(j)])
    
    #必须有执行次数.若n=0，则不执行咯
    if n:
        #先侵蚀
        for k in range(n):
            new_img_tag,new_content=ImgErode(new_img_tag,target_tag)
            
        #后膨胀
        for k in range(n):    
            new_img_tag,new_content=ImgExpand(new_img_tag,target_tag)   
      
    #着色
    new_img_rgb=np.full(np.shape(img_rgb),background_rgb)
    
    for pos in new_content:    
        new_img_rgb[pos[0],pos[1]]=rgb_dict[target_tag]
        
    #显示计算结果
    if show:
        plt.figure()
        plt.imshow(new_img_rgb)
 
    return new_img_rgb,new_content

#由列表计算    
def ContentOpen(content,n,show=False):     
    
    #先侵蚀
    for k in range(n):
        content=ContentErode(content)
        
    #后膨胀
    for k in range(n):    
        content=ContentExpand(content) 
        
    return content
    
#9.7
#==============================================================================     
"""如何变得好看，平滑？闭运算？"""
#对Chips集合进行高度校正
#extent表示闭运算的程度
def ChipsRegularization(CHIP_1,CHIP_2,img_rgb,rgb_dict,extent=0,show=False,output=True):
    
    #将Chip分别正则化
    CHIP_1.Regularize()
    CHIP_2.Regularize()
    
    #矫正CHIPS的总高度
#    I_top_1=min([pos[0] for pos in CHIP_1.content])
#    I_top_2=min([pos[0] for pos in CHIP_2.content])
#    
    #两偏移距与高度的差之和为恒定值
#    I_offset_1=int(np.round((I_top_2-I_top_1)/2))
#    I_offset_2=int(I_top_1-I_top_2+I_offset_1)
    
#    print(I_top_1,I_top_2)
#    print(I_offset_1,I_offset_2)
    
#    CHIP_1.Move(I_offset_1,0)
#    CHIP_2.Move(I_offset_2,0)

    #更新顶层
    CHIP_1.UpdateTop()
    CHIP_2.UpdateTop()
    
    if show:
        
        #显示fraction集合
        img_rgb_top=ShowFractions([CHIP_1.top,CHIP_2.top],img_rgb,rgb_dict,output=True)
        
#        print(np.shape(img_rgb_top))
        
        #闭运算
        ImgClose(img_rgb_top,rgb_dict,img_rgb[0,0],CHIP_1.top.tag,extent,show)
    
    return CHIP_1,CHIP_2

"""
case 1：top消失的函数 ok
case 2：将others融入top的函数 ok
case 3：自动识别下一个fault的函数 手动勾选
case 4：定义类的侵蚀和膨胀函数 ok
"""

#==============================================================================  
#在Chip对象当中DeleteTop
#extent表示Close的次数
def DeleteTop(which_Chip,extent=0,show=False):
    
#    print(which_Chip.top.tag)
    
    for this_chips in which_Chip.total_chips:
        
        for this_chip in this_chips.total_chip:
            
#            print('this chip tag is')
#            print(this_chip.tag)
            
            if this_chip.tag==which_Chip.top.tag:
                
                this_chips.total_chip.remove(this_chip)
    
#        print(this_chips.total_chip)
        
        this_chips.Init()
        
#        print(this_chips.total_chip)
#        print(this_chips.content)
 
    #更新一波   
    which_Chip.Init()
    
#    #使用前
#    if show:   
#        which_Chip.top.Show(img_rgb,rgb_dict)

    #top的内容
    top_content=ContentClose(which_Chip.top.content,extent)

    top_fraction=o.fraction()
    top_fraction.content=top_content
    top_fraction.tag=which_Chip.top.tag
    
    which_Chip.top=top_fraction
    
    #fault的内容
    fault_content=ContentClose(which_Chip.fault_content,extent)
    
    fault_fraction=o.fraction()
    fault_fraction.content=fault_content
    fault_fraction.tag=-1
    
#    #使用后
#    if show:
#        which_Chip.top.Show(img_rgb,rgb_dict)

    """输出新的top和fault，若新的layer不止一层需要修改成新的对象"""
    
    #先输出top后输出fault，避免覆盖
    return [top_fraction,fault_fraction]

#9.17
    
#增加底色并修改尺寸
#i_bottom为画布的底部i坐标，默认为0
def AddBase(img_tag,i_bottom):
    
    import copy
    new_img_tag=copy.deepcopy(img_tag)
    
    #每一列，自下而上遍历
    for j in range(np.shape(img_tag)[1]):
        
        for i in range(np.shape(img_tag)[0]-1,i_bottom,-1):
            
            #找到奇怪的点
            if img_tag[i,j]!=0:

                #全用base_tag替代
                new_img_tag[i:i_bottom,j]=np.array([-2]*len(img_tag[i:i_bottom,j]))
                
                break
      
    return new_img_tag

#在画布上画上这些fraction的content
#计算top基底和断层矩阵的函数
#简单模型：仅有TopBaseFault各一个的情况
def TopBaseFault(Chips,img_tag,rgb_dict,extent,i_bottom):
   
    #新的输出矩阵
    new_img_tag=np.zeros(np.shape(img_tag))
    
    for this_Chip in Chips:
        
        #删除Top
        top_fraction,fault_fraction=DeleteTop(this_Chip,extent)

        #先画top
        for pos in top_fraction.content:
            
            new_img_tag[int(pos[0]),int(pos[1])]=top_fraction.tag
        
    #再根据top的位置绘制base
    new_img_tag=AddBase(new_img_tag,i_bottom)
    
    #最后绘制fault
    for pos in fault_fraction.content:
        
        new_img_tag[pos[0],pos[1]]=top_fraction.tag
        
    return new_img_tag

#============================================================================== 
#修改tag矩阵的尺寸
#i_top表示顶部留白，默认为0
#即删除空白
def FitSize(img_tag,i_top=0,show=False):
    
    #遍历：寻找图像的上下左右边界
    
    #上
    for i in range(np.shape(img_tag)[0]):   
  
        if list(img_tag[i,:])!=[0]*len(img_tag[i,:]):
     
            top=i
            
            break
        
    #下
    for i in range(np.shape(img_tag)[0]-1,0,-1):  
        
        if list(img_tag[i,:])!=[0]*len(img_tag[i,:]):
     
            bottom=i
            
            break 
        
    #左
    for j in range(np.shape(img_tag)[1]):  
        
        if list(img_tag[:,j])!=[0]*len(img_tag[:,j]):
     
            left=j
            
            break
        
    #左    
    for j in range(np.shape(img_tag)[1]-1,0,-1):
        
        if list(img_tag[:,j])!=[0]*len(img_tag[:,j]):

            right=j
            
            break
        
#    print(left,right,top,bottom)
     
    #显示模块
    if show:
        
        plt.figure()
        plt.imshow(img_tag[top-i_top:bottom+1,left:right+1])
        plt.axis('off')
        
    return img_tag[top-i_top:bottom+1,left:right+1]

#计算当下长度
def CalculateLength(img_rgb,rgb_dict,show=False):

    img_tag=FitSize(RGB2Tag(img_rgb,rgb_dict))
    img_rgb=np.array(Tag2RGB(img_tag,rgb_dict),dtype=np.uint8)
    
    #显示模块
    if show:
        
        plt.figure()
        plt.imshow(img_rgb)
        #plt.axis('off')

    return np.shape(img_rgb)[1]

"""
1 os.path.exists(path) 判断一个目录是否存在
2 os.makedirs(path) 多层创建目录
3 os.mkdir(path) 创建目录
"""
#11.12
#============================================================================== 
#在某路径下判断并创建文件夹
def GenerateFold(path):
    
    #引入模块
    import os
 
    #去除首位空格
    path=path.strip()
    
    #去除尾部\符号
    path=path.rstrip("\\")
 
    #判断路径是否存在(True/False)
    Exist=os.path.exists(path)
 
    #判断结果
    if not Exist:
        
        #如果不存在则创建目录
        #创建目录操作函数
        os.makedirs(path) 
        
#9.26
#============================================================================== 
#打印计算结果
#unit:像素点与长度换算单位
#save_path:保存路径
def PrintResult(save_path,unit,length_before,length_now):
    
    #判断并创建文件夹
    GenerateFold(save_path)
    
    #将计算结果写入result.txt文件
    with open(save_path+'\\'+"result.txt","w") as file:
        
        file.write('原始长度：%5.2fkm'
                   %(length_before/unit))
        
        file.write('\n')
        
        file.write('当下长度：%5.2fkm'
                   %(length_now/unit))
        
        if length_before>length_now:
            
            file.write('\n')
            file.write('缩短量：%5.2fkm'
                       %(float(length_before-length_now)/unit))
            
            file.write('\n')
            file.write('缩短率：%5.2f%%'
                       %(float(length_before-length_now)/unit/length_now*100))
    
        if length_before<length_now:
            
            file.write('\n')
            file.write('拉张量：%5.2fkm'
                       %-(float(length_before-length_now)/unit))
            
            file.write('\n')
            file.write('拉张率：%5.2f%%'
                       %-(float(length_before-length_now)/unit/length_now*100))
    
            
    print('')
    
    print('原始长度：%5.2fkm'%(length_before/unit))
    print('当下长度：%5.2fkm'%(length_now/unit))
    
    if length_before>length_now:
    
        print('缩短量：%5.2fkm'
              %(float(length_before-length_now)/unit))
        
        print('缩短率：%5.2f%%'
              %(float(length_before-length_now)/unit/length_now*100))
    
    if length_before<length_now:
        
        print('拉张量：%5.2fkm'
              %-(float(length_before-length_now)/unit))
        
        print('拉张率：%5.2f%%'
              %-(float(length_before-length_now)/unit/length_now*100))
           
#10.18        
#==============================================================================         
#根据新的keys排布dict
def DictOrderByKeys(which_dict,new_keys):
    
    #先判断keys和dict的keys是否相同
    if list(set(new_keys))!=list(set(which_dict.keys())):
        
        print('ERROR:invalid keys')
    
        return 
    
    #正常情况下
    if list(set(new_keys))==list(set(which_dict.keys())):
        
        #建立新的values列表
        new_values=[which_dict[this_key] for this_key in new_keys]
        
    new_dict=dict(zip(new_keys,new_values))
    
    return new_dict
    
#根据新的values排布dict
def DictOrderByValues(which_dict,new_values):
    
    #先判断keys和dict的keys是否相同
    if list(set(new_values))!=list(set(which_dict.values())):
        
        print('ERROR:invalid values')
        
        return
    
    #正常情况下
    if list(set(new_values))==list(set(which_dict.values())):
        
        #建立新的keys列表
        new_keys=[DictKeyOfValue(which_dict,this_value) for this_value in new_values]
        
    new_dict=dict(zip(new_keys,new_values))
    
    return new_dict

#10.17
#============================================================================== 
#写一个把像素点网上推的函数
#img_tag位输入的tag矩阵
def PushUpImg(img_tag):
    
    #基底tag
    base_tag=GetBaseTag(img_tag)
    
    #空白tag
    blank_tag=0
    
    #建立新的img_tag
    new_img_tag=np.zeros((np.shape(img_tag)[0],np.shape(img_tag)[1]))
    
    for column in range(np.shape(img_tag)[1]):
        
        #所有的tag
        tag_list=list(set(list(img_tag[:,column])))
        
        #tag对应的depth列表
        depth_list=[]
        
        #遍历所有tag及其深度
        for this_tag in tag_list:
            
            that_depth=np.mean(list(np.where(img_tag[:,column]==this_tag)))
            
            depth_list.append(that_depth)
         
        #tag与深度建立索引
        map_tag_depth=dict(zip(tag_list,depth_list))

        #深度list,从小到大来排列
        new_depth_list=sorted(depth_list,reverse=False)
        
#        print(map_tag_depth)
#        print(new_depth_list)
        
#        print(list(map_tag_depth.keys()))
#        print(list(map_tag_depth.keys())==tag_list)
        
        #重组dict
        new_map_tag_depth=DictOrderByValues(map_tag_depth,new_depth_list)
        
#        print(new_map_tag_depth)
        
        #得到了新的tag列表
        new_tag_list=list(new_map_tag_depth.keys())
        
#        print(new_tag_list)
        
        #各个tag的数量
        map_tag_frequency=List2FrequencyDict(img_tag[:,column])
        
#        print(map_tag_frequency)
        
        #频率列表
#        frequency_list=list(map_tag_frequency.values())
        
#        print(frequency_list)

        """把白色换掉？？"""
        if base_tag in new_tag_list and blank_tag in new_tag_list:
            
#            print(map_tag_frequency[base_tag])
#            print(map_tag_frequency[blank_tag])
            
            #把blank贴到base  
            map_tag_frequency[base_tag]+=map_tag_frequency[blank_tag]
            
            #把空白抹掉
            map_tag_frequency.pop(blank_tag)
            
#        print(column)   
#        print(map_tag_frequency)
#        print(map_tag_frequency.keys())
        
        #新的列
        new_content=[]
        
        #重新排布
        for this_tag in list(map_tag_frequency.keys()):
         
            new_content+=map_tag_frequency[this_tag]*[this_tag]
                
#        print(len(new_content))
#        print(np.shape(new_img_tag)[0])
#        
#        print(len(new_content)==np.shape(new_img_tag)[0])
        
        #数量不符合就不和他玩了
        if len(new_content)!=np.shape(new_img_tag)[0]:
            
            print('ERROR:invalid column')
        
            return 
        
        #正常情况下
        if len(new_content)==np.shape(new_img_tag)[0]:
            
            #新的列应当是这样的
            new_img_tag[:,column]=new_content
        
    return new_img_tag   
     
#10.18
#============================================================================== 
#点击拾取fractions对象并生成plate对象
#total_fractions表示图像中的所有fraction对象
def PickAndGeneratePlate(total_fractions,img_rgb):

    print('')
    print('here comes a new plate')
    
    #建立fractions的content
    Content=[]
    
    #建立pos总集合
    for this_fraction in total_fractions:
        
        Content+=this_fraction.content
    
    #这个plate中所有的fractions
    that_fractions=[]
    
    count=0
    
    import copy
    
    #像素矩阵
    img_rgb_temp=copy.deepcopy(img_rgb)
    
    #循环呗
    while True:
        
        print('......')
        print('please pick the layer')
        
        #点击获取像素点坐标
        layer_point_pos=plt.ginput(1)[0]
        
        #注意反过来，因为是xy坐标
        pos_xy=[int(layer_point_pos[0]),int(layer_point_pos[1])]
        
        pos_IJ=copy.deepcopy(pos_xy)
        
        #IJ形式是xy形式的颠倒
        pos_IJ.reverse()
        
    #    print('......')
    #    print(pos_IJ)
                
        #如果点到外面，此plate的fraction提取结束
        if pos_IJ not in Content:
            
            print('......')
            print('layer picking of this plate is over')
            
            break
        
        #判断这个坐标合理与否
        for this_fraction in total_fractions:
                
            #判断他在哪
            if pos_IJ in this_fraction.content:
                
                #且不在已收录的fraction对象集中
                if this_fraction in that_fractions: 
                    
                    print('......')
                    print('this layer is already picked')
                    
                    break
                    
                if this_fraction not in that_fractions:
                    
                    count+=1
            
                    print('......')
                    print('picking the layer'+''+str(count))
                    
                    ShowEdge(this_fraction,img_rgb_temp)
                    
                    that_fractions.append(this_fraction)
                    
                    break
                
    #显示一下呗
    plt.figure()
    plt.imshow(img_rgb_temp)

    #生成的plate对象
    that_plate=o.plate()
    
    #初始化
    that_plate.Init(that_fractions)
    
    return that_plate

#============================================================================== 
#表示chips和中点坐标对应关系的键值对
#axis：'both','I','J'分别表示行列索引，行索引，列索引
def MapCenterchipsOf(which_Chip,axis):

    map_J_total_chips={}
    
    for this_chips in which_Chip.total_chips:
        
        if this_chips.center!=None:
            
            #以下两句意思一样的
#            map_J_total_chips.update({this_chips:this_chips.center[1]})
#            map_J_total_chips[this_chips]=this_chips.center[1]   
             
            #行索引
            if axis is 'I':
                
                map_J_total_chips[this_chips]=this_chips.center[0] 
                
            #列索引
            if axis is 'J':
                
                map_J_total_chips[this_chips]=this_chips.center[1] 
                
            #列索引
            if axis is 'both':
                
                map_J_total_chips[this_chips]=this_chips.center
            
#    print(map_J_total_chips)
    
    return map_J_total_chips

#返回两端的chips
#side表示边，有'left'和'right'两个选项
def chipsOf(which_Chip,side):
    
    #先建立键值对
    #根据values的值返回chips对象
    map_J_total_chips=MapCenterchipsOf(which_Chip,'J')
    
    #最左的即J最小的chips
    if side is 'left':
    
        return DictKeyOfValue(map_J_total_chips,min(list(map_J_total_chips.values())))

    #最右的即J最大的chips
    if side is 'right':
    
        return DictKeyOfValue(map_J_total_chips,max(list(map_J_total_chips.values())))

#which_chips中行索引最小的所有pos集合
def TopIPosIn(which_chips):
    
    #求最高点的所有坐标
    I_which_chips=[pos[0] for pos in which_chips.content]
    
#    print(I_which_chips)
    
    top_I_which_chips=min(I_which_chips)
    
#    print(top_I_which_chips)
#    print(which_chips.content)
    
    #返回这一行中所有满足top的点
    top_I_pos_in_which_chips=[pos for pos in which_chips.content if pos[0]==top_I_which_chips]
    
#    print(top_I_pos_in_which_chips)

    return top_I_pos_in_which_chips

#返回左右chips的距离最近的两个点  
#side表示左右chips
def SpecialPointOf(which_chips,side):
    
    #先求which_chips中行索引最小的所有pos集合
    top_I_pos_in_which_chips=TopIPosIn(which_chips)
    
#    print(top_I_pos_in_which_chips)
    
    #求他们的行列索引集合
    I_top_I_pos_in_which_chips=[pos[0] for pos in top_I_pos_in_which_chips]
    J_top_I_pos_in_which_chips=[pos[1] for pos in top_I_pos_in_which_chips]
    
#    print(I_top_I_pos_in_which_chips)
#    print(J_top_I_pos_in_which_chips)
    
    #建立索引呗
    map_JI_top_I_pos_in_which_chips=dict(zip(J_top_I_pos_in_which_chips,I_top_I_pos_in_which_chips))
    
#    print(map_JI_top_I_pos_in_which_chips)
    
    #max在右
    if side is 'right':
        
        special_point=[map_JI_top_I_pos_in_which_chips[max(J_top_I_pos_in_which_chips)],max(J_top_I_pos_in_which_chips)]
    
    #min在左
    if side is 'left':
        
        special_point=[map_JI_top_I_pos_in_which_chips[min(J_top_I_pos_in_which_chips)],min(J_top_I_pos_in_which_chips)]
        
#    print(special_point)
    
    return special_point
    
#将Chips对象聚合在一起
#先处理两个Chip对象
def Cohere(Chips):
    
    #根据中点来判断
    J_center_Chips=[this_Chip.center[1] for this_Chip in Chips]
    
    #建立Chip和J值的索引关系
    map_J_center_Chips=dict(zip(Chips,J_center_Chips))

    #min在左
    Chip_left=DictKeyOfValue(map_J_center_Chips,min(list(map_J_center_Chips.values())))
    
    #max在右
    Chip_right=DictKeyOfValue(map_J_center_Chips,max(list(map_J_center_Chips.values())))
   
#    print(Chip_left.center)
#    print(Chip_right.center)
    
    #取Chip_left中最右的
    chips_left=chipsOf(Chip_left,'right')
    
    #取Chip_right中最左的
    chips_right=chipsOf(Chip_right,'left')

#    print(chips_right,chips_left)
    
    #根据其坐标进行移动
#    print(chips_right.center)
#    print(chips_left.center)
#    
#    print(chips_right.content)
#    print(chips_left.content)

    I_offset=SpecialPointOf(chips_right,'left')[0]-SpecialPointOf(chips_left,'right')[0]
    J_offset=SpecialPointOf(chips_right,'left')[1]-SpecialPointOf(chips_left,'right')[1]
    
#    print(I_offset,J_offset)
    
    #左右盘的位移
    I_offset_left=int(np.floor(I_offset/2))
    J_offset_left=int(np.floor(J_offset/2))
    
    #右边的偏移距        
    I_offset_right=abs(abs(abs(I_offset)-abs(I_offset_left)))        
    J_offset_right=abs(abs(abs(J_offset)-abs(J_offset_left)))
    
    #判断是否为0 
    #乘上算子
    if I_offset_left!=0:
        
        I_offset_right*=(-I_offset_left/abs(I_offset_left))
    
    if J_offset_left!=0:
        
        J_offset_right*=(-J_offset_left/abs(J_offset_left))
    
#    print(I_offset_left,J_offset_left)
#    print(I_offset_right,J_offset_right)
    
#    print(Chip_left.center)
#    print(Chip_right.center)

    #移动Chip_left,Chip_right
    Chip_left.Move(I_offset_left,J_offset_left)
    Chip_right.Move(I_offset_right,J_offset_right)

#    print(Chip_left.center)
#    print(Chip_right.center)
    
    return [Chip_left,Chip_right]

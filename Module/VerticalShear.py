# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 15:29:39 2019

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：简单剪切去褶皱函数库-VerticalShear
@原理：用垂直剪切或斜剪切方法消除地层形变，将地层恢复到水平或假定的区域基准面。
"""

'''垂直剪切'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from Module import Image as Im

#动态修改字体，需要在可视化参数中添加fontproperties=font
font=FontProperties(fname=r"C:\Windows\Fonts\Simsun.ttc",size=12)

#11.7
#============================================================================== 
#第0期次的恢复
def Originate(img_tag,rgb_dict,show=False):
        
    #纯地层的tag
    layer_tag_list=[this_tag for this_tag in list(rgb_dict.keys()) if this_tag>0]
    
#    print(layer_tag_list)
    
    #空白处面积
    area_blank=len(np.where(img_tag==0)[1])
    
    #新矩阵的行列
    new_column=int(np.ceil(np.shape(img_tag)[1]))
    new_row=int(np.ceil(np.shape(img_tag)[0]-area_blank/new_column))
    
    #新的tag矩阵
    new_img_tag=np.full((new_row,new_column),-2)
    
    #tag厚度和深度的映射关系
    map_layer_tag_thickness,\
    map_layer_tag_bottom_depth,\
    map_layer_tag_top_depth\
    =TagThicknessAndDepth(img_tag,layer_tag_list)
       
    #重新上色
    for j in range(np.shape(new_img_tag)[1]):
    
        for k in range(len(layer_tag_list)):
    
            #地层的tag
            this_tag=layer_tag_list[k]
            
            #上下界面的深度
            this_bottom_depth=list(map_layer_tag_bottom_depth.values())[k][j]
            this_top_depth=list(map_layer_tag_top_depth.values())[k][j]
            
            #厚度
            this_thickness=list(map_layer_tag_thickness.values())[k][j]
            
            new_img_tag[this_top_depth:this_bottom_depth,j]=int(this_thickness)*[this_tag]
    
    #显示与否
    if show:
            
        plt.figure()
        plt.imshow(Im.Tag2RGB(new_img_tag,rgb_dict))

    return new_img_tag

#============================================================================== 
#求出img_tag中不同tag的平均深度
def TagMeanDepth(img_tag,tag_list):
    
    #比较他们的深度度
    depth_list=[]
    
    for this_tag in tag_list:
          
#        print(np.mean(list(np.where(img_rgb==list(this_rgb))[0])))

        depth_list.append(np.mean(list(np.where(img_tag==this_tag)[0])))
        
#    建立颜色何深度的索引
    map_tag_depth=dict(zip(tag_list,depth_list))
    
    return map_tag_depth

#============================================================================== 
#不同tag的厚度和深度
def TagThicknessAndDepth(img_tag,layer_tag_list):
    
    #thickness
    #每层各列的厚度的列表之列表
    layer_thickness_list=[]
    
    for this_tag in layer_tag_list:
        
        layer_thickness=[]
        
        for j in range(np.shape(img_tag)[1]):
            
            layer_thickness.append(len(np.where(img_tag[:,j]==this_tag)[0]))
        
        layer_thickness_list.append(layer_thickness)
        
    #建立tag和地层各列厚度的映射关系
    map_layer_tag_thickness=dict(zip(layer_tag_list,layer_thickness_list))
    
#    print(map_layer_tag_thickness)
    
    #bottom_depth
    #每层各列的底部深度的列表之列表
    layer_bottom_depth_list=[]
    
    count=0
    #计算底部深度
    for this_tag in list(map_layer_tag_thickness.keys()):

        #第一层厚度即底部深度
        if count==0:
            
            layer_bottom_depth=map_layer_tag_thickness[this_tag]
            
            layer_bottom_depth_list.append(layer_bottom_depth)
            
        #从第二层开始
        if count>0:

            #底部深度来了
            layer_bottom_depth=list(np.array(layer_bottom_depth_list[count-1])+np.array(map_layer_tag_thickness[this_tag]))
        
            layer_bottom_depth_list.append(layer_bottom_depth)
        
        count+=1
    
    #建立tag和地层各列底部深度的映射关系
    map_layer_tag_bottom_depth=dict(zip(layer_tag_list,layer_bottom_depth_list))
    
    #top_depth
    #每层各列的顶部深度的列表之列表
    layer_top_depth_list=[]
    
    #计算顶部深度
    for k in range(len(layer_tag_list)):
        
        #顶部部深度来了
        layer_top_depth=list(np.array(layer_bottom_depth_list[k])-np.array(layer_thickness_list[k]))
        
        layer_top_depth_list.append(layer_top_depth)
    
    #建立tag和地层各列顶部深度的映射关系
    map_layer_tag_top_depth=dict(zip(layer_tag_list,layer_top_depth_list))
    
    return map_layer_tag_thickness,map_layer_tag_bottom_depth,map_layer_tag_top_depth

#============================================================================== 
#tag插值改变矩阵尺寸
def ReshapeTagNearby(img_tag,shape):
    
    new_img_tag=np.full(shape,-2)
    
    for i in range(np.shape(new_img_tag)[0]):
        
        for j in range(np.shape(new_img_tag)[1]):
            
            #新的坐标索引
            new_i=int(np.floor(i*np.shape(img_tag)[0]/np.shape(new_img_tag)[0]))
            new_j=int(np.floor(j*np.shape(img_tag)[1]/np.shape(new_img_tag)[1]))
            
            new_img_tag[i,j]=img_tag[new_i,new_j]
            
    return new_img_tag

#11.10
#============================================================================== 
#开始恢复
#original_img_tag为恢复之前的tag矩阵
def Recover(original_img_tag,rgb_dict,side='right',show=False):
    
    #输出的所有img_tag矩阵组成的列表
    final_img_tag_list=[original_img_tag]
    
    #总位移量列表
    transform_length_list=[0]
    
    #纯地层的tag
    layer_tag_list=[this_tag for this_tag in list(rgb_dict.keys()) if this_tag>0]
    
#    print(layer_tag_list)
    
    import copy
    img_tag=copy.deepcopy(original_img_tag)
    
    #建立tag和对应消去面积字典里
    map_tag_area_to_diminish={}
        
    #进入每一期剥蚀的循环  
    for k in range(len(layer_tag_list)):
        
        #要消除的layer的tag
        tag_to_diminish=layer_tag_list[k]
        
    #    print(tag_to_diminish)
        
        #要消除的tag面积
        area_to_diminish=len(np.where(img_tag==tag_to_diminish)[1])
        
#        print(area_to_diminish)
    
        #将消去面积和tag添加到另一个字典里     
        map_tag_area_to_diminish[tag_to_diminish]=area_to_diminish

        #消除tag后的宽度和高度
        new_height=int(np.ceil(np.shape(img_tag)[0]))
        new_width=int(np.ceil(np.shape(img_tag)[1]-area_to_diminish/new_height))
    
        """对他们进行横向压缩"""
        
        #缩放因子,axis=0,axis=1
        factor_1=new_width/np.shape(img_tag)[1]
        factor_0=1/factor_1
    
    #    print(factor_0,factor_1)
        
        #新矩阵的尺寸：但最终会被截断，所以是临时的
        new_shape_temp=(int(np.ceil(np.shape(img_tag)[0]*factor_0)),
                        int(np.ceil(np.shape(img_tag)[1]*factor_1)))
        
        #新的矩阵
        new_img_tag_temp=ReshapeTagNearby(img_tag,new_shape_temp)
        
    #    plt.figure()
    #    plt.imshow(whj.Tag2RGB(new_img_tag_temp,rgb_dict))
        
        #正式的用于输出的tag矩阵
        new_img_tag=np.full((new_height,new_width),-2)
        
        #tag厚度和深度的映射关系
        map_layer_tag_thickness=TagThicknessAndDepth(new_img_tag_temp,layer_tag_list)[0]
        
        map_layer_tag_bottom_depth={}
        map_layer_tag_top_depth={}
     
        #然后，对这些个字典进行修改
        
        #把tag_to_diminish那层剥掉
        del map_layer_tag_thickness[tag_to_diminish]
            
        count=0
        
    #    print(list(map_layer_tag_thickness.keys()))
        
        for this_tag in list(map_layer_tag_thickness.keys()):
    
    #        print(this_tag)
            
            #底部深度
            #第一层厚度即底部深度
            if count==0:
         
                #底部深度
                layer_bottom_depth=map_layer_tag_thickness[this_tag]
            
                #顶部深度    
                layer_top_depth=[0]*len(layer_bottom_depth)
                
                #收录进来
                map_layer_tag_bottom_depth[this_tag]=layer_bottom_depth
                map_layer_tag_top_depth[this_tag]=layer_top_depth
                
            #从第二层开始
            if count>0:
                
                #顶部深度    
                layer_top_depth=list(map_layer_tag_bottom_depth.values())[count-1]
    
                #底部深度
                layer_bottom_depth=list(np.array(layer_top_depth)+np.array(map_layer_tag_thickness[this_tag]))
           
                #收录进来
                map_layer_tag_bottom_depth[this_tag]=layer_bottom_depth
                map_layer_tag_top_depth[this_tag]=layer_top_depth
     
            count+=1
            
        #重新上色
        for j in range(np.shape(new_img_tag)[1]):
        
            for k in range(len(map_layer_tag_thickness.keys())):
        
                #地层的tag
                this_tag=layer_tag_list[k]
                    
                #上下界面的深度
                this_bottom_depth=list(map_layer_tag_bottom_depth.values())[k][j]
                this_top_depth=list(map_layer_tag_top_depth.values())[k][j]
                
                #厚度
                this_thickness=list(map_layer_tag_thickness.values())[k][j]
                
                new_img_tag[this_top_depth:this_bottom_depth,j]=int(this_thickness)*[list(map_layer_tag_thickness.keys())[k]]
       
#        #截断之前
#        plt.figure()
#        plt.imshow(whj.Tag2RGB(new_img_tag,rgb_dict)) 
        
        #输出矩阵
        final_img_tag=np.zeros(np.shape(original_img_tag))
             
#        print(list(map_tag_area_to_diminish.keys()))
        
        """对final_img_tag进行操作，补上消去地层"""
        
        #进入该循环
        for k in range(len(map_tag_area_to_diminish.keys())):
            
#            print(list(map_tag_area_to_diminish.keys())[k])
                    
            #计算面积的界限
            area_upper_bound=sum(list(map_tag_area_to_diminish.values())[:k+1])
            
            area_lower_bound=sum(list(map_tag_area_to_diminish.values())[:k])
            
#            print(area_upper_bound,area_lower_bound)
            
            #这一期次填补界面列坐标
            j_lower_bound=int(np.ceil(area_lower_bound/np.shape(final_img_tag)[0]))
            
            j_upper_bound=int(np.ceil(area_upper_bound/np.shape(final_img_tag)[0]))
            
#            print(lower_bound,upper_bound)
            
            #填充各期次的剥蚀
            #左右两种观赏模式
            if side is 'right':
                
                l=np.shape(final_img_tag)[1]
                
#                print(l-upper_bound,l-lower_bound)
                
                final_img_tag[:,l-j_upper_bound:l-j_lower_bound]=list(map_tag_area_to_diminish.keys())[k]
            
            if side is 'left':
                
#                print(lower_bound,upper_bound)
                
                final_img_tag[:,j_lower_bound:j_upper_bound]=list(map_tag_area_to_diminish.keys())[k]
      
        #复制粘贴核心部分
        final_img_tag[:np.shape(new_img_tag)[0],:np.shape(new_img_tag)[1]]=new_img_tag[:,:]
        
        #把位移量收录进来
        transform_length_list.append(np.shape(final_img_tag)[1]-np.shape(new_img_tag)[1])
        
        #把img_tag收录进来
        final_img_tag_list.append(final_img_tag)

#        #截断之后
#        plt.figure()
#        plt.imshow(Tag2RGB(final_img_tag,rgb_dict)) 
        
        #更新输入矩阵
        img_tag=copy.deepcopy(new_img_tag)
        
    #显示模块
    if show:
            
        for this_final_img_tag in final_img_tag_list:
            
            plt.figure()
            plt.imshow(Im.Tag2RGB(this_final_img_tag,rgb_dict)) 
    
    return final_img_tag_list,transform_length_list


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
        
#11.10        
#============================================================================== 
#打印计算结果
def PrintResult(profile_length,final_img_tag_list,transform_length_list,save_path):  
   
    #判断并创建文件夹
    GenerateFold(save_path)
    
    #1km代表unit个像素点（需根据实际比例尺修改）
    unit=np.shape(final_img_tag_list[0])[1]/profile_length
    
    #输出重要参数
    print('初始长度：%5.2fkm'
          %(np.shape(final_img_tag_list[0])[1]/unit))
    
    for i in range(len(transform_length_list)):
        
        #当下的像素点长度
        that_length=np.shape(final_img_tag_list[0])[1]-transform_length_list[i]
 
        print('第%d期长度：%5.2fkm，拉张量：%5.2fkm，拉张率：%4.2f%%'
              %(i,that_length/unit,
                transform_length_list[i]/unit,
                transform_length_list[i]/(np.shape(final_img_tag_list[0])[1]/100)))
        
    #将计算结果写入result.txt文件
    with open(save_path+'\\'+"result.txt","w") as file:
      
        file.write('初始长度：%5.2fkm'
                   %(np.shape(final_img_tag_list[0])[1]/unit))
        file.write('\n')
        
        for i in range(len(transform_length_list)):
            
            #当下的像素点长度
            that_length=np.shape(final_img_tag_list[0])[1]-transform_length_list[i]
            
            file.write('第%d期长度：%5.2fkm，拉张量：%5.2fkm，拉张率：%4.2f%%'
                       %(i,that_length/unit,
                         transform_length_list[i]/unit,
                         transform_length_list[i]/(np.shape(final_img_tag_list[0])[1]/100)))
            file.write('\n')
            
#11.11           
#============================================================================== 
#处理结果的单独表示
#final_img_tag_list为恢复后各期次的tag矩阵
def PrintSingle(img_rgb,final_img_tag_list,rgb_dict,save_path,show=False): 
    
    #判断并创建文件夹
    GenerateFold(save_path)
    
    #子目录路径
    save_path+='\\single'
    
    #生成子文件夹
    GenerateFold(save_path)
    
    #修改路径
    import os 
    
    FigName=os.path.join(save_path,'原图.png')
    
    import imageio
    
    #保存原图
    imageio.imwrite(FigName,img_rgb)
    
#    ax=plt.gca()
#    ax.imshow(img_rgb)
#    
#    #去掉坐标刻度
#    ax.set_xticks([])
#    ax.set_yticks([])
#    
#    #去掉上下左右边框
#    ax.spines['top'].set_visible(False) 
#    ax.spines['bottom'].set_visible(False) 
#    ax.spines['left'].set_visible(False) 
#    ax.spines['right'].set_visible(False)
#    
#    
#    fig.savefig(FigName,dpi=300,bbox_inches='tight')
#    
#    #关闭图片  
#    plt.close() 
    
    #保存列表中的img_tag
    number=0 
    
    for this_final_img_tag in final_img_tag_list:
        
        #修改路径
        FigName='第'+str(number)+'期.png'
        FigName=os.path.join(save_path,FigName)
        
        #先转为rgb矩阵
        this_final_img_rgb=Im.Tag2RGB(this_final_img_tag,rgb_dict)
        
        #逐个保存
        imageio.imwrite(FigName,this_final_img_rgb)
        
#        fig=plt.figure()
          
#        ax=plt.gca()       
#        ax.imshow(this_final_img_rgb)
#        
#        #去掉坐标刻度
#        ax.set_xticks([])
#        ax.set_yticks([])
#        
#        #去掉上下左右边框
#        ax.spines['top'].set_visible(False) 
#        ax.spines['bottom'].set_visible(False) 
#        ax.spines['left'].set_visible(False) 
#        ax.spines['right'].set_visible(False)
#        
#        fig.savefig(FigName,dpi=300,bbox_inches='tight')      
#        #关闭图片
#        if not show:
#            
#            plt.close()  
        
        number+=1   
        
#11.12
#============================================================================== 
#处理结果生成组合图
#accurate表示两种显示模式的开关(True/False)
def PrintSubplot(img_rgb,final_img_tag_list,rgb_dict,save_path,show=False):
   
    #判断并创建文件夹
    GenerateFold(save_path)
    
    #子目录路径
    save_path+='\\subplot'
    
    #生成子文件夹
    GenerateFold(save_path)
    
    import os 
    
    #最终要打印的rgb矩阵组成的列表
    final_img_rgb_list=[img_rgb]+[Im.Tag2RGB(this_final_img_tag,rgb_dict) for this_final_img_tag in final_img_tag_list]
    
    """不准确地输出（好看）"""
    
    #可视化，仅仅是表示
    fig=plt.figure() 
    
    #子图序号
    number=1
    
    #一共这么多小图
    amount_of_subplot=len(final_img_rgb_list)

    #打印每一期次
    for this_img_rgb in final_img_rgb_list:
                   
        ax=plt.subplot(amount_of_subplot,1,number)    
        ax.imshow(this_img_rgb)
        
        #去掉坐标刻度
        ax.set_xticks([])
        ax.set_yticks([])
                      
        #去掉上下左右边框
        ax.spines['top'].set_visible(False) 
        ax.spines['bottom'].set_visible(False) 
        ax.spines['left'].set_visible(False) 
        ax.spines['right'].set_visible(False) 
        
        ax.axis('tight')
        
        number+=1

    #修改图名
    FigName='inaccurate组合图.png'
    
    #修改路径   
    FigName=os.path.join(save_path,FigName)   
    fig.savefig(FigName,dpi=300,bbox_inches='tight')

    #关闭图片
    if not show:
        
        plt.close()   
       
    """实打实地输出"""
#    #把原图去掉
#    final_img_rgb_list.remove(final_img_rgb_list[0])
    
    '''设定一个坐标轴范围'''
    x_boundary=[0,np.shape(img_rgb)[1]]
    y_boundary=[0,np.shape(img_rgb)[0]]

    #一共这么多张图
    amount_of_fig=int(np.ceil(len(final_img_rgb_list)/5))
    
    #一共这么多小图
    amount_of_subplot=len(final_img_rgb_list)
    
    #背景色
    background_rgb=np.array([255,255,255],dtype=np.uint8)
    
    #第k张图
    for k in range(amount_of_fig):
        
        #可视化，仅仅是表示
        fig=plt.figure() 
        
        #子图序号
        number=1
        
        this_fig_final_img_rgb_list=final_img_rgb_list[5*k:min(5*(k+1),amount_of_subplot)]
        
        #打印每一期次
        for this_img_rgb in this_fig_final_img_rgb_list:
               
            #翻转一波
            this_img_rgb_to_show=np.full(np.shape(this_img_rgb),background_rgb)
            
            for kk in range(np.shape(this_img_rgb_to_show)[0]):
                
                this_img_rgb_to_show[-kk-1]=this_img_rgb[kk]
                
            ax=plt.subplot(5,1,number)  
            ax.imshow(this_img_rgb_to_show)
            ax.axis([x_boundary[0],x_boundary[1],y_boundary[0],y_boundary[1]])
            
            #去掉坐标刻度
            ax.set_xticks([])
            ax.set_yticks([])
                          
            #去掉上下左右边框
            ax.spines['top'].set_visible(False) 
            ax.spines['bottom'].set_visible(False) 
            ax.spines['left'].set_visible(False) 
            ax.spines['right'].set_visible(False) 
            
            number+=1
    
        #修改图名
        FigName='accurate组合图'+str(k+1)+'.png'
        
        #修改路径   
        FigName=os.path.join(save_path,FigName)   
        fig.savefig(FigName,dpi=300,bbox_inches='tight')
    
        #关闭图片
        if not show:
            
            plt.close()  
            
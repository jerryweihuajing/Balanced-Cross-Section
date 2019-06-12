# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 15:06:28 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于面积守恒s的平衡恢复函数库
@目标：
1 自动读取颜色rgb和灰度（由浅到深） OK
2 读取输入图片的方式改为由路径读取  OK
3 深度由min()函数来确定 OK
4 unit即比例尺由输入导入 OK
5 导出函数 
  1)导出bmp图片的函数 OK
  2)导出缩短量和缩短率计算结果（文本格式）
6 测试随机模型 OK
7* 所有输入界面化,所有输出美观化
8* 尝试加入断层的解释（深度学习与神经网络方法）
9* 三种平衡恢复方法：
   1)基于面积 OK 
   2)基于断层拉伸 
   3)基于层长
   不同的处理方法适用于不同的模型
习惯：函数用大写字母，变量名用下划线
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

#============================================================================== 
#rgb转灰度的函数
def rgb2gray(rgb):
   
    gray=np.zeros(np.shape(rgb)[0:-1])
   
    for i in range(np.shape(rgb)[0]):
       
        for j in range(np.shape(rgb)[1]):
            
            gray[i,j]=np.dot(rgb[i,j],[0.299,0.587,0.113])
    
    return gray.astype(int)

#============================================================================== 
#输入路径path，读取图片，生成图片的rgb和灰度矩阵函数
#参数show表示图片预览参数：默认为None，rgb表示开启rgb预览，gray表示灰度预览
def LoadImage(load_path,show=None):
    
    img=Image.open(load_path)
    img_rgb=np.array(img)
    
    if show is 'rgb': 
       
        #plt以数组的形式表示图片，PIL.Image表示Image类型的图片
        #显示rgb图像
       
        plt.figure()
        plt.imshow(img_rgb) 
        Image.fromarray(img_rgb).show()
        
    return img_rgb

#============================================================================== 
"""不需要coreldraw修图的应急措施"""
#给图像矩阵增加上顶面（一般为白色）或下底面（基底色）
#操作对象为img_rgb
#上顶面增加add_top行
#改变返回值类型很重要！
def AddTop(img_rgb,add_top):
    
    #白色的RGB
    rgb_white=np.array([255,255,255])
    
    new_rgb=np.full((np.shape(img_rgb)[0]+add_top,np.shape(img_rgb)[1],3),rgb_white)
    new_rgb[-np.shape(img_rgb)[0]:,-np.shape(img_rgb)[1]:,:]=img_rgb[:,:,:]
    
    return new_rgb.astype(img_rgb.dtype)

#下底面增加add_bottom行
def AddBottom(img_rgb,add_bottom):
    
    rgb_base=img_rgb[-1,-1]
   
    new_rgb=np.full((np.shape(img_rgb)[0]+add_bottom,np.shape(img_rgb)[1],3),rgb_base)
    new_rgb[:np.shape(img_rgb)[0],:np.shape(img_rgb)[1],:]=img_rgb[:,:,:]
   
    return new_rgb.astype(img_rgb.dtype)

#============================================================================== 
#将rgb值矩阵转化为灰度值矩阵
def GenerateImgGray(img_rgb,show=None):
   
    img_gray=rgb2gray(img_rgb) 
   
    if show is 'gray': 
       
        #显示灰度图像
        plt.figure()
        plt.imshow(img_gray,cmap='gray')
        Image.fromarray(img_gray).show()    
        
    return img_gray

#============================================================================== 
#创建rgb和灰度列表和灰度和rgb的映射字典的函数
def GenerateListAndDict(img_rgb,well):
    
    #rgb数组
    rgb_list=[] 
    
    #灰度数组
    tag_list=[] 
    
    #以第j列为例拾取颜色，获取地层的gray和rgb值
    '''well很关键！'''
    j=well
    
    #计数器，后来发展为标签
    count=0
    
    for i in range(np.shape(img_rgb)[0]):
        
        if list(img_rgb[i,j]) not in rgb_list:
            
            rgb_list.append(list(img_rgb[i,j]))
            count+=1
            tag_list.append(count)

    #建立tag和rgb的映射字典
    color_dict={} 
    
    for i in range(len(rgb_list)):
       
        color_dict[tag_list[i]]=rgb_list[i]
    
    return rgb_list,tag_list,color_dict

#============================================================================== 
#生成图片的索引Tag矩阵
def GenerateImgTag(img_rgb,color_dict):
   
    #计算img_tag,初始化为0
    img_tag=np.full(np.shape(img_rgb)[0:-1],0)
    
    for i in range(np.shape(img_rgb)[0]):
       
        for j in range(np.shape(img_rgb)[1]):
            
            for k in range(1,len(color_dict)+1):
                
                if color_dict[k]==list(img_rgb[i,j]):
                    
                    img_tag[i,j]=k
                    
    return img_tag

#============================================================================== 
#计算各层的像素点数量，索引为层序号，layer[0]表示空白区域
def InitLayer(tag_list,img_tag):
    
    layer=[]
    
    for k in range(len(tag_list)):
       
        layer.append([])
        
        for j in range(np.shape(img_tag)[1]):
            
            layer[k].append(np.sum(img_tag[:,j]==tag_list[k]))
    
    return layer

#============================================================================== 
"""深度的确定方式：层最高点"""
#创建各层最大高度值的列表
def InitHeight(layer,height,width):
   
    Height=[height]
   
    #记录下各层催高点的位置
    temp=np.zeros((height,width))
    
    for j in range(width):
        
        sum_height=0 #临时变量
        
        for i in range(len(layer)):
            
            sum_height+=layer[i][j]
            temp[i,j]=height-sum_height
            
    for i in range(len(layer)-1):
        
        Height.append(int(temp[i].max()))
        
    return Height

#============================================================================== 
#计算各种缩短
def Calculate(layer,Height,width): 
    
    #计算缩短量，单位为像素点
    #缩短量
    shorten=[0] 
   
    for i in range(1,len(layer)-1):
        
        length=0
       
        for item in layer[i]:
            
            length+=item
            
        shorten.append(length/Height[i])
        
    #每一期缩短之后的长度
    shorten_length=[width] 
    
    for i in range(1,len(layer)-1):
        
        shorten_length.append(shorten_length[i-1]-shorten[i])
        
    #每一期缩短率
    shorten_rate=[0] 
    
    for i in range(1,len(layer)-1):
        
        #最后一期的长度作分母
        shorten_rate.append(shorten[i]/shorten_length[-1]) 
        
    #总缩短量
    shorten_sum=0 
    
    #总缩短率
    shorten_rate_sum=0 
    
    for i in range(1,len(layer)-1):
       
        shorten_sum+=shorten[i]
        shorten_rate_sum+=shorten_rate[i]   
        
    #各阶段缩短率之和,初始阶段显然为0
    rate=[0] 
    
    for k in range(1,len(layer)-1):
        
        rate.append(rate[-1]+shorten_rate[k]) 
   
    #各阶段的缩短量之和为(1+rate[k])*width
    #各阶段的缩短之后的长度与原长的比值为(1-shorten[k]/shorten_length[0])
    
    return shorten,shorten_length,shorten_sum,shorten_rate_sum,shorten_rate,rate

#============================================================================== 
"""
A,B,C,D处的指数 expo
B无论组合还是bmp都为1，控制地层厚度
A和C本质是一样的，前者控制灰度图和rgb图的高度
D控制组合图的宽度
A=C=D=1:组合图
A=C=D=0:bmp
"""
#第n期的缩短n=0表示初期拉平状态,第n张图
def GeneratePushResult(layer,Height,width,shorten_length,tag_list,expo,tag_base,color_dict,img_rgb):
    
    #灰度值结果和rgb结果
    push_tag,push_rgb=[],[]
    
    #为了使单个图好看将图片横向压缩生成rgb_push_for_single
    rgb_push_for_single=[]
    
    #灰度版本
    for n in range(1,len(layer)):
       
        #某底层拉平的下界面
        depth=np.zeros((len(layer)-1,width))
       
        #将结果转化为整型
        depth=depth.astype(int) 
        
        #最大化像素点行数（成图需要）
        """
        缩放比例：第n期次的长度和第一期的长度之比
        ratio=shorten_length[k]/shorten_length[0]
        A处
        """
       
        #缩放比例
        ratio=shorten_length[n-1]/shorten_length[0]
        draw=np.full((int(np.floor(Height[n-1]/ratio**expo)),width),tag_base) 
        
        for j in range(width):
           
            for k in range(n,len(layer)-1):
                
                """
                缩放比例：第n期次的长度和第一期的长度之比
                ratio=shorten_length[k]/shorten_length[0]
                B处
                """
                
                depth[k][j]=depth[k-1][j]+np.floor(layer[k][j]/ratio**(expo+1))
                
                for i in range(depth[k-1][j],depth[k][j]):
                    draw[i,j]=tag_list[k]
                    
        push_tag.append(draw)
    
    #rgb版本
    #初始和一二三期
    for k in range(len(layer)-1):
       
        #rgb数组是三维的,先填充基底
        #考虑了将矩阵行数扩大，为了subplot图好看
        
        """
        缩放比例：第n期次的长度和第一期的长度之比
        ratio=shorten_length[k]/shorten_length[0]
        C处和A处是一个道理
        """
        
        #缩放比例
        ratio=shorten_length[k]/shorten_length[0]
        
        #纵向
        #图形高度压缩之后的图像矩阵
        
        draw=np.full((int(np.floor(Height[k]/ratio**expo)),width,3),
                     np.array(color_dict[tag_base])) 
        
        for i in range(Height[k]):
           
            for j in range(width):
               
                draw[i,j]=np.array(color_dict[push_tag[k][i,j]])
                
        #将映射后的矩阵转化为和原图相同的格式        
        push_rgb.append(draw.astype(img_rgb.dtype)) 
        
        """不能插值！因为颜色是唯一的，不可平滑，只能四舍五入像素点！"""
        #横向
        #宽度压缩之后的图像矩阵
        new_push_rgb=np.full((len(push_rgb[k]),int(np.floor(shorten_length[k])),3),
                             np.array(color_dict[tag_base]))
        
        for i in range(np.shape(new_push_rgb)[0]):
           
            for j in range(np.shape(new_push_rgb)[1]):
                
                new_push_rgb[i,j]=push_rgb[k][i,int(np.round(j/ratio))]
        
        #每一期的结果都存入rgb_push_for_single列表当中
       
        rgb_push_for_single.append(new_push_rgb)
        
    return push_rgb,rgb_push_for_single

#============================================================================== 
#生成组合图
#title表示是否输出图名(ON/OFF),默认为OFF
def ShowSubplot(img_rgb,font,push_rgb,shorten_length,shorten_rate,d,expo,save_path,middle,title='OFF'):
    
    #expo=1时才执行
    if expo==1:      
        
        #可视化，仅仅是表示
        fig_rgb_1=plt.figure(1) 
        
        #用matplotlib.pyplot作Figure图
        #add_axes([left,bottom,width,height])
        
        #原图
        ax=fig_rgb_1.add_axes([0.1,0.5,0.5,0.5])
        ax.imshow(img_rgb)
        
        #去掉坐标刻度
        ax.set_xticks([])
        ax.set_yticks([])
        
        #判断是否输出图名
        if title=='ON':
            plt.title('基于面积深度法的平衡恢复剖面',fontproperties=font)    
            
        #拉平初始状态+第n期次
        #生成第一个图
        fig_rgb=fig_rgb_1
        
        """
        D处
        缩放比例：第n期次的长度和第一期的长度之比
        ratio=shorten_length[k]/shorten_length[0]
        """
        top=0.3
        height=0.18
        
#        top=0
#        height=0.15
        
        #生成第一个图
        for k in range(min(4,len(push_rgb))):
            
            #缩放比例：
            ratio=shorten_length[k]/shorten_length[0]
            ax=fig_rgb.add_axes([0.1,top-k*height/(1-shorten_rate[k])**(expo-1),0.5*ratio**expo,0.5])
            
            ax.imshow(push_rgb[k])
            ax.set_xticks([])
            ax.set_yticks([])
            
        #给图片命名并保存
        FigName1=os.path.join(save_path,'组合图.png')
        fig_rgb.savefig(FigName1,dpi=d,bbox_inches='tight')
        plt.close() #关闭图片
        
        #生成第二个图
        fig_rgb_2=plt.figure(2)
        fig_rgb=fig_rgb_2
        
        #循环画第二幅图
        for k in range(4,len(push_rgb)):
            
            ax=fig_rgb.add_axes([0.1,top-(k-4)*height/(1-shorten_rate[k])**(expo-1),
                                 0.5*(shorten_length[k]/shorten_length[0])**expo,0.5])
            ax.imshow(push_rgb[k])
            ax.set_xticks([])
            ax.set_yticks([])
            
        #给图片命名并保存
        FigName2=os.path.join(save_path,'组合图2.png')
        fig_rgb.savefig(FigName2,dpi=d,bbox_inches='tight')
        plt.close() #关闭图片
        
#============================================================================== 
#打印计算结果
def PrintResult(profile_length,shorten,shorten_length,shorten_sum,shorten_rate_sum,save_path):  
   
    #1km代表unit个像素点（需根据实际比例尺修改）
    unit=shorten_length[0]/profile_length
    
    #输出重要参数
    print('初始长度：%5.2fkm'
          %(shorten_length[0]/unit))
    
    for i in range(len(shorten)):
        
        print('第%d期长度：%5.2fkm，拉张量：%5.2fkm'
              %(i,shorten_length[i]/unit,shorten[i]/unit))
   
    print('总拉张量：%5.2fkm，拉张率：%4.2f%%'
          %(shorten_sum/unit,shorten_rate_sum*100))
    
    #将计算结果写入result.txt文件
    with open(save_path+'\\'+"result.txt","w") as file:
      
        file.write('初始长度：%5.2fkm'
                   %(shorten_length[0]/unit))
        file.write('\n')
        
        for i in range(len(shorten)):
            
            file.write('第%d期长度：%5.2fkm，拉张量：%5.2fkm'
                       %(i,shorten_length[i]/unit,shorten[i]/unit))
            file.write('\n')
       
        file.write('总拉张量：%5.2fkm，拉张率：%4.2f%%'
                   %(shorten_sum/unit,shorten_rate_sum*100))

#============================================================================== 
#处理结果的单独表示
#img_rgb为原图矩阵
#rgb_push_for_single为处理结果矩阵组成的列表
#dpi为分辨率
def ShowSingle(img_rgb,rgb_push_for_single,d,expo,save_path): 
     
    #期次序号，0表示原图
    #exp=0时执行保存图片
    if expo==0:
        
        number=0 
        FigName ='原图.png'      
        FigName =os.path.join(save_path,FigName)
        
        from scipy.misc import imsave
        
        imsave(FigName,img_rgb)
        
#        #用matplotlib.pyplot绘制图片
#        fig=plt.figure(number)
#        plt.imshow(img_rgb)
#        #关闭刻度
#        plt.xticks([])
#        plt.yticks([])
#        #关闭坐标轴
#        plt.axis('off') 
#        #给图片命名并保存        
#        fig.savefig(FigName,dpi=d,bbox_inches='tight',pad_inches=0)
#        plt.close() #关闭图片

        for item in rgb_push_for_single:
           
            FigName ='第'+str(number)+'期.png'
            FigName =os.path.join(save_path,FigName)
            
            #控制图片大小，根据图像矩阵大小直接输出
            imsave(FigName,item)
            number+=1
                     
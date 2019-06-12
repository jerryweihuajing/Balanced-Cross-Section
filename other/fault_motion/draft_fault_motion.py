# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 22:42:32 2018

@author:Wei Huajing
@company:Nanjing University
@e-mail:jerryweihuajing@126.com

@title：基于断层牵引法的平衡恢复草稿
"""

#%%
#输入完全由于点击来决定
#
#plate_up.Init([total_fractions[0]])
#plate_down.Init([total_fractions[1]])

"""考核后研究一下fault的变形"""

#plate_total=o.plate()
#plate_total.Init(total_fractions)
#
#CHIP=plate_total.ToChip(this_fault,img_tag,5,'C')
#
#whj.ShowChips([CHIP],img_rgb,rgb_dict,grid='on')
#
#CHIP.UpdateTop()
#CHIP.Regularize()
#
#whj.ShowChips([CHIP],img_rgb,rgb_dict,grid='on')

##正则化
#CHIP_1.Regularize()
#CHIP_2.Regularize()
#
#whj.ShowChips([CHIP_1,CHIP_2],img_rgb,rgb_dict)

#%%
#img_rgb=np.array(img_rgb,dtype=np.uint8)
#
#plt.figure()
#plt.imshow(img_rgb)

#删除fault
#Layer=whj.DeleteFault(total_fractions)    

##初始化角点
#for this_layer in Layer:
#    this_layer.InitAngle(Fault,img_tag,img_rgb,rgb_dict)

##显示轮廓
#whj.ShowEdge(Layer[0],img_rgb)

#根据面积不变原理
#计算符合tag的元素数量
##生成角点列表
#layer_tag=[2,3]  
##获得所有的fault
#Fault=[this_fraction for this_fraction in total_fractions if this_fraction.tag==-1]

"""补充点和拉平点对应的时不同的运动方式，拉张和挤压"""  

#whj.ChipRegularization(CHIP_1)
#whj.ChipRegularization(CHIP_2)
#whj.ShowChips([CHIP_1,CHIP_2],img_rgb,rgb_dict)

#plates=whj.TrueMove(plate_up,plate_down,Fault[0],2,
#                       img_tag,img_rgb,rgb_dict,True)

#填充这四个角围城的区域
#whj.FillGap(plate_up,plate_down,img_rgb,rgb_dict,True)

##四个顶点
#ABCD=[[0,0],[6,6],[1,3],[3,1]]    
#
##对象法
#Qua=o.quadrangle(ABCD)  
#print(Qua.IncludePoint([1,1]))
#
##全局函数法
#print(whj.PointInQuadrangle([1,1],ABCD))
    
#X,Y=[1,2,3],[1,4,9]
#
##limit表示定义域的取值范围
#limit=[0,6]
#
#A=GetInterpolation(CombineXY(X,Y),limit)
#B=GenerateLineList(0,0,1,limit)
#
#print(CrossDataAB(A,B))
   
#目标点
#target_point=(np.array(plate_up.top.top_right)+np.array(plate_down.top.top_left))/2     

#Chips=[CHIP_1,CHIP_2]

##检验搜索函数
#a=SearchByID(Chips,'2-450|3')
#print(a.id)
#print(a.tag)
#
#b=SearchByID(Chips,'2-450')
#print(b.id)
#print(b.total_tag)

#显示
#CHIP_1.Show(img_rgb,rgb_dict)
#CHIP_2.Show(img_rgb,rgb_dict,'on')

##移动
#CHIP_1.MoveTo(target_point,'left')
#CHIP_2.MoveTo(target_point,'right')
#CHIP_1.Show(img_rgb,rgb_dict,'on')
#CHIP_2.Show(img_rgb,rgb_dict,'on')

##得到只有top的像素矩阵
#img_rgb_top=CHIP_1.top.Show(img_rgb,rgb_dict,output=True)
#img_rgb_top=CHIP_2.top.Show(img_rgb,rgb_dict,output=True)

#显示fraction集合
#img_rgb_top=whj.Showfractions([CHIP_1.top,CHIP_2.top],img_rgb,rgb_dict,output=True)

#开运算
#whj.Open(img_rgb_top,rgb_dict,img_rgb[0,0],CHIP_1.top.tag,6,True)

#闭运算
#whj.Close(img_rgb_top,rgb_dict,img_rgb[0,0],CHIP_1.top.tag,6,output=True)

#CHIP_1.top.Close(1)
#
#CHIP_1.top.Show(img_rgb,rgb_dict)
#
#CHIP_2.top.Close(1)

#CHIP_2.top.Show(img_rgb,rgb_dict)

#for this_fraction in CHIP_1.others:
#    
#    print(this_fraction.tag)
#    

##top小事other补上的函数
#def DeleteTop(which_Chip,img_rgb=None,rgb_dict=None,show=False):
#    
#    that_plate=o.plate()
#    that_plate.Init(which_Chip.others)
#
#    if show:
#        that_plate.Show(img_rgb,rgb_dict)
#        
#    return that_plate
#
#"""这时候又如何把-1加进来呢"""
#DeleteTop(CHIP_2)
#DeleteTop(CHIP_2,img_rgb,rgb_dict,True)

#9.11

#for this_fraction in CHIP_2.plate.fractions:
#    
#    if this_fraction.tag==2:
#        
#        CHIP_2.plate.fractions.remove(this_fraction)
# 
#CHIP_2.plate.Show(img_rgb,rgb_dict)   

#在Chip对象中建立fault属性
##fault最后画
#img_rgb=whj.Showfractions(DeleteTop(CHIP_2)+DeleteTop(CHIP_1),img_rgb,rgb_dict,output=True)

#img_tag=whj.RGB2Tag(img_rgb,rgb_dict)
#
#plt.figure()
#
#plt.imshow(TopBaseFault(CHIP_1,img_tag,-50))

#top_fraction,fault_fraction=DeleteTop(CHIP_1,1)

#CHIP_1.Show(img_rgb,rgb_dict)
#
#top_fraction.Show(img_rgb,rgb_dict)
#fault_fraction.Show(img_rgb,rgb_dict)


""""""
#"""斜率有问题，可能是边缘效应"""

#hj=whj.PushUpImg(new_img_tag)
#
#plt.figure()
#
#plt.imshow(hj)



#10.29
#==============================================================================  
#将Chip转化为plate对象
#"""Chip中的块体对象未必能连在一起了，所以不能再通过图像这座桥梁了"""
#def Chip2Plate(which_Chip):
#
#    #新建一个plate对象
#    that_plate=o.plate()
#    
#    #重新定义各项属性
#    that_plate.content=content
##    
# -*- coding:utf-8 -*-
import glob
import matplotlib.pyplot as plt
import configparser
import os
import sys
from PIL import Image
import re

o_path = os.getcwd() # 返回当前工作目录
sys.path.append(o_path) # 添加自己指定的搜索路径
from GetShp.Tool import *

#处理得到x_max,y_max,x_not_missing,y_not_missing
#x_not_missing,y_not_missing是处理图片是没有缺失的图片对应的x和y值
#保存x_max和y_max用于后面设置循环
def handle_xy(strPath):
    x_max=0
    y_max=0
    x_not_missing=[]
    y_not_missing=[]
    nameRe0=re.findall('\d+',os.path.splitext(os.path.basename(strPath[0]))[0])
    x_min=int(nameRe0[0])
    y_min=int(nameRe0[1])
    for i in strPath:
        imageDelPath=os.path.basename(i)#去除路径
        imageName=os.path.splitext(imageDelPath)[0]#取出文件名
        nameRe=re.findall('\d+',imageName)
        x_num=int(nameRe[0])
        y_num=int(nameRe[1])
        x_not_missing.append(x_num)
        y_not_missing.append(y_num)
        if(x_num>x_max):
            x_max=x_num
        if(y_num>y_max):
            y_max=y_num
        if(x_num<x_min):
            x_min=x_num
        if(y_num<y_min):
            y_min=y_num 
    return x_max,y_max,x_not_missing,y_not_missing,x_min,y_min
#根据文件信息转二值图矩阵
#1为黑色，255为白色，再转二值图
#存在为白色，丢失显示黑色
#通过0和255矩阵，判断那些位置需要加入pass字符串，将这些位置保存下来
def convertBImage(x_num,y_num,x_not_missing,y_not_missing,x_min,y_min):
    initialImage=np.zeros((y_num+1,x_num+1),dtype=int)
    listLength=len(x_not_missing)
    l=1
    while l<=listLength:
        initialImage[y_not_missing[l-1]-y_min,x_not_missing[l-1]-x_min]=255
        l=l+1
    image=Image.fromarray(initialImage).convert('1')
    #保存实际大小的二值图
    mpimg.imsave('survey.jpg',image)
    plt.imshow(image)
    #保存显示出来的二值图
    plt.savefig('resultShow.jpg')

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.cfg',encoding='utf-8-sig')
    concatenate=config['Concatenate']
    path=concatenate['path']
    fill_pic=concatenate['fill_pic']
    save_path=concatenate['save_path']
    strPath=glob.glob(os.path.join(path,'*.png'))
    imageChange(fill_pic,strPath[0])
    x_max,y_max,x_not_missing,y_not_missing,x_min,y_min=handle_xy(strPath)
    convertBImage(x_max-x_min,y_max-y_min,x_not_missing,y_not_missing,x_min,y_min)
    stitchingImages(x_max-x_min,y_max-y_min,strPath,path,x_min,y_min,fill_pic,save_path)
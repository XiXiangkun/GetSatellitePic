import glob
import configparser
import os
import sys

o_path = os.getcwd() # 返回当前工作目录
sys.path.append(o_path) # 添加自己指定的搜索路径
from GetShp.Tool import *

config = configparser.ConfigParser()
config.read('config.cfg',encoding='utf-8-sig')
resources=config['Concatenate']
mode=resources['mode']
place=resources['place']
area=[float(e.strip()) for e in resources['area'].split(',')]
path=resources['path']
fill_pic=resources['fill_pic']
save_path=resources['save_path']
strPath=glob.glob(os.path.join(path,'*.png'))
imageChange(fill_pic,strPath[0])
left,top,right,bottom = getGeoForAddress(place) if mode=="1"  else area
pos1x,pos1y=lonlat2xy(left,top,z)
pos2x,pos2y=lonlat2xy(right,bottom,z)
#pos1x,pos1y,pos2x,pos2y=1598,694,1599,695
stitchingImages(pos2x-pos1x,pos2y-pos1y,strPath,path,pos1x,pos1y,fill_pic,save_path)
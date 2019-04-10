import requests
import configparser
import os
import sys

o_path = os.getcwd() # 返回当前工作目录
sys.path.append(o_path) # 添加自己指定的搜索路径
from GetShp.Tool import *
from GetShp.file import *

#爬虫图片并保存成对应格式
def catchPic(x,y,z,path,logger):
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
	source = "https://www.google.cn/maps/vt?lyrs={style}@804&gl=cn&x={x}&y={y}&z={z}"
	furl = source.format(style="s",x=x,y=y,z=z)
	pic=requests.get(url=furl,headers=headers,timeout=20)
	if pic.status_code==403:
		logger.warn('status_code:403 x=%s,y=%s,z=%s'%(x,y,z))
	path_get=getDownloadPath(path,x,y,z)
	fullpath=os.path.join(path_get,'s'+'_'+str(x)+'_'+str(y)+'_'+str(z)+'.png')
	fp=open(fullpath,'wb')
	fp.write(pic.content)
	fp.close()	

def download(mode,place,area,z,path,logger):
	left,top,right,bottom = getGeoForAddress(place) if mode=="1"  else area
	pos1x,pos1y=lonlat2xy(left,top,z)
	pos2x,pos2y=lonlat2xy(right,bottom,z)
	for y in range(pos1y,pos2y+1):
		for x in range(pos1x,pos2x+1):
			catchPic(x,y,z,path,logger)

if __name__ == '__main__':
	config = configparser.ConfigParser()
	config.read('config.cfg',encoding='utf-8-sig')
	GetShp=config['GetSatellite']
	mode=GetShp['mode']
	place=GetShp['place']
	area=[float(e.strip()) for e in GetShp['area'].split(',')]
	z=int(GetShp['z'])
	path=GetShp['path']
	logger=genLogger()
	fileSystem(z,path)
	download(mode,place,area,z,path,logger)
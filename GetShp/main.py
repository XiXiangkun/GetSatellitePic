import requests
import configparser
from GetShp.Tool import *
from GetShp.file import *
import time

#爬虫图片并保存成对应格式
def catchPic(x,y,z,shp_type,url_size,path,logger,f):
	url='https://maps.googleapis.com/maps/api/staticmap?&center={center_lat},{center_lon}&zoom={z}&format=png&maptype=roadmap&style=color:0xffffff&style=element:labels%7Cvisibility:off&style={shp_type}%7Celement:geometry%7Ccolor:0xff0000&size={url_size}'
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
	center_lon,center_lat=xy2lonlat(x,y,z)
	furl=url.format(center_lat=center_lat,center_lon=center_lon,z=z,shp_type=shp_type_list[shp_type[0]],url_size=url_size)
	try:
		pic=requests.get(url=furl,headers=headers,timeout=10)
		#time.sleep(0.2)
		print(pic)
		if pic.status_code==403:
			f.write(str(x)+","+str(y)+",\n")
			logger.warn('status_code:403 x=%s,y=%s,z=%s'%(x,y,z))
		else:
			path_get=getDownloadPath(path,x,y,z)
			dirName = os.path.join(path_get, shp_type[1])
			if not os.path.isdir(dirName):
				os.makedirs(dirName)
			fullpath=os.path.join(dirName,shp_type[1]+'_'+str(x)+'_'+str(y)+'_'+str(z)+'.png')
			fp=open(fullpath,'wb')
			fp.write(pic.content)
			fp.close()
			im=Image.open(fullpath)
			#裁剪图片
			region=im.crop((0,50,256,306))
			region.save(fullpath)
	except:
		logger.warn('disConnect: x=%s,y=%s,z=%s'%(x,y,z))
		f.write(str(x)+","+str(y)+",\n")

def download(url_size,mode,place,area,z,shp_type,path,logger):
	left,top,right,bottom = getGeoForAddress(place) if mode=="1"  else area
	pos1x,pos1y=lonlat2xy(left,top,z)
	pos2x,pos2y=lonlat2xy(right,bottom,z)
	times=1
	fw=open('403_1.txt','w+')
	for y in range(pos1y,pos2y+1):
			for x in range(pos1x,pos2x+1):
				catchPic(x,y,z,shp_type,url_size,path,logger,fw)
	fw.close()
	fr=open('403_1.txt','r')
	while True:
		txt_content=fr.readline()
		if txt_content=='':
			break
		else:
			times=2
		fw=open('403_2.txt','w+')
		while txt_content!='':
			x,y = int(txt_content.split(',')[0]),int(txt_content.split(',')[1])
			catchPic(x,y,z,shp_type,url_size,path,logger,fw)
			txt_content = fr.readline()
		fw.close()
		fr.close()
		os.remove('403_1.txt')
		fr=open('403_2.txt','r')
		txt_content=fr.readline()
		if txt_content=='':
			break
		else:
			times=1
		fw=open('403_1.txt','w+')
		while txt_content!='':
			x,y = int(txt_content.split(',')[0]),int(txt_content.split(',')[1])
			catchPic(x,y,z,shp_type,url_size,path,logger,fw)
			txt_content = fr.readline()
		fw.close()
		fr.close()
		os.remove('403_2.txt')
		fr=open('403_1.txt','r')

def main():
	config = configparser.ConfigParser()
	config.read('config.cfg',encoding='utf-8-sig')
	GetShp=config['GetShp']
	instance = config['GenInstances']
	categories = [e.strip() for e in instance["categories"].split(",")]
	url_size=GetShp['url_size']
	mode=GetShp['mode']
	place=GetShp['place']
	area=[float(e.strip()) for e in GetShp['area'].split(',')]
	z=int(GetShp['z'])
	shp_index = int(GetShp['shp_index'])
	if not -1<shp_index<14:
		shp_index=0
	shp_type=(shp_index,categories[shp_index])
	path=GetShp['path']
	logger=genLogger()
	fileSystem(z,path)
	download(url_size,mode,place,area,z,shp_type,path,logger)
import logging
import os
from math import *
import xml.etree.cElementTree as ET
import numpy as np
import tarfile
import json
import urllib
import urllib.request as ur
import matplotlib.image as mpimg
from PIL import Image
import time


shp_type_list=['feature:road%7Celement:geometry%7Ccolor:0xff0000&style=feature:transit.line','feature:water','feature:road.highway','feature:administrative.country','feature:administrative.province','feature:landscape.man_made','feature:landscape.natural.landcover','feature:landscape.natural.terrain','feature:poi.business','feature:poi.park','feature:road.arterial','feature:road.local','feature:transit.line','feature:transit.station.airport']

def lonlat2xy(lon, lat, z):
    x = floor(((lon+180)/360)*2**z);
    if(x == 2**z):
        x -= 1
    y = floor(2**(z-1)-log(tan(radians(lat))+1/cos(radians(lat)))/(2*pi)*2**z);
    return x,y

# 左上角的纬度
def y2lat(y,z):
    return 90-2*degrees(atan(exp(2*pi*(y-2**(z-1))/2**z)))

#返回中心经纬度
def xy2lonlat(x,y,z):
 lat = y2lat(y,z)
 lat = lat - abs(y2lat(y+1,z)-lat)/2
 lon = (360/2**z)*(x+0.5)-180;
 return lon,lat

def bgInclude(cornerList, areaLatLon):
    left, top, right, bottom = areaLatLon
    for point in cornerList:
        lon, lat = point
        if(left<=lon<=right and bottom<=lat<=top):
            return True
    return False

def changeFileName():
    os.chdir("shp_folder")
    allImgs = os.listdir()
    for name in allImgs:
        suffix = os.path.splitext(name)[1]
        if( suffix=='.jpeg' or suffix=='.jpg' or suffix=='.png'):
            x,y = name.split("_")[1],name.split("_")[2]
            print(x,y)
            os.rename(name,"road_"+str(int(x))+"_"+str(int(y))+"_11.png")

def genLogger():
    logger = logging.getLogger("DataShow")
    logger.setLevel(logging.WARN)
    fh = logging.FileHandler("logger.log")
    fh.setLevel(logging.WARN)
    fmt = "%(asctime)s %(levelname)s %(message)s "
    datefmt = "%Y-%m-%d  %H:%M:%S %a"
    formatter = logging.Formatter(fmt, datefmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def getLatLon(tree, xPath):
    lat,lon = 0,0
    for elem in tree.iterfind(xPath):
        for latlon in elem:
            lat = latlon.text if latlon.tag == 'latitude' else lat
            lon = latlon.text if latlon.tag == 'longitude' else lon
    return lat,lon

def readxml(filename):
    tree = ET.ElementTree(file = filename )
    SAR_map = dict()
    SAR_map['id'] = list(tree.iterfind('productID'))[0].text
    SAR_map['file_name'] = filename
    img_w, img_h = list(tree.iterfind('imageinfo/width'))[0].text, list(tree.iterfind('imageinfo/height'))[0].text
    SAR_map['img_size'] = {"width": img_w, "height": img_h}
    center_lat, center_lon = getLatLon(tree,'imageinfo/center')
    SAR_map['center'] = {"lat": center_lat, "lon": center_lon}
    topleft_lat, topleft_lon = getLatLon(tree,'imageinfo/corner/topLeft')
    topRight_lat, topRight_lon = getLatLon(tree,'imageinfo/corner/topRight')
    bottomLeft_lat, bottomLeft_lon = getLatLon(tree,'imageinfo/corner/bottomLeft')
    bottomRight_lat, bottomRight_lon = getLatLon(tree,'imageinfo/corner/bottomRight')
    SAR_map['corner'] = {"topleft": {"lat": topleft_lat, "lon": topleft_lon},
                        "topRight": {"lat": topRight_lat, "lon": topRight_lon},
                        "bottomRight": {"lat": bottomRight_lat, "lon": bottomRight_lon},
                        "bottomLeft": {"lat": bottomLeft_lat, "lon": bottomLeft_lon}}
    return SAR_map

def findxmls(filenames):
    SAR_maps = list()
    os.chdir('xml')
    for filename in filenames:
        SAR_maps.append(readxml(filename))
    return SAR_maps

def extract(logger):
    if not os.path.isdir("xml"):
        os.makedirs("xml")
        xmlfiles = []
    else:
        xmlfiles = os.listdir("xml")
    filenames = []
    for gzip_name in os.listdir():
        has = False
        if("tar.gz" in gzip_name):
            for xmlfile in xmlfiles:
                #为了速度快，如果xml中已经有了该压缩包中的文件就不再解压压缩包
                if(gzip_name.split(".tar.")[0] in xmlfile):
                    filenames.append(xmlfile)
                    # print("has:"+xmlfile)
                    has = True
                    break
            if(not has):
                tar = tarfile.open(gzip_name)
                isXml = False
                for name in tar.getnames():
                    if("meta.xml" in name):
                        isXml = True
                        # print("no has and extract:"+name)
                        filenames.append(name)
                        tar.extract(name,path="xml")
                        break
                if(not isXml):
                    logger.warn("xml not found:"+gzip_name)
                tar.close()
    return filenames

def genJson(filepath,logger):
    #同级目录下要有一个文件夹存放压缩包
    os.chdir(filepath)
    filenames = extract(logger)
    SAR_maps = findxmls(filenames)
    os.chdir(os.path.join("..",".."))
    f = open(os.path.join(filepath,'SAR_map.json'),'w')
    f.write(json.dumps(SAR_maps))
    f.close()

# 根据瓦片坐标获取图像数据
def getdata(x,y,z,style='s'):
    source = "https://www.google.cn/maps/vt?lyrs={style}@804&gl=cn&x={x}&y={y}&z={z}"
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36'}
    furl = source.format(x=x,y=y,z=z,style=style)
    req = ur.Request(url=furl, headers=headers)
    # time.sleep(0.5)
    try:
        data=ur.urlopen(req,timeout=5).read()
    except:
        print("get picture failed!")
        print("url:",furl)
        exit()
    return data

#从Json文件中读取数据图片的四个角信息
def getCornerListByJson(corner):
    cornerList = list()
    for point in list(corner.values()):
        t = (float(point['lon']),float(point['lat']))
        cornerList.append(t)
    return cornerList

#从文件名中读取xy 算出数据图片的四个角信息
def getCornerListByName(filename):
    nameSplit = filename.split("_")
    x,y,z = int(nameSplit[1]), int(nameSplit[2]), int(nameSplit[3])
    left, top = 360*(x/2**z)-180, y2lat(y,z)
    latSpan = abs(top-y2lat(y+1,z)) #纬度跨度
    lonSpan = 360*(0.5/2**z) #经度跨度
    right, bottom = left+lonSpan, top-latSpan
    return [(left,top), (right,top), (right,bottom), (left,bottom)]

#将四个角连成的轮廓画在背景上
def drawArea(draw,cornerList,color,imgWH):
    # print("drawArea:" + str(cornerList))
    imgW,imgH = imgWH
    polygons = []
    for point in cornerList:
        lon, lat = point
        x = floor((0.5+lon/360)*imgW);
        y = floor((0.5-log(tan(radians(lat))+1/cos(radians(lat)))/(2*pi))*imgH);
        polygons.append(x)
        polygons.append(y)
    # print(polygons)
    draw.polygon(polygons, fill=color)

def pointInPolygon(point, verts):
    """
    - PNPoly算法
    - xyverts  [(x1, y1), (x2, y2), (x3, y3), ...]
    """

    x, y = point
    vertx = [xyvert[0] for xyvert in verts]
    verty = [xyvert[1] for xyvert in verts]
    # 判断是否在最小外接四边形内
    if not verts or not min(vertx) <= x <= max(vertx) or not min(verty) <= y <= max(verty):
        return False
    # 上一步通过后，核心算法部分
    nvert = len(verts)
    is_in = False
    for i in range(nvert):
        j = nvert - 1 if i == 0 else i - 1
        if ((verty[i] > y) != (verty[j] > y)) and (
                    x < (vertx[j] - vertx[i]) * (y - verty[i]) / (verty[j] - verty[i]) + vertx[i]):
            is_in = not is_in
    return is_in

#获取对应城市的经纬度
def getGeoForAddress(address):
    #address = "北京"
    #addressUrl = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address
    addressUrl='https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key=AIzaSyAadVAdjp_hGd21y9y-R6wQ0IcOcHcrl9c'
    #中文url需要转码才能识别
    addressUrlQuote = urllib.parse.quote(addressUrl, ':?=/')
    response = ur.urlopen(addressUrlQuote).read().decode('utf-8')
    try:
        res = json.loads(response)['results'][0]['geometry']['bounds']
        #获取北京的西南和东北边界坐标经纬度
        top = res['northeast']['lat']
        right = res['northeast']['lng']
        bottom = res['southwest']['lat']
        left = res['southwest']['lng']
    except:
        # logger.error('getGeoForAddress error')
        exit()
    #返回北京的西南和东北边界坐标经纬度
    return left,top,right,bottom

def imageChange(fill_pic,strPath):
    black = Image.open(fill_pic)
    image = Image.open(strPath)
    blackRGBA = black.convert(image.mode)
    blackRGBA.save(fill_pic)

#图片拼接函数
#与最后的if判断对应，row==y_num+1时，循环已经结束
#column<x_num是因为列图的第一张单独取出，循环只用处理x_num数量的图
def stitchingImages(x_num,y_num,strPath,path,x_min,y_min,fill_pic,save_path):
    row=0
    column=0
    imageTemporary=[]
    while row!=y_num+1:
        column=0
        imageType=os.path.splitext(os.path.basename(strPath[0]))[0].split('_')[0]
        z=os.path.splitext(os.path.basename(strPath[0]))[0].split('_')[3]
        pic_path=os.path.join(path,imageType+'_'+str(x_min)+'_'+str(y_min+row)+'_'+z+'.png')
        imageCombine=mpimg.imread(pic_path,0)
        while column<x_num:
            pic_path=os.path.join(path,imageType+'_'+str(x_min+column+1)+'_'+str(y_min+row)+'_'+z+'.png')
            try:
                imageAdd=mpimg.imread(pic_path,0)
            except:
                imageAdd=mpimg.imread(fill_pic,0)
            imageCombine=np.concatenate((imageCombine,imageAdd),1)
            column=column+1
        row=row+1
        #拼接的图临时保存
        imageTemporary.append(imageCombine)
    #列图的横向拼接
    imageCombine2=imageTemporary[0]
    for i in imageTemporary[1:]:
        imageCombine2=np.concatenate((imageCombine2,i))
        mpimg.imsave(os.path.join(save_path,'conResult.png'),imageCombine2)
    del imageTemporary
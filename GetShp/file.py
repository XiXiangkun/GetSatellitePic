import os
import math

# 文件管理系统创建；
NUM2_5=32
NUM2_10=1024
NUM2_15=32768

def txtFile(dirName_z,x,y,x_2,y_2,x_3,y_3,mode):
	if mode==0:
		num_x_s=NUM2_5*x;num_x_e=NUM2_5*(x+1)-1
		num_y_s=NUM2_5*y;num_y_e=NUM2_5*(y+1)-1
	elif mode==1:
		num_x_s=NUM2_10*x+NUM2_5*x_2;num_x_e=NUM2_10*x+NUM2_5*(x_2+1)-1
		num_y_s=NUM2_10*y+NUM2_5*y_2;num_y_e=NUM2_10*y+NUM2_5*(y_2+1)-1
	elif mode==2:
		num_x_s=NUM2_15*x+NUM2_10*x_2+NUM2_5*x_3;num_x_e=NUM2_15*x+NUM2_10*x_2+NUM2_5*(x_3+1)-1
		num_y_s=NUM2_15*y+NUM2_10*y_2+NUM2_5*y_3;num_y_e=NUM2_15*y+NUM2_10*y_2+NUM2_5*(y_3+1)-1
	else:
		pass
	txtPath=os.path.join(dirName_z,'info.txt')
	f=open(txtPath,'a+')
	f.write('x_start:'+str(num_x_s)+'\nx_end:'+str(num_x_e)+'\n')
	f.write('y_start:'+str(num_y_s)+'\ny_end:'+str(num_y_e)+'\n')
	f.close()
	
def makeDir(dirName):
	if not os.path.isdir(dirName):
		os.makedirs(dirName)

def loop(num,dirName,mode):
	for x in range(0,2**num):
		for y in range(0,2**num):
			dirName_z = os.path.join(dirName, 'x_'+str(x)+'y_'+str(y))
			makeDir(dirName_z)
			if mode==0:
				txtFile(dirName_z,x,y,0,0,0,0,0)
			elif mode==1 or mode==2:
				for x_2 in range(0,NUM2_5):
					for y_2 in range(0,NUM2_5):
						dirName_z_2 = os.path.join(dirName_z, 'x_'+str(x_2)+'y_'+str(y_2))
						makeDir(dirName_z_2)
						if mode==1:
							txtFile(dirName_z_2,x,y,x_2,y_2,0,0,1)
						elif mode==2:
							for x_3 in range(0,NUM2_5):
								for y_3 in range(0,NUM2_5):
									dirName_z_3 = os.path.join(dirName_z_2, 'x_'+str(x_3)+'y_'+str(y_3))
									makeDir(dirName_z_3)
									txtFile(dirName_z_3,x,y,x_2,y_2,x_3,y_3,2)

def fileSystem(z,path):
	dirName = os.path.join(path, str(z))
	makeDir(dirName)
	if z<=5:
		txtPath=os.path.join(dirName,'info.txt')
		f=open(txtPath,'a+')
		f.write('x_start:0\nx_end:'+str(2**z-1)+'\n')
		f.write('y_start:0\ny_end:'+str(2**z-1)+'\n')
		f.close()
		return
	elif z<=10:
		loop(z-5,dirName,0)
		return
	elif z<=15:
		loop(z-10,dirName,1)
		return
	elif z<=20:
		loop(z-15,dirName,2)
		return

def getDownloadPath(path,x,y,z):
	if z<=5:
		downloadPath = os.path.join(path, str(z))
	elif z<=10:
		path_1='x_'+str(math.floor(x/NUM2_5))+'y_'+str(math.floor(y/NUM2_5))
		downloadPath = os.path.join(path,str(z),path_1)
	elif z<=15:
		x_1=math.floor(x/NUM2_10);y_1=math.floor(y/NUM2_10)
		print(x_1,y_1)
		path_1='x_'+str(x_1)+'y_'+str(y_1)
		path_2='x_'+str(math.floor((x-x_1*NUM2_10)/NUM2_5))+'y_'+str(math.floor((y-y_1*NUM2_10)/NUM2_5))
		downloadPath = os.path.join(path,str(z),path_1,path_2)
	elif z<=20:
		x_1=math.floor(x/NUM2_15);y_1=math.floor(y/NUM2_15)
		x_2=math.floor((x-x_1*NUM2_15)/NUM2_10);y_2=math.floor((y-y_1*NUM2_15)/NUM2_10)
		path_1='x_'+str(x_1)+'y_'+str(y_1)
		path_2='x_'+str(x_2)+'y_'+str(y_2)
		path_3='x_'+str(math.floor((x-x_1*NUM2_15-x_2*NUM2_10)/NUM2_5))+'y_'+str(math.floor((y-y_1*NUM2_15-y_2*NUM2_10)/NUM2_5))
		downloadPath = os.path.join(path,str(z),path_1,path_2,path_3)
	return downloadPath


#fileSystem(11,r'D:\shixi_result\progress\final\try')
print(getDownloadPath('a',29,365,11))

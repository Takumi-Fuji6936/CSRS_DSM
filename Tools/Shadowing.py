# coding: utf-8
import math
import numpy as np
from osgeo import gdal
import sys
import os
import re
#import osr
from tqdm import tqdm

def Shadow(f1,SZA,SAA,f2):
	#処理する画像の読み込み
	dat= gdal.Open(f1, gdal.GA_ReadOnly)
	geotransform= dat.GetGeoTransform()


	 
	#画像を配列に変換
	dsm = np.array(dat.GetRasterBand(1).ReadAsArray())


	#xとyのピクセル数取得
	x_pixels = dat.RasterXSize
	y_pixels = dat.RasterYSize

	#xとyのピクセルサイズの取得
	PIXEL_SIZE_x = geotransform[1]
	PIXEL_SIZE_y = geotransform[5]
	#print PIXEL_SIZE_x,PIXEL_SIZE_y

	#画像の左上の座標の取得
	x_min = geotransform[0] 
	y_max = geotransform[3]

	#Shadowを格納する配列
	shadow=np.zeros((y_pixels,x_pixels),np.uint8)
	#print dsm.shape,shadow.shape

	#SUN_AZIMUTH = 131.24202951
	#SUN_ELEVATION = 62.21167254

	SUN_ZENITH = math.radians(SZA)
	SUN_AZIMUTH = math.radians(90-SAA)
	SUN_ELEVATION = math.radians(90 - SZA)
	

	Sun_x=1.0*math.cos(SUN_ELEVATION)*math.cos(SUN_AZIMUTH)
	Sun_y=1.0*math.cos(SUN_ELEVATION)*math.sin(SUN_AZIMUTH)
	Sun_z=-1.0*math.sin(SUN_ELEVATION)

	Sun_x=math.cos(SUN_AZIMUTH) 
	Sun_y=math.sin(SUN_AZIMUTH) 
	Sun_z=math.tan(SUN_ELEVATION) 
	print (Sun_x,Sun_y,Sun_z)
	
	for i in tqdm(range(x_pixels)):

		for j in range(y_pixels):
			
			#対象ピクセル
			dsm_x=i
			dsm_y=j
			dsm_z=dsm[j][i]
			#print dsm_x,dsm_y,dsm_z
			
			if dsm_z<=0.0:
				continue

			else:	
				k=0
				#print j
				x=0
				y=0
				while x <= x_pixels-1 and y<= y_pixels-1 :
					k+=1
					x=i + math.cos(SUN_AZIMUTH) * k
					y=j -math.sin(SUN_AZIMUTH) * k
					z=dsm_z + math.tan(SUN_ELEVATION) * k
					
					#print dsm[int(y)][int(x)]
					
					if dsm[int(y)][int(x)] >= z:
						#print dsm_z,z
						shadow[j][i]=1
						break
		#print (i,j)	
				
			
	driver = gdal.GetDriverByName('GTiff')


	#編集後の画像の画素数と型の設定
	dataset = driver.Create(
	        f2,#処理後の画像名
	        x_pixels,
	        y_pixels,
	        #バンド数
	        1,
	        gdal.GDT_Float64, )

	#編集後の画像の位置情報の設定
	dataset.SetGeoTransform((
	        x_min,  
	        PIXEL_SIZE_x, 
	        0,     
	        y_max,   
	        0,   
	        -PIXEL_SIZE_x))  

	#処理した画像の保存
	#srs = osr.SpatialReference()
	#srs.SetUTM( 53, 1 )
	#dataset.SetProjection( srs.ExportToWkt() )
	dataset.GetRasterBand(1).WriteArray(shadow)   # write r-band to the raster

	dataset.FlushCache()  
	dataset = None    
	

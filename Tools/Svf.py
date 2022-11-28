# coding: utf-8
import numpy as np
from osgeo import gdal
from osgeo import gdal_array
import math
import time
from tqdm import tqdm
from numba import double
from numba import jit,u2,f4,i8,u2,i4,i2
import glob
import re

#if __name__ == '__main__':
def Svf(f1,f2,f3):
	#処理する画像の読み込み
	dat1= gdal.Open(f1, gdal.GA_ReadOnly)
	geotransform= dat1.GetGeoTransform()

	#配列に変換
	Azi_land= np.array(dat1.GetRasterBand(1).ReadAsArray()).astype(np.float32)
	Zeni_land= np.array(dat1.GetRasterBand(2).ReadAsArray()).astype(np.float32)

	#xとyのピクセル数取得
	x_pixels = dat1.RasterXSize
	y_pixels = dat1.RasterYSize

	#画像の左上の座標の取得
	x_min = geotransform[0] 
	y_max = geotransform[3]

	#xとyのピクセルサイズの取得
	PIXEL_SIZE_x = geotransform[1]
	PIXEL_SIZE_y = geotransform[5]

	Azi_land = np.deg2rad(Azi_land)
	Zeni_land = np.deg2rad(Zeni_land)



	file = glob.glob(f2+'*.tif')

	#print(file)
	N_file = len(file)
	print(N_file)
	n=0
	Svf=0
	for f in file:
		
		try:
			Azimth = math.radians(float(re.split(r'[\\_]', file[n])[2]))
		except:
			Azimth = math.radians(float(re.split('[/_]', file[n])[2]))

		#print(f,Azimth)
		#処理する画像の読み込み
		dat1= gdal.Open(f, gdal.GA_ReadOnly)
		geotransform= dat1.GetGeoTransform()

		#配列に変換
		Hori= np.array(dat1.GetRasterBand(1).ReadAsArray()).astype(np.float32)

		Hori_angle = math.pi/2 - np.arctan(Hori)

		Sv_1 = np.cos(Zeni_land)*np.sin(Hori_angle)*np.sin(Hori_angle)
		Sv_2 = np.sin(Zeni_land)*np.cos(Azimth- Azi_land )
		Sv_3 = Hori_angle - np.sin( Hori_angle ) * np.cos( Hori_angle )

		Svf = Svf + Sv_1 + Sv_2 * Sv_3
		
		n+=1
	
	#Svf = Svf /(2 * math.pi)
	Svf = Svf / N_file

	driver = gdal.GetDriverByName('GTiff')


	#編集後の画像の画素数と型の設定
	dataset = driver.Create(
			f3,#処理後の画像名
			x_pixels,
			y_pixels,
			#バンド数
			1,
			gdal.GDT_Float32, )

	#編集後の画像の位置情報の設定
	dataset.SetGeoTransform((
			x_min,  
			PIXEL_SIZE_x, 
			0,     
			y_max,   
			0,   
			-PIXEL_SIZE_x))  


	dataset.GetRasterBand(1).WriteArray(Svf)
	dataset.FlushCache()  
	dataset = None
	
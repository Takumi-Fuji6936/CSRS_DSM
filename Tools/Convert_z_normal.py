# coding: utf-8
import numpy as np
import pandas as pd
import sys
import math
from osgeo import gdal
from osgeo import gdal_array
import numpy.linalg as LA
from tqdm import tqdm


def ZtoN(f1,f2):

	#処理する画像の読み込み
	dat= gdal.Open(f1, gdal.GA_ReadOnly)
	geotransform= dat.GetGeoTransform()

	DSM = np.array(dat.GetRasterBand(1).ReadAsArray())

	#xとyのピクセル数取得
	x_pixels = dat.RasterXSize
	y_pixels = dat.RasterYSize

	#画像の左上の座標の取得
	x_min = geotransform[0] 
	y_max = geotransform[3]
	#xとyのピクセルサイズの取得
	PIXEL_SIZE_x = geotransform[1]
	PIXEL_SIZE_y = geotransform[5]


	L=np.zeros((y_pixels,x_pixels),np.float32)
	M=np.zeros((y_pixels,x_pixels),np.float32)
	N=np.zeros((y_pixels,x_pixels),np.float32)



	for i in tqdm(range(1,y_pixels-1)):
		for j in range(1,x_pixels-1):
					
			DAM_1=DSM[i-1][j-1]
			DAM_2=DSM[i-1][j]
			DAM_3=DSM[i-1][j+1]
			DAM_4=DSM[i][j-1]
			DAM_5=DSM[i][j]
			DAM_6=DSM[i][j+1]
			DAM_7=DSM[i+1][j-1]
			DAM_8=DSM[i+1][j]
			DAM_9=DSM[i+1][j+1]

			

			X = np.array((-0.1,0.0,0.1,
				          -0.1,0.0,0.1,
				          -0.1,0.0,0.1))

			#X=X-DAM_5[0]
			
			Y = np.array((0.1,0.1,0.1,
				          0.0,0.0,0.0,
				          -0.1,-0.1,-0.1))

			#Y=Y-DAM_5[1]
			#print(Y)
			Z = np.array((DAM_1,DAM_2,DAM_3,
				          DAM_4,DAM_5,DAM_6,
				          DAM_7,DAM_8,DAM_9))
			#print(Z)
			#Z=Z-DAM_5[2]


			#print(Z)
			XX = np.sum(X*X)
			XY = np.sum(Y*X)
			XZ = np.sum(X*Z)
			YZ = np.sum(Y*Z)
			YY = np.sum(Y*Y)
			ZZ = np.sum(Z*Z)
			Y_ = np.sum(Y)
			Z_ = np.sum(Z)
			X_ = np.sum(X)

			MM = np.array([[XX,XY,XZ],
				           [XY,YY,YZ],
				           [XZ,YZ,ZZ]])

			#print(MM)
			A = np.array([[X_],
				          [Y_],
				          [Z_]])
			

			M_det = LA.det(MM)
			#print (MM)

			#if  len(np.where(Z>1)[0])==9:	
			if  M_det!=0 :	
				inv_M = np.linalg.inv(MM)


				Q = np.dot(inv_M,A)
				UU= math.sqrt(Q[0]**2+Q[1]**2+Q[2]**2)#ベクトルの長さ
				#print(UU)
				L[i][j] = Q[0][0]/UU
				M[i][j] = Q[1][0]/UU
				N[i][j] = Q[2][0]/UU
				#print  (UU,Z,Q[2][0]/UU)

	driver = gdal.GetDriverByName('GTiff')

	#編集後の画像の画素数と型の設定
	dataset = driver.Create(
	        f2,#処理後の画像名
	        x_pixels,
	        y_pixels,
	        3,
	        gdal.GDT_Float32, )

	#編集後の画像の位置情報の設定
	dataset.SetGeoTransform((
	        x_min,
	        PIXEL_SIZE_x,
	        0,
	        y_max,
	        0,
	        -PIXEL_SIZE_x))  

	#処理した画像の保存
	dataset.GetRasterBand(1).WriteArray(L)
	dataset.GetRasterBand(2).WriteArray(M)
	dataset.GetRasterBand(3).WriteArray(N)
	
	dataset.FlushCache()  

	return 0
# coding: utf-8
import numpy as np
from osgeo import gdal
from osgeo import gdal_array
import math
import time
from tqdm import tqdm
from numba import double
from numba import jit,u2,f4,i8,u2,i4,i2

@jit(f4[:,:](i8,i8,f4[:,:],i4[:,:],f4[:,:],f4), nopython=True)
def Horizon_numba(y_pixels,Max_Number,DSM,Horizon,Angle,PIXEL_SIZE_x):
	
	for k in range(y_pixels):
		#初期値
		J = Max_Number - 1
		I = J - 1
		Horizon[k][Max_Number] = Max_Number
		Horizon[k][J] = Max_Number

		
		Angle[k][J] = ( DSM[k][Max_Number] - DSM[k][J] )/ PIXEL_SIZE_x #( Max_Number - J )

		while I >=0:
			#print(J,I)
			S_J_I = ( DSM[k][J] - DSM[k][I] )/ ( PIXEL_SIZE_x*( J - I ) )
			S_J   = Angle[k][J]
			
			
			if S_J_I < S_J:

				J = Horizon[k][J]

				if J ==	Max_Number:
					Horizon[k][I] = J
					Angle[k][I] = ( DSM[k][Max_Number] - DSM[k][I] )/ ( PIXEL_SIZE_x*( Max_Number - I ) )
					J = I
					I = J - 1
				#print(J)
			else:
				Horizon[k][I] = J
				Angle[k][I] = S_J_I #( DSM[k][J] - DSM[k][I] )/ ( PIXEL_SIZE_x*( J - I ) )
				J = I
				I = J - 1
				#print(J,I)
		
	return Angle

@jit(f4[:,:](i8,i8,i2,f4,f4[:,:],f4[:,:]), nopython=True)
def Qubic_numba(x_pixels,y_pixels,Kakudai,Rotaion,DSM,After):

	New_x_pixels = x_pixels + Kakudai
	New_y_pixels = y_pixels + Kakudai

	x_center = int(x_pixels/2)
	y_center = int(y_pixels/2)

	Add = int(Kakudai/2)
	Theta = Rotaion * 3.14159265359/180.0
	Alfa = -0.5#-0.75

	Cos = math.cos(Theta)
	Sin = math.sin(Theta)
	
	for i in range(New_y_pixels):
		for j in range(New_x_pixels):
			#変換後画像左下原点へ変換 拡大前の座標
			After_x = j - Add
			After_y = (New_y_pixels - i) -Add
			#変換前画像左下原点
			Befor_x =  Cos*( After_x - x_center ) +  Sin*( After_y - y_center ) + x_center 
			Befor_y = -Sin*( After_x - x_center ) +  Cos*( After_y - y_center ) + y_center 


			#左上原点へ変換
			jj = Befor_x
			ii = y_pixels - Befor_y

			JJ = int(jj)
			II = int(ii)
			Weight=0.0
			
			if ii>=2 and ii<= y_pixels-3 and jj >=2 and jj<= x_pixels-3:



				#対象ピクセルの周囲4*4ピクセルの格納
				SRC = np.array([ [ DSM[II-1][JJ-1],DSM[II-1][JJ],DSM[II-1][JJ+1],DSM[II-1][JJ+2] ],
								 [ DSM[II][JJ-1]  ,DSM[II][JJ]  ,DSM[II][JJ+1]  ,DSM[II][JJ+2]   ],
								 [ DSM[II+1][JJ-1],DSM[II+1][JJ],DSM[II+1][JJ+1],DSM[II+1][JJ+2] ],
								 [ DSM[II+2][JJ-1],DSM[II+2][JJ],DSM[II+2][JJ+1],DSM[II+2][JJ+2] ] ])


				#X方向の距離格納
				X = np.array((1 + jj - JJ,    jj - JJ,
					          1 - jj + JJ,2 - jj + JJ))
				

				#Y方向の距離格納
				Y = np.array((1 + ii - II,    ii - II,
					          1 - ii + II,2 - ii + II))
				

				for m in range(4):
					XX = X[m]
					if XX<0.0:
						XX = -XX

					if XX>=0 and XX<1:
						X_weihgt =  1 - ( Alfa + 3) * XX * XX  +( Alfa + 2 ) * XX * XX *XX
						 
					elif XX >= 1 and XX < 2:
						X_weihgt = -4 * Alfa + 8 * Alfa * XX - 5 * Alfa * XX * XX + Alfa * XX * XX * XX
						
					else  :
						X_weihgt  = 0



					for n in range(4):
						YY = Y[n]

						if YY<0.0:
							YY = -YY

						if YY>=0 and YY<1:
							Y_weihgt =  1 - ( Alfa + 3) * YY * YY  +( Alfa + 2 ) * YY * YY *YY

						elif YY >= 1 and YY < 2:
							Y_weihgt = -4 * Alfa + 8 * Alfa * YY - 5 * Alfa * YY* YY + Alfa * YY * YY * YY
							
						else  :
							Y_weihgt = 0

						Weight = Weight+SRC[n][m] * X_weihgt * Y_weihgt 
				
				if Weight<0.0:
					Weight = 0.0
				else:
					Weight = Weight
				After[i][j] = Weight
				
	return After

#if __name__ == '__main__':
def Horizon(f1,f2):
	#処理する画像の読み込み
	dat1= gdal.Open(f1, gdal.GA_ReadOnly)
	geotransform= dat1.GetGeoTransform()

	#配列に変換
	DSM= np.array(dat1.GetRasterBand(1).ReadAsArray()).astype(np.float32)

	#xとyのピクセル数取得
	x_pixels = dat1.RasterXSize
	y_pixels = dat1.RasterYSize

	#画像の左上の座標の取得
	x_min = geotransform[0] 
	y_max = geotransform[3]
	#xとyのピクセルサイズの取得
	PIXEL_SIZE_x = geotransform[1]
	PIXEL_SIZE_y = geotransform[5]

	t = time.time()
	
	list = np.array((0.00,22.5,45.0,67.5,90,
					 112.5,135.0,157.5,180.0,
					 202.5,225.0,247.5,270.0,
					 292.5,315.0,337.5))
	list_name = np.where((list>=0) & (list<=270),90+list,list-270)
	#print( list_name )
	#print(aaaaaaaa)
	Kakudai = 1500

	New_x_pixels = x_pixels + Kakudai
	New_y_pixels = y_pixels + Kakudai
	After = np.zeros( (New_y_pixels , New_x_pixels )).astype(np.float32)
	
	
	Max_Number = int(New_x_pixels - 1) #x配列方向番号の最大値
	for kk,ll in zip(list,list_name):

		if kk ==0:
			Max_ = int(x_pixels - 1)
			Horizon = np.zeros( (y_pixels , x_pixels )).astype(np.int32)#地平線となる場所
			Angle   = np.zeros( (y_pixels , x_pixels )).astype(np.float32)#地平線の角度
			Out=Horizon_numba(y_pixels,Max_,DSM,Horizon,Angle,PIXEL_SIZE_x)

		else:
			Horizon = np.zeros( (New_y_pixels , New_x_pixels )).astype(np.int32)#地平線となる場所
			Angle   = np.zeros( (New_y_pixels , New_x_pixels )).astype(np.float32)#地平線の角度
			Kakudai = 1500
			After = np.zeros( (New_y_pixels , New_x_pixels )).astype(np.float32)
			
			R_DSM=Qubic_numba(x_pixels,y_pixels,Kakudai,kk,DSM,After)


			Horizon_=Horizon_numba(New_y_pixels,Max_Number,R_DSM,Horizon,Angle,PIXEL_SIZE_x)

			
			Kakudai = -Kakudai
			Re_R = np.zeros( (y_pixels , x_pixels )).astype(np.float32)
			Out = Qubic_numba(New_x_pixels,New_y_pixels,Kakudai,-1.0*kk,Horizon_,Re_R)
			
			print (ll,"numba2:", time.time() - t)

		driver = gdal.GetDriverByName('GTiff')


		#編集後の画像の画素数と型の設定
		dataset = driver.Create(
				f2+str(ll)+"_azimth.tif",#処理後の画像名
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


		dataset.GetRasterBand(1).WriteArray(Out)
		dataset.FlushCache()  
		dataset = None
	
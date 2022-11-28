# coding: utf-8
import numpy as np
import pandas as pd
import sys
import math
#import cv2
from osgeo import gdal
from osgeo import gdal_array
import numpy.linalg as LA
from tqdm import tqdm


def NtoA(f1,f2):


        #処理する画像の読み込み
        dat= gdal.Open(f1, gdal.GA_ReadOnly)
        geotransform= dat.GetGeoTransform()
         
        #画像を配列に変換
        l = np.array(dat.GetRasterBand(1).ReadAsArray())
        m = np.array(dat.GetRasterBand(2).ReadAsArray())
        n = np.array(dat.GetRasterBand(3).ReadAsArray())

        #xとyのピクセル数取得
        x_pixels = dat.RasterXSize
        y_pixels = dat.RasterYSize

        #画像の左上の座標の取得
        x_min = geotransform[0] 
        y_max = geotransform[3]
        #xとyのピクセルサイズの取得
        PIXEL_SIZE_x = geotransform[1]
        PIXEL_SIZE_y = geotransform[5]



        Azimuth = np.rad2deg(np.arctan2(m,l))

        Azimuth = np.where(Azimuth<0,360+Azimuth,Azimuth)
        Azimuth = np.where((Azimuth>=0) & (Azimuth<=90),270+Azimuth,Azimuth-90)
        #Azimuth = np.where((Azimuth>=90) & (Azimuth<360),Azimuth-90,Azimuth)
        #print( np.min(Azimuth),np.max(Azimuth) )
        Azimuth = 360 - Azimuth

        Zenith = np.degrees(np.arccos( n ))




        driver = gdal.GetDriverByName('GTiff')

        #編集後の画像の画素数と型の設定
        dataset = driver.Create(
                f2,#処理後の画像名
                x_pixels,
                y_pixels,
                2,
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
        dataset.GetRasterBand(1).WriteArray(Azimuth )
        dataset.GetRasterBand(2).WriteArray( Zenith )

        dataset.FlushCache()  


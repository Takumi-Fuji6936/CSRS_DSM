import pandas as pd
import sys
import numpy as np
import glob
import re
import os
from Tools import Convert_normal_angle
from Tools import Convert_z_normal
from Tools import Rotation_Horizon
from Tools import Svf
from Tools import Shadowing
from Tools import Reflectance


#シミュレートする衛星センサが観測した日付け
date_Y = "2020"
date_M = "04" 
date_D = "12"

#シミュレートする衛星センサが観測した日での太陽幾何条件
SZA = 10
SAA = 130

#シミュレートするバンド。バンド名はParameter/Lambda.csvに従う
tar_Band = "B8A"

#使用する端末によりwinかmacを選んでください。
#Win
"""
inp = "inp\\raster100cm.tif"
out_z ="temp\\Normal.tif"
out_h = "temp\\Horizon\\"
out_n = "temp\\Angle.tif"
out_svf = "out\\SVF.tif"
out_shadow = "out\\Shadow.tif"
out_ref = "out\\Reflectance"

#対象バンドの波長情報
Lambda = pd.read_csv("Parameter\\Lambda.csv")
#センサの波長応答関数
SRF = pd.read_csv("Parameter\\Sensor_SRF\\SRF_S2A.csv")
#葉の分光反射率
SP_leaf = pd.read_csv("Parameter\\SR\\canopy.txt",delim_whitespace=True,names=("wl","Ref"))
#指定した日におけるバンドごとの放射照度
IR = "Parameter\\Irradiance"
"""

#mac
inp = "inp/raster100cm.tif"
out_z ="temp/Normal.tif"
out_h = "temp/Horizon/"
out_n = "temp/Angle.tif"
out_svf = "out/SVF.tif"
out_shadow = "out/Shadow.tif"
out_ref = "out/Reflectance"

Lambda = pd.read_csv("Parameter/Lambda.csv")
SRF = pd.read_csv("Parameter/Sensor_SRF/SRF_S2A.csv")
SP_leaf = pd.read_csv("Parameter/SR/canopy.txt",delim_whitespace=True,names=("wl","Ref"))
IR = "Parameter/Irradiance"


Shadowing.Shadow(inp,SZA,SAA,out_shadow)

Convert_z_normal.ZtoN(inp,out_z)

Rotation_Horizon.Horizon(inp,out_h)

Convert_normal_angle.NtoA(out_z,out_n)

Svf.Svf(out_n,out_h,out_svf)

Reflectance.Reflectance(out_svf,out_shadow,Lambda,tar_Band,SRF,SP_leaf,IR,date_Y,date_M,date_D,out_ref)

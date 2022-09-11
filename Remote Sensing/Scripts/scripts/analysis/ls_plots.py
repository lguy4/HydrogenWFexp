import argparse
import datacube
import numpy as np
import matplotlib.pyplot as plt
import os


### create cl arguments
parser = argparse.ArgumentParser()

parser.add_argument('--prod', nargs = 1, type=str, required=True, 
    help="--prod 'name_of_data_product:str'")
parser.add_argument('--measure', nargs = 1, type = str, required = True,
    help= "--measure 'comma_sep_measurements:str'")

parser.add_argument('--time', nargs = 1, type = str, required = True, 
    help= "--time 'comma_sep_list_of_times:fmt(yyyy-mm-dd)'")  
parser.add_argument('--lat', nargs = 1, type=str, required=True, 
    help="--lat 'lat_min:float, lat_max:float'")
parser.add_argument('--lon', nargs = 1, type=str, required=True, 
    help="--lon 'lon_min:float, lon_max:float'")
parser.add_argument('--crs', nargs = 1, type = str, required = True)
parser.add_argument('--res', nargs = 1, type = str, required = True)




args = parser.parse_args()

### gather input data for dc.load from command line arguments
prod = args.prod[0]
measure = args.measure[0].split(",")
time = tuple(args.time[0].split(","))
if len(args.lat[0].split(",")) == 2:
    lat = tuple([float(x) for x in args.lat[0].split(",")])
else:
    raise Exception("Arguments must be of the form: --lat 'lat_min:float, lat_max:float'")

if len(args.lon[0].split(",")) == 2:
    lon = tuple([float(x) for x in args.lon[0].split(",")])
else:
    raise Exception("Arguments must be of the form: --lon 'lon_min:float, lon_max:float'")
crs = args.crs[0]
res = tuple([int(r) for r in args.res[0].split(",")])


# python s1a_plots.py --prod "s1_grd" --measure "vv,vh" --time "2021-10-31" --lat "32.925658, 33.004151" --lon "-96.768169, -96.614618" --crs "EPSG:32614" --res "-1, 1"

# dc = datacube.Datacube()

# ds = dc.load(product = prod, measurements=measure, time = time, 
# longitude=lon, latitude=lat, output_crs = crs, 
# resolution = res)

# list of products 
# [ 'ls1_level1_usgs_GS',
#  'ls1_level1_usgs_TP',
#  'ls2_level1_usgs_GS',
#  'ls2_level1_usgs_TP',
#  'ls3_level1_usgs_GS',
#  'ls3_level1_usgs_TP',
#  'ls4_MSS_level1_usgs_GS',
#  'ls4_MSS_level1_usgs_TP',
#  'ls4_TM_level1_usgs_GS',
#  'ls4_TM_level1_usgs_TP',
#  'ls5_MSS_level1_usgs_GS',
#  'ls5_MSS_level1_usgs_TP',
#  'ls5_TM_level1_usgs_GS',
#  'ls5_TM_level1_usgs_TP',
#  'ls7_level1_usgs_GS',
#  'ls7_level1_usgs_GT',
#  'ls7_level1_usgs_TP',
#  'ls8_level1_usgs_GT',
#  'ls8_level1_usgs_TP',
#  'ls9_level1_usgs_GT',
#  'ls9_level1_usgs_TP']
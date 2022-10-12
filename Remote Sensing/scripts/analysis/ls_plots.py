import argparse
import datacube
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os


# import derived_metrics as dm

dc = datacube.Datacube()

# landsat_products = [product for product in list(dc.list_products()['name'].values) if product.startswith('ls')]


### enable multiline help: referenced from:
### https://stackoverflow.com/questions/3853722/how-to-insert-newlines-on-argparse-help-text

class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)








### create cl arguments
parser = argparse.ArgumentParser(formatter_class=SmartFormatter)


parser.add_argument('--prod', nargs = 1, type = str, required=True,
    help="R|List of Products\n"
         "ls1_level1_usgs_GS\n" 
         "ls1_level1_usgs_TP\n"
         "ls2_level1_usgs_GS\n"
         "ls2_level1_usgs_TP\n"
         "ls3_level1_usgs_GS\n"
         "ls3_level1_usgs_TP\n"
         "ls4_MSS_level1_usgs_GS\n"
         "ls4_MSS_level1_usgs_TP\n"
         "ls4_TM_level1_usgs_GS\n"
         "ls4_TM_level1_usgs_TP\n"
         "ls5_MSS_level1_usgs_GS\n"
         "ls5_MSS_level1_usgs_TP\n"
         "ls5_TM_level1_usgs_GS\n"
         "ls5_TM_level1_usgs_TP\n"
         "ls7_level1_usgs_GS\n"
         "ls7_level1_usgs_GT\n"
         "ls7_level1_usgs_TP\n"
         "ls8_level1_usgs_GT\n"
         "ls8_level1_usgs_TP\n"
         "ls9_level1_usgs_GT\n"
         "ls9_level1_usgs_TP\n")


# parser.add_argument('--landsat', nargs = 1, type=str, required=True, 
#     help="'--landsat lsx' for x = 1,2,3,4,5,7,8,9")


parser.add_argument('--measure', nargs = 1, type = str, default = 'rgb', required = False,
    help= "--measure 'comma_sep_measurements:str'; please reference md document for a product's available measurements") #also account for derived_metrics; default rgb


parser.add_argument('--cmap', nargs = 1, type = str, default = ["viridis"], required = False,
    help = "...")




parser.add_argument('--time', nargs = 1, type = str, default = ["0000"], required = False, 
    help= "--time 'comma_sep_list_of_times:fmt(yyyy-mm-dd, yyyy-mm, or yyyy)'") 








parser.add_argument('--lat', nargs = 1, type=str, required=True, 
    help="--lat 'lat_min:float, lat_max:float'")
parser.add_argument('--lon', nargs = 1, type=str, required=True, 
    help="--lon 'lon_min:float, lon_max:float'")
parser.add_argument('--crs', nargs = 1, type = str, required = True)
parser.add_argument('--res', nargs = 1, type = str, required = True)




# referenced from https://gis.stackexchange.com/questions/404697/finding-all-dates-of-particular-dataset-in-open-data-cube





def indvidual_band(product, measure_cmap, time, lon, lat, crs, res):
    indv_measure = [mtuple for mtuple in measure_cmap]
    for mtuple in indv_measure:
        band, cmap = mtuple
        ds = dc.load(product= product, measurements=[band], 
                time = time, longitude=lon, latitude=lat, 
                output_crs = crs, resolution = res)
        band_img = ds[band].isel(time=0).values
        #.replace("(", "").replace(")", "")
        dst = f"{dst_base}/{product_mission}/{product}_{band}_{time.year}_{time.month}_{time.day}_lat{str(lat)}_lon{str(lon)}.png"
        plt.imshow(band_img, cmap = cmap)
        plt.title(f"time: {time}, band: {band}, crs: {crs}")
        plt.xlabel("x (meters)")
        plt.ylabel("y (meters)")
        plt.savefig(dst)
    





def rgb_plots(product, time, lon, lat, crs, res, dst):
    ds = dc.load(product= product, measurements=['red', 'green', 'blue'], 
             time = time, longitude=lon, latitude=lat, 
             output_crs = crs, resolution = res)
    ds[['red', 'green', 'blue']].isel(time=0).to_array().plot.imshow(robust=True, figsize=(20,10))
    plt.title(f"time: {time}, band: rgb, crs: {crs}")
    plt.xlabel("x (meters)")
    plt.ylabel("y (meters)")    
    plt.savefig(dst)



def product_dates(prod : str):
    found_dates = []
    for [time] in dc.index.datasets.search_returning(
                    ['time'], 
                    product=prod):
        found_time_offset = time.lower
        found_time = (abs(found_time_offset.utcoffset()) + found_time_offset).replace(tzinfo = None)
        found_dates.append(found_time)
    return found_dates




def naive_date_check(test_date : str, date_list):
    dt_list = test_date.split('-')
    if len(dt_list) == 3:
        t0 = datetime.datetime(int(dt_list[0]), int(dt_list[1]), int(dt_list[2]))
        t_dif = [abs(t.replace(tzinfo=None) - t0) for t in date_list]
        nearest_index = t_dif.index(min(t_dif))
        returned_date = date_list[nearest_index]
        summary_rd = datetime.datetime(returned_date.year, returned_date.month, returned_date.day)
        if summary_rd  != t0:
            print('no exact match found: providing closest available date')
        return [returned_date]
    elif len(dt_list) == 2:
        test_year, test_month = int(dt_list[0]), int(dt_list[1])
        matched_dates = [t  for t in date_list if (t.year==test_year and t.month == test_month)]
        if len(matched_dates) == 0:
            print("no matches: providing latest available date")
            return [max(date_list)]
        else:
            return matched_dates
    else:
        test_year = int(dt_list[0])
        matched_dates = [t  for t in date_list if t.year==test_year]
        if len(matched_dates) == 0:
            if test_date == '0000':
                print('no date is provided: providing latest available date')
            else:
                print("no matches: providing latest available date")
            return [max(date_list)]
        else:
            return matched_dates







args = parser.parse_args()

### gather input data for dc.load from command line arguments
prod = args.prod[0]
product_mission = prod.split('_')[0]








measure = args.measure[0].split(", ")

measure_no_rgb = measure.copy()
if 'rgb' in measure_no_rgb:
    measure_no_rgb.remove('rgb')

# if type(args.cmap) == str:
#     cmap = args.cmap.split(", ")
# else:
#     cmap = args.cmap
cmap = args.cmap[0].split(", ")

# print(measure)
# print(args.cmap)
# print(cmap)

# if not enough cmap arguments are provided to match number of measure arguments,
# append "viridis" until number of arguments match

if len(measure_no_rgb) != len(cmap):
    while len(measure_no_rgb) != len(cmap):
        cmap.append('viridis')
    measure_cmap = list(zip(measure_no_rgb , cmap))
else:
    measure_cmap = list(zip(measure_no_rgb , cmap))



#print(measure_cmap)

time = args.time[0].split(",")[0]









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







dst_base = "/home/output/ls_plots_out"

product_list_2 = ['ls4_TM_level1_usgs_GS',
                  'ls4_TM_level1_usgs_TP',
                  'ls5_TM_level1_usgs_GS',
                  'ls5_TM_level1_usgs_TP',
                  'ls7_level1_usgs_GS',
                  'ls7_level1_usgs_GT',
                  'ls7_level1_usgs_TP',
                  'ls8_level1_usgs_GT',
                  'ls8_level1_usgs_TP',
                  'ls9_level1_usgs_GT',
                  'ls9_level1_usgs_TP']



def main():
    test_date = time
    time_list = naive_date_check(test_date, product_dates(prod))
    measure_list = list(dc.list_measurements().loc[prod]['name'].values)
    if "rgb" in measure and prod in product_list_2:
        for t in time_list:
            #os.mkdir(f"{dst_base}/{product_mission}/")
            dst = f"{dst_base}/{product_mission}/{prod}_{'rgb'}_{t.year}_{t.month}_{t.day}_lat{str(lat)}_lon{str(lon)}.png"
            rgb_plots(prod, t, lon, lat, crs, res, dst)

    if set(measure_no_rgb).issubset(set(measure_list)):
        for t in time_list:
            indvidual_band(prod, measure_cmap, t, lon, lat, crs, res)
    else:
        print("invalid parameters provided")




if __name__ == "__main__":
    main()

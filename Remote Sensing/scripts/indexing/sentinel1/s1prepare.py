import multiprocessing
import os
import zipfile
import osgeo.gdal as osg



#unzip files from zippath
def unzip(i, platform, product, ext_dates, path, region, ziplist, tcrs):
    date = str(ext_dates[i])
    zipitem_path = f"{path}/src_files/{platform}/{product}/{ziplist[i]}"
    test_dst = f"{path}/extracted/s1data/{product}/{region}"
    with zipfile.ZipFile(zipitem_path) as archive:
        root = archive.namelist()[0]
        print("Extracting zip files...")
        archive.extractall(test_dst)
        os.rename(f"{test_dst}/{root.strip('/')}",
                  f"{test_dst}/{date}")
        print("Done!\n")



#transform images to crs indicated by tcrs
def transform(i, platform, product, ext_dates, path, region, ziplist, tcrs):
    date = str(ext_dates[i])
    im_path = f"{path}/extracted/s1data/{product}/{region}/{date}/measurement"
    im_dir = os.listdir(im_path)

    for img in im_dir:
        imglst = img.split('-')
        src = img
        pol = imglst[3]
        dst = f"{pol}crs.tiff"
        print(f"Transforming {src} into {dst}...")
        osg.Warp(f"{im_path}/{dst}", f"{im_path}/{src}", dstSRS=tcrs, resampleAlg='bilinear')
    print("Done!\n")


#generate metadata and index into datacube
def index(i, platform, product, ext_dates, path, region, ziplist, tcrs):
    date = str(ext_dates[i])
    os.system(f"python scripts/indexing/sentinel1/prep_s1a.py {path}/extracted/s1data/{product}/{region}/{date}")
    os.system(f"datacube dataset add {path}/extracted/s1data/{product}/{region}/{date}/agdc-metadata.yaml")

# python prep_s1a.py C:/Users/lende/dockerenv/data/extracted/s1data/GRD/Richardson/20211031

if __name__ == "__main__":
    global path, platform, product, region, tcrs, zippath, ziplist, ext_dates
    ### input parameters
    #path = "C:/Users/lende/dockerenv/data"
    path = "/home/data"
    platform = 'sentinel1'
    product = 'GRD'
    region = 'Richardson'
    tcrs = 'EPSG:32614'
    ###


    zippath = f"{path}/src_files/{platform}/{product}"
    ziplist = os.listdir(zippath)
    ext_dates = []
    for string in ziplist:
        output = ''.join(list(string.split('_')[4])[:8])
        ext_dates.append(int(output))


    os.mkdir(f'{path}/extracted/s1data')
    os.mkdir(f'{path}/extracted/s1data/{product}')
    os.mkdir(f'{path}/extracted/s1data/{product}/{region}')

    n_cpu = (multiprocessing.cpu_count()) - 1
    n_dates = len(ext_dates)
    index_list = []
    for i in range(n_dates):
        tp = (i, platform, product, ext_dates, path, region, ziplist, tcrs)
        index_list.append(tp)
    

    p = multiprocessing.Pool(n_cpu)
    result0 = p.starmap(unzip, index_list)
    result1 = p.starmap(transform, index_list)
    result2 = p.starmap(index, index_list)
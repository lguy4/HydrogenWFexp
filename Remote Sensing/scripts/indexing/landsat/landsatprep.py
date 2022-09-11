import os
import tarfile
import multiprocessing


#root path of zip files
src_root = "/home/data"

#root path of target directory
dst_root =  "/home/data/extracted"


mission = 'landsat'


src_base = f"{src_root}/src_files/{mission}"
dst_base = f"{dst_root}/{mission}"

src_subdir = [x[0].replace('\\', '/') for x in os.walk(src_base)]
dst_subdir = [x[0].replace(src_base, '').replace('\\', '/') for x in os.walk(src_base)][1:]

def create_subdirs():
    os.mkdir(f"{dst_base}")
    for path in dst_subdir:
        os.mkdir(f"{dst_base}{path}")


def extract_srcpaths():
    global srcpath_list
    srcpath_list = []
    for path in src_subdir:
        if path.endswith('l1'):
            srcpath_list.append(path)


def extract_dstpaths():
    global dstpath_list
    dstpath_list = []
    for path in dst_subdir:
        if path.endswith('l1'):
            dstpath_list.append(f"{dst_base}{path}")


def date_dir():
    global dst_date_path_list, src_date_path_list
    dst_date_path_list = []
    src_date_path_list = []
    for i in range(len(srcpath_list)):
        for item in os.listdir(srcpath_list[i]):
            date = ''.join(list(item.split('_')[3])[:8]) 
            date_path = f"{dstpath_list[i]}/{date}"
            os.mkdir(date_path)
            dst_date_path_list.append(date_path)
            src_date_path_list.append(f"{srcpath_list[i]}/{item}")
        
def tar_extract(src_date_path, dst_date_path):
    print(f"Extracting {src_date_path}...")
    with tarfile.TarFile(src_date_path) as archive:
      archive.extractall(dst_date_path)
    print("Done!")
    print("Generating meta file...")
    os.system(f"python scripts/indexing/landsat/ls_usgs_prepare.py --output {dst_date_path}/meta.yaml {dst_date_path}")
    print("Indexing...")
    os.system(f"datacube dataset add {dst_date_path}/meta.yaml")
    print("Done indexing!\n")   
    
            
                
        


def main():
    create_subdirs()
    extract_srcpaths()
    extract_dstpaths()
    date_dir()

if __name__ == "__main__":
    main()
    extract_input = list(zip(src_date_path_list, dst_date_path_list))
    n_cpu = (multiprocessing.cpu_count()) - 1
    p = multiprocessing.Pool(n_cpu)
    p.starmap(tar_extract, extract_input)

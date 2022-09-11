from __future__ import absolute_import

import uuid
import logging
import yaml
import re
import click
from osgeo import gdal, osr
import os
from pathlib import Path

MTL_PAIRS_RE = re.compile(r'(\w+)\s=\s(.*)')

WGS84_CODE = 12
PS_CODE = 6

images1 = [('BAND_1', 'coastal_aerosol'),
           ('BAND_2', 'blue'),
           ('BAND_3', 'green'),
           ('BAND_4', 'red'),
           ('BAND_5', 'nir'),
           ('BAND_6', 'swir1'),
           ('BAND_7', 'swir2'),
           ('BAND_8', 'panchromatic'),
           ('BAND_9', 'cirrus'),
           ('BAND_10', 'lwir1'),
           ('BAND_11', 'lwir2'),
           ('QUALITY_L1_PIXEL', 'quality_p'),
           ('QUALITY_L1_RADIOMETRIC_SATURATION', 'quality_r'),
           ('ANGLE_SENSOR_AZIMUTH_BAND_4', 'vaa'),
           ('ANGLE_SENSOR_AZIMUTH_BAND_4', 'vza'),
           ('ANGLE_SOLAR_AZIMUTH_BAND_4', 'saa'),
           ('ANGLE_SOLAR_AZIMUTH_BAND_4', 'sza')]


images2 = [('BAND_1', 'blue'),
           ('BAND_2', 'green'),
           ('BAND_3', 'red'),
           ('BAND_4', 'nir'),
           ('BAND_5', 'swir1'),
           ('BAND_6_VCID_1', 'thermal1'),
           ('BAND_6_VCID_2', 'thermal2'),
           ('BAND_7', 'swir2'),
           ('BAND_8', 'panchromatic'),
           ('QUALITY_L1_PIXEL', 'quality_p'),
           ('QUALITY_L1_RADIOMETRIC_SATURATION', 'quality_r'),
           ('ANGLE_SENSOR_AZIMUTH_BAND_4', 'vaa'),
           ('ANGLE_SENSOR_AZIMUTH_BAND_4', 'vza'),
           ('ANGLE_SOLAR_AZIMUTH_BAND_4', 'saa'),
           ('ANGLE_SOLAR_AZIMUTH_BAND_4', 'sza')]

images3 = [('BAND_1', 'green'),
           ('BAND_2', 'red'),
           ('BAND_3', 'nir1'),
           ('BAND_4', 'nir2'),
           ('QUALITY_L1_PIXEL', 'quality_p'),
           ('QUALITY_L1_RADIOMETRIC_SATURATION', 'quality_r')]

images4 = [('BAND_4', 'green'),
           ('BAND_5', 'red'),
           ('BAND_6', 'nir1'),
           ('BAND_7', 'nir2'),
           ('QUALITY_L1_PIXEL', 'quality_p'),
           ('QUALITY_L1_RADIOMETRIC_SATURATION', 'quality_r')]

images5 = [('BAND_1', 'blue'),
           ('BAND_2', 'green'),
           ('BAND_3', 'red'),
           ('BAND_4', 'nir'),
           ('BAND_5', 'swir1'),
           ('BAND_6', 'thermal'),
           ('BAND_7', 'swir2'),
           ('QUALITY_L1_PIXEL', 'quality_p'),
           ('QUALITY_L1_RADIOMETRIC_SATURATION', 'quality_r'),
           ('ANGLE_SENSOR_AZIMUTH_BAND_4', 'vaa'),
           ('ANGLE_SENSOR_AZIMUTH_BAND_4', 'vza'),
           ('ANGLE_SOLAR_AZIMUTH_BAND_4', 'saa'),
           ('ANGLE_SOLAR_AZIMUTH_BAND_4', 'sza')]

try:
    from urllib.request import urlopen
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
    from urllib3 import urlopen




def _parse_value(s):
    s = s.strip('"')
    for parser in [int, float]:
        try:
            return parser(s)
        except ValueError:
            pass
    return s


def _parse_group(lines):
    tree = {}

    for line in lines:

        match = MTL_PAIRS_RE.findall(line.decode('utf-8'))
        if match:
            key, value = match[0]
            if key == 'GROUP':
                tree[value] = _parse_group(lines)
            elif key == 'END_GROUP':
                break
            else:
                tree[key] = _parse_value(value)
    return tree


def get_geo_ref_points(info_pa):
    return {
        'ul': {'x': info_pa['CORNER_UL_PROJECTION_X_PRODUCT'], 'y': info_pa['CORNER_UL_PROJECTION_Y_PRODUCT']},
        'ur': {'x': info_pa['CORNER_UR_PROJECTION_X_PRODUCT'], 'y': info_pa['CORNER_UR_PROJECTION_Y_PRODUCT']},
        'll': {'x': info_pa['CORNER_LL_PROJECTION_X_PRODUCT'], 'y': info_pa['CORNER_LL_PROJECTION_Y_PRODUCT']},
        'lr': {'x': info_pa['CORNER_LR_PROJECTION_X_PRODUCT'], 'y': info_pa['CORNER_LR_PROJECTION_Y_PRODUCT']},
    }


def get_coords(geo_ref_points, spatial_ref):
    t = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

    def transform(p):
        lat, lon, z = t.TransformPoint(p['x'], p['y'])
        return {'lon': lon, 'lat': lat}

    return {key: transform(p) for key, p in geo_ref_points.items()}


def satellite_ref(sat, file_name, sid):
    """
    To load the band_names for referencing either LANDSAT8 or LANDSAT7 or LANDSAT5 bands
    Landsat7ETM  and Landsat5TM  have same band names
    """
    name = (Path(file_name)).stem
    name_len = name.split('_')
    if sat == 'LANDSAT_8' or sat == 'LANDSAT_9':
        sat_img = images1
    elif (sat == 'LANDSAT_4' or sat == 'LANDSAT_5') and sid == 'MSS':
        sat_img = images3
    elif (sat == 'LANDSAT_4' or sat == 'LANDSAT_5') and sid == 'TM':
        sat_img = images5
    elif sat == 'LANDSAT_1' or sat == 'LANDSAT_2' or sat == 'LANDSAT_3':
        sat_img = images4
    elif len(name_len) > 7:
        sat_img = images2
    return sat_img


def get_mtl(path):
    """
    Path is pointing to the folder , where the USGS Landsat scene list in MTL format is downloaded
    from Earth Explorer or GloVis
    """
    newfile = "Empty File"
    metafile = "Name_of_File"
    for file in os.listdir(path):
        if file.endswith("MTL.txt"):
            metafile = file
            newfile = open(os.path.join(path, metafile), 'rb')
    return _parse_group(newfile)['LANDSAT_METADATA_FILE'], metafile


def handle_proj_params(proj_params, projection):
    map_proj = proj_params.get('MAP_PROJECTION')
    spatial_ref = osr.SpatialReference()
    if map_proj == 'UTM':
        cs_code = 32600 + proj_params['UTM_ZONE']
        spatial_ref.ImportFromEPSG(cs_code)
        projection['spatial_reference'] = 'EPSG:%s' % cs_code
    elif map_proj == 'PS':
        datum = proj_params['DATUM']
        if datum != 'WGS84':
            raise RuntimeError('unsupported datum: "%s"' % (datum))
        zone = 0  # ignored in the PS case
        p_long = gdal.DecToPackedDMS(float(proj_params['VERTICAL_LON_FROM_POLE']))
        ts_lat = gdal.DecToPackedDMS(float(proj_params['TRUE_SCALE_LAT']))
        fe = float(proj_params['FALSE_EASTING'])
        fn = float(proj_params['FALSE_NORTHING'])
        args = 0, 0, 0, 0, p_long, ts_lat, fe, fn, 0, 0, 0, 0, 0, 0, 0
        spatial_ref.ImportFromUSGS(PS_CODE, zone, args, WGS84_CODE)
        projection['datum'] = datum
    else:
        raise RuntimeError('unknown map projection: "%s"' % (map_proj))
    return spatial_ref


def prepare_dataset(path):
    info, fileinfo = get_mtl(path)
    # Copying [PRODUCT_METADATA] group into 'info_pm'
    info_pm = info['PRODUCT_CONTENTS']
    level = info_pm['PROCESSING_LEVEL']
    product_type = info_pm['PROCESSING_LEVEL']
    
    info_ia = info['IMAGE_ATTRIBUTES']
    sensing_time = info_ia['DATE_ACQUIRED'] + ' ' + info_ia['SCENE_CENTER_TIME']
    
    info_pa = info['PROJECTION_ATTRIBUTES']
    geo_ref_points = get_geo_ref_points(info_pa)
    projection = {
        'geo_ref_points': geo_ref_points
    }
    spatial_ref = handle_proj_params(info['LEVEL1_PROJECTION_PARAMETERS'], projection)

    satellite = info_ia['SPACECRAFT_ID']
    sensor_id = info_ia['SENSOR_ID']

    images = satellite_ref(satellite, fileinfo, sensor_id)
    return {
        'id': str(uuid.uuid5(uuid.NAMESPACE_URL, path)),
        'processing_level': level,
        'product_type': product_type,
        # 'creation_dt': ct_time,
        'label': info['LEVEL1_PROCESSING_RECORD']['LANDSAT_SCENE_ID'],
        'platform': {'code': satellite},
        'instrument': {'name': info_ia['SENSOR_ID']},
        # 'acquisition': {'groundstation': {'code': station}},
        'extent': {
            'from_dt': sensing_time,
            'to_dt': sensing_time,
            'center_dt': sensing_time,
            'coord': get_coords(geo_ref_points, spatial_ref),
        },
        'format': {'name': info_pm['OUTPUT_FORMAT']},
        'grid_spatial': {
            'projection': projection
        },
        'image': {
            'bands': {
                image[1]: {
                    'path': info_pm['FILE_NAME_' + image[0]],
                    'layer': 1,
                } for image in images
            }
        },
        'LANDSAT_METADATA_FILE': info,
        'lineage': {'source_datasets': {}},
    }


def absolutify_paths(doc, path):
    for band in doc['image']['bands'].values():
        band['path'] = os.path.join(path, band['path'])
    return doc

#C:/Users/lende/mints-ODC-main/ls1data/Richardson/19720725
#C:/Users/lende/python_drafts/products/landsat_c2/metadata/ls1c2l1meta.yaml
#python ls_usgs_prepare.py --output C:/Users/lende/python_drafts/products/landsat_c2/metadata/ls9c2l1meta.yaml C:/Users/lende/mints-ODC-main/ls9data/Richardson/20220629

@click.command(help="""\b
                    Prepare USGS Landsat Collection 1 data for ingestion into the Data Cube.
                    This prepare script supports only for MTL.txt metadata file
                    To Set the Path for referring the datasets -
                    Download the  Landsat scene data from Earth Explorer or GloVis into
                    'some_space_available_folder' and unpack the file.
                    For example: yourscript.py --output [Yaml- which writes datasets into this file for indexing]
                    [Path for dataset as : /home/some_space_available_folder/]""")
@click.option('--output', required=False, help="Write datasets into this file",
              type=click.Path(exists=False, writable=True, dir_okay=False))
@click.argument('datasets',
                nargs=-1)
def main(output, datasets):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    if output:
        docs = (absolutify_paths(prepare_dataset(path), path) for path in datasets)
        with open(output, 'w') as stream:
            yaml.dump_all(docs, stream)
    else:
        raise RuntimeError('must specify --output')


if __name__ == "__main__":
    main()



#datacube product add ls1c2l1.yaml

#datacube product add ls2c2l1.yaml

#datacube product add ls3c2l1.yaml

#datacube product add ls4MSSc2l1.yaml

#datacube product add ls4TMc2l1.yaml

#datacube product add ls5MSSc2l1.yaml

#datacube product add ls5TMc2l1.yaml

#datacube product add ls7c2l1.yaml

#datacube product add ls8c2l1.yaml

#datacube product add ls9c2l1.yaml



################

#datacube dataset add ls1c2l1meta.yaml

#datacube dataset add ls2c2l1meta.yaml

#datacube dataset add ls3c2l1meta.yaml

#datacube dataset add ls4MSSc2l1meta.yaml

#datacube dataset add ls4TMc2l1meta.yaml

#datacube dataset add ls5MSSc2l1meta.yaml

#datacube dataset add ls5TMc2l1meta.yaml

#datacube dataset add ls7c2l1meta.yaml

#datacube dataset add ls8c2l1meta.yaml

#datacube dataset add ls9c2l1meta.yaml

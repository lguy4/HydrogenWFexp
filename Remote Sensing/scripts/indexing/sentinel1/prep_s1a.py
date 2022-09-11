import rasterio.warp
from osgeo import osr
import sys
import click
import yaml
from pathlib import Path



# Construct metadata dict
import uuid
from xml.etree import ElementTree  # should use cElementTree..
from dateutil import parser
import os

bands = ['vh', 'vv']


def get_geometry(path):
    with rasterio.open(path) as img:
        left, bottom, right, top = img.bounds
        crs = str(str(getattr(img, 'crs_wkt', None) or img.crs.wkt))
        corners = {
            'ul': {
                'x': left,
                'y': top
            },
            'ur': {
                'x': right,
                'y': top
            },
            'll': {
                'x': left,
                'y': bottom
            },
            'lr': {
                'x': right,
                'y': bottom
            }
        }
        projection = {'spatial_reference': crs, 'geo_ref_points': corners}

        spatial_ref = osr.SpatialReference(crs)
        t = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

        def transform(p):
            lat, lon, z = t.TransformPoint(p['x'], p['y'])
            return {'lon': lon, 'lat': lat}

        extent = {key: transform(p) for key, p in corners.items()}

        return projection, extent



def band_name(path):
    name = path.stem
    # position = name.find('_')
    if 'vh' in str(path):
        layername = 'vh'
    if 'vv' in str(path):
        layername = 'vv'
    return layername


def prep_dataset(path):
    # generate xml file from safe file
    with open(path/'manifest.safe', 'r') as file_in, open(path/'manifest.txt', 'w') as file_out:
        data = file_in.read()
        file_out.write(data)
    with open(path/"manifest.txt") as fin, open(path/'manifest.xml', 'w') as fout:
        for line in fin:
            fout.write(line.replace('safe:', ''))
            
    
    # Read in the XML header
    xml_path = path/'manifest.xml'
    xml = ElementTree.parse(str(xml_path)).getroot(
    ).find("metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap[@mimeType='text/xml']/xmlData/acquisitionPeriod")
    
    pdir = os.listdir(path)
    for name in pdir:
        if name.endswith(".pdf"):
            doc = name
    n = doc.find('.SAFE')
    
    scene_name = doc[:n]
    platform = 'SENTINEL_1'
    t0 = parser.parse(xml.find('startTime').text)
    t1 = parser.parse(xml.find('stopTime').text)

    # TODO: which time goes where in what format?
    # could also read processing graph, or
    # could read production/productscenerasterstart(stop)time

    # get bands
    # TODO: verify band info from xml
    images = {band_name(im_path): {'path': str(im_path)} 
        for im_path in  path.glob('measurement/*.tiff')}

    # trusting bands coaligned, use one to generate spatial bounds for all

    projection, extent = get_geometry(images['vv']['path'])

    # format metadata (i.e. construct hashtable tree for syntax of file interface)

    return {
        'id': str(uuid.uuid4()),
        'processing_level': "level_1",
        'product_type': "GRD",
        'creation_dt': str(t0),
        'platform': {
            'code': 'SENTINEL_1'
        },
        'instrument': {
            'name': 'SAR'
        },
        'extent': {
            'coord': extent,
            'from_dt': str(t0),
            'to_dt': str(t1),
            'center_dt': str(t0 + (t1 - t0) / 2)
        },
        'format': {
            'name': 'GeoTiff'
        },  
        'grid_spatial': {
            'projection': projection
        },
        'image': {
            'bands': images
        },
        'lineage': {
            'source_datasets': {},
            'ga_label': scene_name
        }  # TODO!
        # C band, etc...
    }


@click.command(
    help="Prepare S1A/B data processed in GeoTiff format dataset for ingestion into the Data Cube.")
@click.argument('datasets', type=click.Path(exists=True, readable=True, writable=True), nargs=-1)


def main(datasets):
    for dataset in datasets:
        path = Path(dataset)
        #assert path/'measurement'.glob('*.tiff'), "Expect a directory with a tiff header file as input"
        print("Starting for dataset " + dataset)
        metadata = prep_dataset(path)

        yaml_path = str(path.joinpath('agdc-metadata.yaml'))

        with open(yaml_path, 'w') as stream:
            yaml.dump(metadata, stream)
    print("Done! Adding to Datacube...\n")


if __name__ == "__main__":
    main()
 

# unzip .zip files

# gdalwarp -r bilinear -t_srs EPSG:32614 s1a-iw-grd-vh-20211031t002801-20211031t002826-040356-04c872-002.tiff vhcrs.tiff
# gdalwarp -r bilinear -t_srs EPSG:32614 s1a-iw-grd-vv-20211031t002801-20211031t002826-040356-04c872-001.tiff vvcrs.tiff

# python prep_s1a.py C:/Users/lende/mints-ODC-main/s1data/Richardson/20170101  (outputs agdc-metadata.yaml)

# datacube dataset add ./agdc-metadata.yaml
from geojson import FeatureCollection, dump
import shapefile
import shutil
import os
from register_layer import register_layer

def write_file(type: str, method: str, date: int):
    storage_path = '/api/storage/'
    layer_hex = register_layer(type, method, date)
    os.makedirs(storage_path + 'shp/' + layer_hex, exist_ok=True)
    with shapefile.Writer(storage_path + 'shp/' + layer_hex) as w:
        # write polygons here...
        w.field('field1', 'C')

    prj = open(storage_path + "shp/" + layer_hex + ".prj", "w")
    epsg  = 'GEOGCS["WGS 84",'
    epsg += 'DATUM["WGS_1984",'
    epsg += 'SPHEROID["WGS 84",6378137,298.257223563]]'
    epsg += ',PRIMEM["Greenwich",0],'
    epsg += 'UNIT["degree",0.0174532925199433]]'
    prj.write(epsg)
    prj.close()

    shutil.make_archive(storage_path + 'shp/' + layer_hex, 'zip', storage_path + 'shp/' + layer_hex)
    shutil.rmtree(storage_path + 'shp/' + layer_hex, ignore_errors=True)

    features = []
    # write polygons here...
    feature_collection = FeatureCollection(features)
    os.makedirs(storage_path + 'json/' + layer_hex, exist_ok=True)
    with open(storage_path + 'json/' + layer_hex + '.geojson', 'w') as f:
        dump(feature_collection, f)

def write_files(date: int):
    types = ["ignition", "spread", "total"]
    methods = ["JAC", "AHP", "MLC"]
    for t in types:
        for m in methods:
            write_file(t, m, date)
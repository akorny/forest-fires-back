import csv
import os
import shutil
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime

from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
import fiona
from fiona.crs import from_epsg

import geopandas as gpd

from config import Config as cfg
from coordinate_translator import from_lks92_to_lat_long
from register_layer import register_layer
from weather import Weather


@dataclass
class Path:
    path: str
    coefficient_JAC: float
    coefficient_AHP: float
    coefficient_MLC: float

@dataclass
class PathsCollection:
    const_paths: list

   
def count_danger(_method: str, _risk: str, _coeff: float) -> str:
    """This function counts danger level using previously declared interval"""

    _dic_percentage = {
        'breakout': 0.528,
        'spread': 0.472,
        'total': 1
    }
    
    _im = float(_dic_percentage[_risk])
    
    if _method == 'JAC':
        if   -50         < _coeff <= 0.334 * _im: return 'LOW'
        elif 0.334 * _im < _coeff <= 0.431 * _im: return 'MID'
        elif 0.431 * _im < _coeff <= 1:           return 'HIGH'

    if _method == 'AHP':
        if   -50         < _coeff <= 3.260 * _im : return 'LOW'
        elif 3.260 * _im < _coeff <= 4.772 * _im:  return 'MID'
        elif 4.772 * _im < _coeff <= 10:           return 'HIGH'

    if _method == 'MLC':
        if   0             < _coeff <= 93.592 * _im:  return 'LOW'
        elif 93.592 * _im  < _coeff <= 149.916 * _im: return 'MID'
        elif 149.916 * _im < _coeff <= 300:           return 'HIGH'

def count_risk_coeff(_risk: str, _model: str):
    """
    This function counts risk coefficient by using previously created 
    CSV files with constant weights and by nonconstant weights we take in 
    runntime
    """

    dataset_path = 'csv/'

    # Paths and weights for breakout risk
    breakout_paths = PathsCollection(
        # Constant
        [Path(f'{ dataset_path }historical_fires_risk.csv',
              cfg.JAC_RAISE5,
              cfg.AHP_RAISE5,
              cfg.MLC_RAISE5),
         Path(f'{ dataset_path }kudra_risk.csv', 
              cfg.JAC_RAISE7,
              cfg.AHP_RAISE7,
              cfg.MLC_RAISE7),
         Path(f'{ dataset_path }railway_risk.csv',
              cfg.JAC_RAISE6,
              cfg.AHP_RAISE6,
              cfg.MLC_RAISE6),
         Path(f'{ dataset_path }road_risk.csv',
              cfg.JAC_RAISE8,
              cfg.AHP_RAISE8,
              cfg.MLC_RAISE8),
         Path(f'{ dataset_path }forest_types_risk.csv',
              cfg.JAC_RAISE4,
              cfg.AHP_RAISE4,
              cfg.MLC_RAISE4),
         Path(f'{ dataset_path }temp_risk.csv',
              cfg.JAC_RAISE1,
              cfg.AHP_RAISE1,
              cfg.MLC_RAISE1),
         Path(f'{ dataset_path }nokr_risk.csv',
              cfg.JAC_RAISE2,
              cfg.AHP_RAISE2,
              cfg.MLC_RAISE2),
         Path(f'{ dataset_path }sunny_days_risk.csv',
              cfg.JAC_RAISE3,
              cfg.AHP_RAISE3,
              cfg.MLC_RAISE3),
        ])
    
    # Paths and weights for spread risk
    spread_paths = PathsCollection(
        # Constant
        [Path(f'{ dataset_path }forest_types_risk.csv',
              cfg.JAC_SPREAD14,
              cfg.AHP_SPREAD14,
              cfg.MLC_SPREAD14),
         Path(f'{ dataset_path }slope_risk.csv',
              cfg.JAC_SPREAD16,
              cfg.AHP_SPREAD16,
              cfg.MLC_SPREAD16),
         Path(f'{ dataset_path }aspect_risk.csv',
              cfg.JAC_SPREAD15,
              cfg.AHP_SPREAD15,
              cfg.MLC_SPREAD15),
         Path(f'{ dataset_path }road_risk.csv',
              cfg.JAC_SPREAD17,
              cfg.AHP_SPREAD17,
              cfg.MLC_SPREAD17),
         Path(f'{ dataset_path }udens_risk.csv',
              cfg.JAC_SPREAD18,
              cfg.AHP_SPREAD18,
              cfg.MLC_SPREAD18),
         Path(f'{ dataset_path }min_joslas_risk.csv',
              cfg.JAC_SPREAD21,
              cfg.AHP_SPREAD21,
              cfg.MLC_SPREAD21),
         Path(f'{ dataset_path }temp_risk.csv',
              cfg.JAC_SPREAD10,
              cfg.AHP_SPREAD10,
              cfg.MLC_SPREAD10),
         Path(f'{ dataset_path }nokr_risk.csv',
              cfg.JAC_SPREAD11,
              cfg.AHP_SPREAD11,
              cfg.MLC_SPREAD11),
         Path(f'{ dataset_path }sunny_days_risk.csv',
              cfg.JAC_SPREAD12,
              cfg.AHP_SPREAD12,
              cfg.MLC_SPREAD12),
         Path(f'{ dataset_path }stigas_risk.csv',
              cfg.JAC_SPREAD20,
              cfg.AHP_SPREAD20,
              cfg.MLC_SPREAD20),
        ])

    # Paths and weights for total risk
    total_paths = PathsCollection(
        breakout_paths.const_paths + spread_paths.const_paths
    )

    _dict_paths = {
        'breakout': breakout_paths,
        'spread': spread_paths,
        'total': total_paths
    }
    
    path_by_risk = _dict_paths[_risk]
    list_all_coefficients = []

    count = 0

    for info in path_by_risk.const_paths:
        _path = info.path

        if _model == 'JAC':
            _coefficient = info.coefficient_JAC
        elif _model == 'AHP':
            _coefficient = info.coefficient_AHP
        elif _model == 'MLC':
            _coefficient = info.coefficient_MLC
        else:
            raise TypeError(f"Unsuported method {_model}, try 'JAC', 'AHP' or 'MLC'")

        try: 
            with open(_path) as csv_risk:
                reader = csv.reader(csv_risk)
                next(reader)
                list_coefficients = []

                for row in reader:
                    list_coefficients.append(int(row[1]) * _coefficient)

                list_all_coefficients.append(list_coefficients)
                count += 1
        except IndexError as e:
            raise IndexError(f'Error occured in file {_path} in row {row[0]}')

    return [sum(i) for i in zip(*list_all_coefficients)]

def create_layer(_path: str, _risk: str, _method: str, _file_type: str):
    """This function creates current SHP layers to `_path` directory"""

    GEOMETRY = 'MultiPolygon'
    PROPERTIES = {'ID': 'str:6', 'DANGER': 'str:6'}

    if _file_type == 'shp':
        NEW_DRIVER = 'ESRI Shapefile'
    elif _file_type == 'json':
        NEW_DRIVER = 'GeoJSON'
    else:
        raise TypeError(f"Unsupported file type {_file_type}")
        
    NEW_CRS = from_epsg(4326) # 3059
    NEW_SCHEMA = {'properties': PROPERTIES, 'geometry': GEOMETRY}
    
    FEATURE = {"geometry": {"type": GEOMETRY,
                            "coordinates": None},
               "properties": None}
            
    # Counting RISK coefficients to group polygons
    coefficients = count_risk_coeff(_risk, _method)

    with fiona.open(
        _path,
        'w',
        driver=NEW_DRIVER,
        crs=NEW_CRS,
        schema=NEW_SCHEMA
    ) as new_shp:
            
        with fiona.open('Squares/squares.shp', 'r') as squares_shp:
            
            # If coefficients count does not equal to squares count that means
            # there are problems with records in CSV files
            if len(squares_shp) != len(coefficients):
                raise Exception("Problems with csv files!")
            
            _poly_by_danger = {
                    'LOW': [],
                    'MID': [],
                    'HIGH': []
                }
                 
            for square, coeff in zip(squares_shp, coefficients):
                _id  = square['properties']['ID']
                poly = square['geometry']['coordinates'][0]

                current_feature = deepcopy(FEATURE)
                current_properties = deepcopy(PROPERTIES)

                # Converting coords from LKS92 to WGS84
                poly = [from_lks92_to_lat_long(coord[0], coord[1]) for coord in poly]
                poly = [elem[::-1] for elem in poly]

                for i, coords in enumerate(poly):
                    poly[i] = (round(coords[0], 7), round(coords[1], 7))

                args = (_id, count_danger(_method, _risk, coeff))

                # Filling properties with previously declared arguments
                for _key, _arg in zip(current_properties, args):
                    current_properties[_key] = _arg

                # Preparing feature to write into file
                current_feature['geometry']['coordinates'] = [poly]
                current_feature['geometry']['type'] = GEOMETRY
                current_feature['properties'] = current_properties

                # Sorting features by danger
                danger_level = current_feature['properties']['DANGER']
                _poly_by_danger[danger_level].append(current_feature)
                
            _feature_id = 0
            for _danger_level in _poly_by_danger:
                to_unite = []
                list_poly = _poly_by_danger[_danger_level]

                if list_poly:

                    # Itereating by list of features and creating polygons to unite them
                    for _poly in list_poly:
                        to_unite.append(Polygon(_poly['geometry']['coordinates'][0]))
                    union = unary_union(to_unite)
                    
                    _mapping = mapping(union)
                    if _mapping["type"] == "Polygon":
                        _mapping["type"] = "MultiPolygon"
                        _mapping["coordinates"] = [_mapping["coordinates"]]
                        feature_to_write = {'geometry': _mapping,
                                            'properties': {
                                                'ID': str(_feature_id),
                                                'DANGER': _danger_level
                                                }
                                            }
                    elif _mapping["type"] == "MultiPolygon":
                        feature_to_write = {'geometry': _mapping,
                                            'properties': {
                                                'ID': str(_feature_id),
                                                'DANGER': _danger_level
                                                }
                                            }
                    else:
                        raise ValueError("Unsupported feature type")
                                 
                    _feature_id += 1
                    # Writing united multipolygon
                    new_shp.write(feature_to_write)

def create_shp_layers() -> None:
    """This function creates all SHP layers to `shp_path` directory"""

    weather_filename = {
        "temp": "temp_risk",
        "nokr": "nokr_risk",
        "veja_atr": "veja_atr_risk",
        "sunny_days": "sunny_days_risk"
    }

    weather = Weather.get_data()
    for key in weather.keys():
        lst = weather[key]

        with open("csv/{}.csv".format(weather_filename[key]), "w", newline='') as csv_writer:
            file = csv.writer(csv_writer)
            file.writerow(["ID", weather_filename[key].upper()])
            for i, row in enumerate(lst):
                file.writerow([i, row])

    
    RISKS = ['breakout', 'spread', 'total']
    RISKS_MAPPING = {
        "breakout": "ignition",
        "spread": "spread",
        "total": "total"
    }

    METHOD = ['JAC', 'AHP', 'MLC']
    
    storage_path = '../storage/'
    _date = datetime.now()
    
    for _risk in RISKS:
        for _method in METHOD:
            print("Creating layer. Method -> {}; Risk -> {}".format(_method, _risk))
            # Creating SHP file
            layer_hex  = register_layer(RISKS_MAPPING[_risk], _method, _date)
            layer_directory = f'{ storage_path }shp/{ layer_hex }'
            layer_path = f'{ layer_directory }/{ layer_hex }.shp'
            
            os.makedirs(layer_directory, exist_ok=True)
            create_layer(layer_path, _risk, _method, "shp")
            
            shutil.make_archive(layer_directory, 'zip', layer_directory)
            
            # Creating JSON
            json_layer_directory = f'{ storage_path }json'
            json_layer_path = f'{ json_layer_directory }/{ layer_hex }.json'
            
            shp_file = gpd.read_file(layer_path)
            shp_file.to_file(json_layer_path, driver='GeoJSON')

            # Removing SHP temp directory
            shutil.rmtree(layer_directory, ignore_errors=True)
            
            
                           
if __name__ == "__main__":
    create_shp_layers()

import requests
import json
import math
import csv
from copy import deepcopy
from coordinate_translator import from_lat_long_to_lks92
import datetime

class NoDataException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Weather:

    damaged_data_output= 999
    weather_url = "https://gispub.lvceli.lv/gispub/rest/services/GISPUB/SIC_CMSPoint/MapServer/1/query?where=&text=LV&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentsOnly=false&datumTransformation=&parameterValues=&rangeValues=&f=pjson"
    forest_points_path = "csv/forest_points.csv"
    hot_days_path = "csv/hot_days_stations_.csv"
    nokr_path = "csv/nokr_sum.csv"
    town_coords_path = "csv/town_coords.csv"
    points = [
        {'id': 'LV01', 'y': '57.19453487', 'x': '24.36230328'},
        {'id': 'LV02', 'y': '57.16828851', 'x': '24.96569038'},
        {'id': 'LV03', 'y': '56.84637604', 'x': '24.41017133'},
        {'id': 'LV04', 'y': '56.81234532', 'x': '24.2495496'},
        {'id': 'LV05', 'y': '56.2989199', 'x': '24.34372902'},
        {'id': 'LV06', 'y': '56.92952175', 'x': '23.61501575'},
        {'id': 'LV07', 'y': '57.38848467', 'x': '24.42913583'},
        {'id': 'LV08', 'y': '56.64010351', 'x': '23.77633017'},
        {'id': 'LV09', 'y': '57.2741013', 'x': '24.8949337'},
        {'id': 'LV10', 'y': '57.22118552', 'x': '25.23075163'},
        {'id': 'LV10', 'y': '57.22118552', 'x': '25.23075163'},
        {'id': 'LV11', 'y': '56.66075001', 'x': '24.89806133'},
        {'id': 'LV12', 'y': '56.38038208', 'x': '23.67671686'},
        {'id': 'LV13', 'y': '56.52133156', 'x': '24.17237341'},
        {'id': 'LV14', 'y': '56.8359801', 'x': '23.57609153'},
        {'id': 'LV15', 'y': '57.62169834', 'x': '24.38711617'},
        {'id': 'LV16', 'y': '57.50354801', 'x': '25.327102'},
        {'id': 'LV17', 'y': '57.65118801', 'x': '25.86377317'},
        {'id': 'LV18', 'y': '57.38805351', 'x': '25.97390617'},
        {'id': 'LV19', 'y': '57.01939417', 'x': '22.97691067'},
        {'id': 'LV20', 'y': '57.39440067', 'x': '21.84980867'},
        {'id': 'LV21', 'y': '56.66714601', 'x': '23.06080683'},
        {'id': 'LV22', 'y': '56.67100551', 'x': '22.28984083'},
        {'id': 'LV23', 'y': '56.64518751', 'x': '21.8845905'},
        {'id': 'LV24', 'y': '56.59306684', 'x': '25.54641267'},
        {'id': 'LV25', 'y': '56.52141984', 'x': '26.46058633'},
        {'id': 'LV26', 'y': '56.54010317', 'x': '27.29912433'},
        {'id': 'LV27', 'y': '56.39728046', 'x': '27.99057297'},
        {'id': 'LV28', 'y': '56.43649217', 'x': '26.07228267'},
        {'id': 'LV29', 'y': '55.92755217', 'x': '26.64375667'},
        {'id': 'LV30', 'y': '55.89763651', 'x': '27.2932865'},
        {'id': 'LV31', 'y': '56.95821194', 'x': '23.90075684'},
        {'id': 'LV32', 'y': '57.15223684', 'x': '22.69016967'},
        {'id': 'LV33', 'y': '57.46918734', 'x': '26.44297317'},
        {'id': 'LV34', 'y': '56.27674432', 'x': '27.07452318'},
        {'id': 'LV35', 'y': '56.89453751', 'x': '23.711839'},
        {'id': 'LV36', 'y': '56.58939567', 'x': '21.66298783'},
        {'id': 'LV37', 'y': '57.37810467', 'x': '25.05118867'},
        {'id': 'LV38', 'y': '57.06875994', 'x': '24.48996306'},
        {'id': 'LV39', 'y': '56.93271167', 'x': '23.48088817'},
        {'id': 'LV40', 'y': '56.959658', 'x': '24.37540837'},
        {'id': 'LV41', 'y': '57.09029584', 'x': '24.31334067'},
        {'id': 'LV42', 'y': '56.75106501', 'x': '23.893663'},
        {'id': 'LV43', 'y': '57.23644334', 'x': '22.20748467'},
        {'id': 'LV44', 'y': '57.33471067', 'x': '24.45546333'},
        {'id': 'LV45', 'y': '56.77865484', 'x': '23.3645565'},
        {'id': 'LV46', 'y': '56.59658134', 'x': '26.87487167'},
        {'id': 'LV47', 'y': '56.21446077', 'x': '21.13288879'},
        {'id': 'LV48', 'y': '56.80233518', 'x': '27.73095131'},
        {'id': 'LV49', 'y': '56.1570026', 'x': '26.33971617'},
        {'id': 'LV50', 'y': '57.30744911', 'x': '25.62436581'},
        {'id': 'LV51', 'y': '56.69331225', 'x': '24.24163092'},
        {'id': 'LV52', 'y': '56.84361032', 'x': '24.01911069'},
        {'id': 'LV53', 'y': '56.57480723', 'x': '21.29273918'},
        {'id': 'LV54', 'y': '56.64716867', 'x': '22.78889277'},
        {'id': 'LV57', 'y': '57.22224802', 'x': '25.58484355'},
        {'id': 'LV58', 'y': '56.88367954', 'x': '22.11005958'},
        {'id': 'LV59', 'y': '56.38642036', 'x': '24.25440466'},
        {'id': 'LV60', 'y': '57.11592133', 'x': '24.32339594'},
        {'id': 'LV61', 'y': '56.7533897', 'x': '25.11882382'},
        {'id': 'LV62', 'y': '56.82470691', 'x': '24.75838306'},
        {'id': 'LV63', 'y': '57.49602655', 'x': '24.43127042'},
        {'id': 'LV64', 'y': '57.86634051', 'x': '24.37241591'},
        {'id': 'LV65', 'y': '57.56978523', 'x': '26.9844444'},
        {'id': 'LV95', 'y': '56.79126443', 'x': '23.96470303'},
        {'id': 'LV98', 'y': '56.95906788', 'x': '23.95427765'}
    ]


    @staticmethod
    def get_nearest(x, y, points):
            nearest = None
            nearest_id = None
            index = None
            for counter, point in enumerate(points):
                point_x, point_y = from_lat_long_to_lks92(float(point["y"]), float(point["x"]))
                delta_x = abs(float(x) - float(point_x))
                delta_y = abs(float(y) - float(point_y))
                distance = math.sqrt(delta_x**2 + delta_y**2)
                if nearest and distance < nearest:
                    nearest, nearest_id, index = distance, point["id"], counter
                elif nearest == None:
                    nearest, nearest_id, index = distance, point["id"], counter

            return nearest_id, index


    @staticmethod
    def get_data():
        response = requests.get(Weather.weather_url)
        data = json.loads(response.text)
        weather = {}
        result_weather = []
        for attr in data["features"]:
            weather[attr["attributes"]["id"]] = {"id": attr["attributes"]["id"], 
                                    "temp": attr["attributes"]["at"],
                                    "is_raining": attr["attributes"]["rs"],
                                    "veja_atr": attr["attributes"]["ws"]
                                    }


        forest_points = []
        with open(Weather.forest_points_path, 'r') as file:
            csvreader = csv.reader(file)
            next(csvreader)
            for row in csvreader:
                forest_points.append([row[1], row[2]])


        nokr = {}
        with open(Weather.nokr_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for item in reader:
                if item[0] in nokr.keys():
                    nokr[item[0]].append([item[1], item[2]])
                else:
                    nokr[item[0]] = [[item[1], item[2]]]


        hot_days = {}
        with open(Weather.hot_days_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for item in reader:
                if item[1] in hot_days.keys():
                    hot_days[item[1]].append([item[2], item[3]])
                else:
                    hot_days[item[1]] = [[item[2], item[3]]]


        town_coords = {}
        with open(Weather.town_coords_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for item in reader:
                town_coords[item[0]] = [float(item[1]), float(item[2])]


        for point in forest_points:
            points = deepcopy(Weather.points)
            x, y = point[0], point[1]
            result_weather.append({"id": None, 
                                    "temp": None,
                                    "veja_atr": None,
                                    "nokr": 0,
                                    "hot_days": 0,
                                    "is_raining": None
                                    })
            while True:
                if len(points) == 0:
                    raise NoDataException("No data was found")
                nearest_id, index = Weather.get_nearest(x, y, points)
                
                
                if None in [result_weather[len(result_weather) - 1][a] for a in ("temp", "veja_atr", "is_raining")]:
                    for i in weather[nearest_id].keys():
                        if result_weather[len(result_weather) - 1][i] == None:
                            result_weather[len(result_weather) - 1][i] = weather[nearest_id][i] if weather[nearest_id][i] not in (Weather.damaged_data_output, "none") else None
                
                if None in [result_weather[len(result_weather) - 1][a] for a in ("temp", "veja_atr", "is_raining")]:
                    del points[index]
                    continue

                break

            month = datetime.datetime.today().month

            for i in hot_days[nearest_id]:
                if int(i[0]) in [month, month - 1, month - 2]:
                    result_weather[len(result_weather) - 1]["hot_days"] += int(i[1])
        
            nearest = None
            nearest_distance = None
            for town in town_coords.keys():
                distance = math.sqrt(abs(float(point[0]) - town_coords[town][0])**2 + abs(float(point[1]) - town_coords[town][1])**2)
                if not nearest:
                    nearest, nearest_distance = town, distance

                elif distance < nearest_distance:
                    nearest, nearest_distance = town, distance


            
            for i in nokr[nearest]:
                if int(i[0]) in [month, month - 1, month - 2]:
                    result_weather[len(result_weather) - 1]["nokr"] += int(i[1])

                
        for i in result_weather:
            if i["temp"] < 18.2:
                i["temp"] = 1
            elif i["temp"] < 18.6:
                i["temp"] = 2
            elif i["temp"] < 19:
                i["temp"] = 3
            elif i["temp"] < 19.4:
                i["temp"] = 4
            else:
                i["temp"] = 5


            if i["veja_atr"] < 3:
                i["veja_atr"] = 1
            elif i["veja_atr"] < 3.9:
                i["veja_atr"] = 2
            elif i["veja_atr"] < 4.3:
                i["veja_atr"] = 3
            elif i["veja_atr"] < 4.6:
                i["veja_atr"] = 4
            else:
                i["veja_atr"] = 5

            if i["nokr"] > 205:
                i["nokr"] = 1
            elif i["nokr"] > 195:
                i["nokr"] = 2
            elif i["nokr"] > 185:
                i["nokr"] = 3
            elif i["nokr"] > 175:
                i["nokr"] = 4
            else:
                i["nokr"] = 5

            if i["hot_days"] < 34:
                i["hot_days"] = 1
            elif i["hot_days"] < 41:
                i["hot_days"] = 2
            elif i["hot_days"] < 48:
                i["hot_days"] = 3
            elif i["hot_days"] < 55:
                i["hot_days"] = 4
            else:
                i["hot_days"] = 5
            
            i["is_raining"] = True if i["is_raining"] > 0 else False



        result_weather_dict = {"temp": [result_weather[i]["temp"] for i in range(len(result_weather))],
                                "veja_atr": [result_weather[i]["veja_atr"] for i in range(len(result_weather))],
                                "hot_days": [result_weather[i]["hot_days"] for i in range(len(result_weather))],
                                "is_raining": [result_weather[i]["is_raining"] for i in range(len(result_weather))],
                                "nokr": [result_weather[i]["nokr"] for i in range(len(result_weather))]
                                }

        return result_weather_dict

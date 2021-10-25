import falcon
from database.tables.layers import Layers
from pages.utils.returners import return_400, return_json
from datetime import datetime

class Period:
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        try:
            fr = datetime.fromtimestamp(int(req.params.get("from")))
            to = datetime.fromtimestamp(int(req.params.get("to")))
        except ValueError:
            return_400(resp)
            return
        
        queries = Layers.select().where((Layers.datetime <= to) & (Layers.datetime >= fr))
        return_json(resp, self.group_queries(queries, to, fr))
    
    def group_queries(self, queries: list, to: datetime, fr: datetime):
        result = {
            "to": to.isoformat(),
            "from": fr.isoformat(),
            "layersets": []
        }
        helper = []

        for q in queries:
            if not q.datetime in helper:
                helper.append(q.datetime)
                result["layersets"].append({
                    "date": q.datetime.isoformat(),
                    "layers": {
                        "ignition": [],
                        "spread": [],
                        "total": []
                    }
                })
            
            index = helper.index(q.datetime)
            result["layersets"][index]["layers"][q.type].append({
                "method": q.method,
                "geojson_url": "/api/storage/json/" + q.hex + ".json",
                "shp_url": "/api/storage/shp/" + q.hex + ".zip"
            })
        
        return result


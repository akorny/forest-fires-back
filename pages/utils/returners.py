import falcon as fc

def return_400(response: fc.Response):
    response.status = 400
    response.content_type = "application/json"
    response.media = {
        "code": 400,
        "message": "Bad Request"
    }
    response.set_header("Access-Control-Allow-Origin", "*")

def return_json(response: fc.Response, json_dict: dict):
    response.status = 200
    response.content_type = "application/json"
    json_dict["code"] = 200
    json_dict["message"] = "OK"
    response.media = json_dict
    response.set_header("Access-Control-Allow-Origin", "*")
from database.tables.layers import Layers
from datetime import datetime
from secrets import token_hex

def register_layer(type: str, method: str, date: datetime):
    """
    Registers layer into database.  
    - type (str) -> layer type. (ignition, spread or total)
    - method (str) -> weight calculation method. (jac, ahp or mlc)
    - date (datetime) -> date and time of layer generation start
    """
    while True:
        hx = token_hex(10)
        if len(Layers.select().where(Layers.hex == hx)) == 0:
            break

    l = Layers()
    l.type = type.lower()
    l.method = method.lower()
    l.datetime = date
    l.hex = hx
    l.save()

    return hx

if __name__ == '__main__':
    register_layer("ignition", "jac", datetime.now())
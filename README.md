# forest-fires-back

> This application was developed for [LATA atverto ģeotelpisko datu hakatons skoleniem 2021](https://www.lata.org.lv/skolas-2021). Developed by `tea.spill(keyboard)` command.

Repository contains backend part of our application. Written in `Python`.

Dependencies: 
- `falcon`
- `peewee`
- `pyshp`
- `fiona`
- `geojson`
- `shapely`
- `geopandas`
- `requests` if `Python` version is less than `3.9`

### Repository structure

- `/database/` - folder contains `Peewee` models and database connection;
- `/pages/` - folder contains `Falcon` page classes;
- `/csv/` - folder contains static data, that is used for layer creation;
- `/Squares/` - folder contains `.shp` file with all squares in Latvian forests;
- `application.py` - main `Falcon` `API` file;
- `config.py` - contains weights for layer creation;
- `coordinate_translator.py` - contains coordinates convertion functions from `LKS-92` to `WGS-84` and vice versa;
- `create_layers.py` - contains layer generation script;
- `register_layer.py` - contains function, that registrates layer into database;
- `weather.py` - contains class, that gather weather conditions from `Latvijas Valsts ceļi` meteostations.

## Setup description

### API

`Falcon` application is served by `gunicorn` and `nginx`. `nginx` is used as proxy server, that connects to `gunicorn` via `UNIX` socket.

### Layer creation

`CRON` calls `create_layers.py` script each 10 minutes. `create_layers.py` script gets weather information, using `Weather` class from `weather.py`. Then, `create_layers.py` generates all 9 layers both in `GeoJSON` and `SHP` file formats, and registrates them in `SQLite3` database.

### nginx

`nginx` serves three parts of our application:

- [Frontend](https://github.com/akorny/forest-fires-front);
- `Falcon` `API`;
- `storage` - layer files.
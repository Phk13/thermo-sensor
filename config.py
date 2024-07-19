
class Config(object):
    DATA = {
        "read_freq": 120,
        "temp_offset": -1.5,
        "hum_offset": 0,
        "pres_offset": 0,
    }

    DB = {
        "host": "",
        "port": 27017,
        "name": "thermo",
        "user": "thermo",
        "pass": "",
        "collection": "reading",
    }

    JSON_FILE = "data.json"

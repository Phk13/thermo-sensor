from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import bme280
from config import Config
from dbaccess import insert_read


def read_sensor():
    while True:
        try:
            temperature, pressure, humidity = bme280.readBME280All()
            break
        except TimeoutError:
            pass
    data = {
        "timestamp": datetime.now().replace(second=0, microsecond=0).isoformat(),
        "temperature": round(temperature + float(Config.DATA['temp_offset']), 2),
        "pressure": round(pressure + float(Config.DATA['pres_offset']), 2),
        "humidity": round(humidity + float(Config.DATA['hum_offset']), 2)
    }
    return data


def save_reading():
    insert_read(read_sensor())



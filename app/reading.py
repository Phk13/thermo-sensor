from flask_restful import Resource
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import app.bme280
from app import config
from app.dbaccess import insert_read


def read_sensor():
    while True:
        try:
            temperature, pressure, humidity = app.bme280.readBME280All()
            break
        except TimeoutError:
            pass
    data = {
        "timestamp": datetime.now().replace(second=0, microsecond=0).isoformat(),
        "temperature": temperature - float(config['DATA']['temp_offset']),
        "pressure": round(pressure - float(config['DATA']['pres_offset']), 2),
        "humidity": round(humidity - float(config['DATA']['hum_offset']), 2)
    }
    return data


def save_reading():
    insert_read(read_sensor())


class Reading(Resource):
    def get(self):
        return read_sensor()


scheduler = BackgroundScheduler()
scheduler.add_job(func=save_reading, trigger="interval", seconds=config['DATA']['read_freq'])
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

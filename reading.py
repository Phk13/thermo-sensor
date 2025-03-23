from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import bme280
from config import Config
from dbaccess import insert_read
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sensor reading validation constants
VALID_RANGES = {
    "temperature": (-40, 85),
    "pressure": (600, 1200),
    "humidity": (0, 100)
}

def validate_reading(reading: Dict[str, Any]) -> bool:
    """Validate sensor readings are within expected ranges."""
    for field, (min_val, max_val) in VALID_RANGES.items():
        value = reading.get(field)
        if value is None or not min_val <= value <= max_val:
            logger.error(f"Invalid {field} reading: {value} (expected {min_val} to {max_val})")
            return False
    return True

def read_sensor(max_retries: int = 3) -> Dict[str, Any]:
    """Read sensor data with retries and validation."""
    for attempt in range(max_retries):
        try:
            temperature, pressure, humidity = bme280.readBME280All()
            
            # Apply calibration offsets
            temperature = round(temperature + float(Config.DATA['temp_offset']), 2)
            pressure = round(pressure + float(Config.DATA['pres_offset']), 2)
            humidity = round(humidity + float(Config.DATA['hum_offset']), 2)
            
            data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "temperature": temperature,
                "pressure": pressure,
                "humidity": humidity
            }
            
            if validate_reading(data):
                return data
            logger.warning(f"Invalid reading on attempt {attempt + 1}/{max_retries}")
            
        except TimeoutError:
            logger.warning(f"Timeout error on attempt {attempt + 1}/{max_retries}")
        except (IOError, OSError) as e:
            logger.error(f"I2C error on attempt {attempt + 1}/{max_retries}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}/{max_retries}: {e}")
    
    # If we get here, we failed to get a valid reading
    raise RuntimeError("Failed to get valid sensor reading after max retries")

async def save_reading():
    """Asynchronous wrapper for saving sensor readings."""
    try:
        data = read_sensor()
        insert_read(data)
        logger.info(f"Successfully saved reading: temp={data['temperature']}°C, "
                   f"pressure={data['pressure']}hPa, humidity={data['humidity']}%")
    except Exception as e:
        logger.error(f"Failed to save reading: {e}")

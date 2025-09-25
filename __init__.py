"""
Sensor module for IoT waste bin monitoring system.
Provides various sensor simulations for waste bin monitoring.
"""

from .sensor_base import SensorBase
from .gps_sensor import GPSSensor
from .temperature_sensor import TemperatureSensor
from .recyclable_sensor import RecyclableSensor
from .fill_level_sensor import FillLevelSensor
from .odor_sensor import OdorSensor
from .humidity_sensor import HumiditySensor
from .air_quality_sensor import AirQualitySensor

__all__ = [
    'SensorBase',
    'GPSSensor',
    'TemperatureSensor',
    'RecyclableSensor',
    'FillLevelSensor',
    'OdorSensor',
    'HumiditySensor',
    'AirQualitySensor'
]

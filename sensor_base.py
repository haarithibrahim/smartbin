"""
Base sensor class for IoT waste bin monitoring system.
Provides common functionality for all sensor types.
"""

import uuid
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime


class SensorBase(ABC):
    """
    Abstract base class for all sensor implementations.
    
    Provides common functionality such as:
    - Unique ID generation
    - Timestamp generation
    - JSON formatting of sensor data
    - Abstract method for reading sensor data
    """
    
    def __init__(self, sensor_type, device_id=None):
        """
        Initialize the sensor with a unique ID and type.
        
        Args:
            sensor_type (str): Type of the sensor (e.g., 'gps', 'temperature')
            device_id (str, optional): Device ID to associate with this sensor.
                                      If None, a random UUID will be generated.
        """
        self.sensor_type = sensor_type
        self.sensor_id = str(uuid.uuid4())
        self.device_id = device_id if device_id else str(uuid.uuid4())
    
    def get_timestamp(self):
        """
        Generate current timestamp in ISO format.
        
        Returns:
            str: Current timestamp in ISO format
        """
        return datetime.utcnow().isoformat() + "Z"
    
    @abstractmethod
    def read(self):
        """
        Read sensor data. Must be implemented by subclasses.
        
        Returns:
            dict: Sensor reading data
        """
        pass
    
    def to_json(self):
        """
        Format sensor data as JSON.
        
        Returns:
            str: JSON string representation of sensor data
        """
        data = self.read()
        data.update({
            "sensorId": self.sensor_id,
            "deviceId": self.device_id,
            "sensorType": self.sensor_type,
            "timestamp": self.get_timestamp()
        })
        return json.dumps(data)
    
    def __str__(self):
        """
        String representation of the sensor.
        
        Returns:
            str: String representation
        """
        return f"{self.sensor_type} Sensor (ID: {self.sensor_id})"
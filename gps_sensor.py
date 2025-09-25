"""
GPS sensor simulation for IoT waste bin monitoring system.
Simulates location data with configurable starting position and movement range.
"""

import random
from .sensor_base import SensorBase


class GPSSensor(SensorBase):
    """
    GPS sensor class that simulates location data with random movement patterns.
    
    Features:
    - Configurable starting position
    - Configurable movement range
    - Random movement simulation
    - Latitude and longitude coordinates
    - Location data for Azure IoT Central map visualization
    """
    
    def __init__(self, device_id=None, 
                 initial_latitude=0.0, initial_longitude=0.0,
                 movement_range=0.0115):
        """
        Initialize the GPS sensor with starting position and movement parameters.
        
        Args:
            device_id (str, optional): Device ID to associate with this sensor
            initial_latitude (float): Starting latitude coordinate
            initial_longitude (float): Starting longitude coordinate
            movement_range (float): Maximum distance the simulated position can move
                                   in a single reading (in degrees)
        """
        super().__init__("gps", device_id)
        self.latitude = initial_latitude
        self.longitude = initial_longitude
        self.movement_range = movement_range
    
    def read(self):
        """
        Generate simulated GPS coordinates with random movement.
        
        Returns:
            dict: Dictionary containing latitude, longitude, and location data
        """
        # Simulate small random movements
        self.latitude += random.uniform(-self.movement_range, self.movement_range)
        self.longitude += random.uniform(-self.movement_range, self.movement_range)
        
        # Ensure latitude stays within valid range (-90 to 90)
        self.latitude = max(-90.0, min(90.0, self.latitude))
        
        # Ensure longitude stays within valid range (-180 to 180)
        self.longitude = max(-180.0, min(180.0, self.longitude))
        
        # Round coordinates for cleaner display
        lat = round(self.latitude, 6)
        lon = round(self.longitude, 6)
        
        return {
            "latitude": lat,
            "longitude": lon,
            # Add location data in format compatible with Azure IoT Central map visualization
            "location": {
                "lat": lat,
                "lon": lon,
                "alt": 0.0,  # Altitude (in meters)
                "accuracy": 5.0  # Accuracy in meters
            }
        }
    
    def set_position(self, latitude, longitude):
        """
        Manually set the current position of the GPS sensor.
        
        Args:
            latitude (float): Latitude coordinate to set
            longitude (float): Longitude coordinate to set
        """
        self.latitude = max(-90.0, min(90.0, latitude))
        self.longitude = max(-180.0, min(180.0, longitude))


if __name__ == "__main__":
    # Example usage for testing
    gps = GPSSensor(initial_latitude=1.3521, initial_longitude=103.8198)  # Singapore
    
    # Generate 5 readings to demonstrate movement
    for _ in range(5):
        reading = gps.read()
        print(f"GPS Reading: Lat {reading['latitude']}, Long {reading['longitude']}")
        print(f"Location: {reading['location']}")
        print(f"JSON: {gps.to_json()}")
"""
Humidity sensor simulation for IoT waste bin monitoring system.
Simulates humidity levels with configurable parameters.
"""

import random
from .sensor_base import SensorBase


class HumiditySensor(SensorBase):
    """
    Humidity sensor class that simulates humidity levels in waste bins.
    
    Features:
    - Humidity percentage measurement
    - High humidity detection
    - Humidity correlation with fill level
    - Random humidity variation
    - Mold risk assessment
    """
    
    def __init__(self, device_id=None, 
                 base_humidity=50.0,
                 humidity_variation=5.0,
                 high_humidity_threshold=75.0,
                 mold_risk_threshold=80.0,
                 fill_level_correlation=0.6):
        """
        Initialize the humidity sensor with humidity parameters.
        
        Args:
            device_id (str, optional): Device ID to associate with this sensor
            base_humidity (float): Base humidity percentage
            humidity_variation (float): Random variation in humidity
            high_humidity_threshold (float): Threshold for high humidity alert
            mold_risk_threshold (float): Threshold for mold risk alert
            fill_level_correlation (float): Correlation factor between fill level and humidity
        """
        super().__init__("humidity", device_id)
        self.base_humidity = base_humidity
        self.humidity_variation = humidity_variation
        self.high_humidity_threshold = high_humidity_threshold
        self.mold_risk_threshold = mold_risk_threshold
        self.fill_level_correlation = fill_level_correlation
        self.current_humidity = base_humidity
    
    def read(self, fill_level=None):
        """
        Generate simulated humidity reading with random variation.
        
        Args:
            fill_level (float, optional): Current fill level percentage to correlate with humidity
        
        Returns:
            dict: Dictionary containing humidity data and status
        """
        # Calculate base humidity with fill level correlation if provided
        if fill_level is not None:
            # Higher fill levels increase humidity
            fill_factor = min(fill_level / 100.0, 1.0) * self.fill_level_correlation
            base_humidity = self.base_humidity + (fill_factor * 30.0)  # Up to 30% increase
        else:
            base_humidity = self.base_humidity
        
        # Add random variation
        variation = random.uniform(-self.humidity_variation, self.humidity_variation)
        humidity = max(0.0, min(100.0, base_humidity + variation))
        
        # Update current humidity
        self.current_humidity = humidity
        
        # Determine status
        is_high = humidity > self.high_humidity_threshold
        is_mold_risk = humidity > self.mold_risk_threshold
        
        # Calculate mold risk percentage
        mold_risk = 0.0
        if humidity > self.mold_risk_threshold:
            mold_risk = min(100.0, ((humidity - self.mold_risk_threshold) / (100.0 - self.mold_risk_threshold)) * 100.0)
        
        return {
            "humidity": round(humidity, 2),
            "unit": "percentage",
            "isHigh": is_high,
            "isMoldRisk": is_mold_risk,
            "moldRiskPercentage": round(mold_risk, 2),
            "status": "mold_risk" if is_mold_risk else ("high" if is_high else "normal"),
            # Add data in format compatible with Azure IoT Central visualization
            "humidityData": {
                "value": round(humidity, 2),
                "unit": "percentage",
                "status": "mold_risk" if is_mold_risk else ("high" if is_high else "normal"),
                "moldRisk": round(mold_risk, 2)
            }
        }
    
    def set_humidity(self, humidity):
        """
        Manually set the current humidity level.
        
        Args:
            humidity (float): Humidity percentage to set
        """
        self.current_humidity = max(0.0, min(100.0, humidity))


if __name__ == "__main__":
    # Example usage for testing
    humidity_sensor = HumiditySensor()
    
    # Generate 10 readings to demonstrate humidity changes
    for i in range(10):
        reading = humidity_sensor.read(fill_level=random.uniform(0, 100))
        status = reading["status"].upper()
        print(f"Reading {i+1}: {reading['humidity']}% ({status})")
        if reading["isMoldRisk"]:
            print(f"  Mold Risk: {reading['moldRiskPercentage']}%")
        print(f"JSON: {humidity_sensor.to_json()}") 
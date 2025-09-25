
import random
from .sensor_base import SensorBase


class AirQualitySensor(SensorBase):
    # Air quality categories based on AQI
    AQI_CATEGORIES = {
        "good": {"range": (0, 50), "color": "green"},
        "moderate": {"range": (51, 100), "color": "yellow"},
        "unhealthy_sensitive": {"range": (101, 150), "color": "orange"},
        "unhealthy": {"range": (151, 200), "color": "red"},
        "very_unhealthy": {"range": (201, 300), "color": "purple"},
        "hazardous": {"range": (301, 500), "color": "maroon"}
    }
    
    def __init__(self, device_id=None, 
                 base_aqi=50.0,
                 aqi_variation=10.0,
                 fill_level_correlation=0.7,
                 temperature_correlation=0.5):
        """
        Initialize the air quality sensor with measurement parameters.
        
        Args:
            device_id (str, optional): Device ID to associate with this sensor
            base_aqi (float): Base Air Quality Index value
            aqi_variation (float): Random variation in AQI
            fill_level_correlation (float): Correlation factor between fill level and air quality
            temperature_correlation (float): Correlation factor between temperature and air quality
        """
        super().__init__("air_quality", device_id)
        self.base_aqi = base_aqi
        self.aqi_variation = aqi_variation
        self.fill_level_correlation = fill_level_correlation
        self.temperature_correlation = temperature_correlation
        self.current_aqi = base_aqi
    
    def read(self, fill_level=None, temperature=None):
        """
        Generate simulated air quality reading with random variation.
        
        Args:
            fill_level (float, optional): Current fill level percentage to correlate with air quality
            temperature (float, optional): Current temperature in Celsius to correlate with air quality
        
        Returns:
            dict: Dictionary containing air quality data and status
        """
        # Calculate base AQI with correlations if provided
        base_aqi = self.base_aqi
        
        if fill_level is not None:
            # Higher fill levels decrease air quality
            fill_factor = min(fill_level / 100.0, 1.0) * self.fill_level_correlation
            base_aqi += (fill_factor * 100.0)  # Up to 100 AQI increase
        
        if temperature is not None:
            # Higher temperatures can decrease air quality
            temp_factor = max(0, (temperature - 25) / 25) * self.temperature_correlation
            base_aqi += (temp_factor * 50.0)  # Up to 50 AQI increase
        
        # Add random variation
        variation = random.uniform(-self.aqi_variation, self.aqi_variation)
        aqi = max(0.0, min(500.0, base_aqi + variation))
        
        # Update current AQI
        self.current_aqi = aqi
        
        # Determine AQI category
        category = "good"
        for cat, props in self.AQI_CATEGORIES.items():
            min_val, max_val = props["range"]
            if min_val <= aqi <= max_val:
                category = cat
                break
        
        # Calculate pollutant levels based on AQI
        co2_level = 400 + (aqi * 2)  # Base CO2 (400 ppm) plus AQI contribution
        voc_level = 0.5 + (aqi * 0.01)  # Base VOC (0.5 ppm) plus AQI contribution
        pm25_level = 12 + (aqi * 0.24)  # Base PM2.5 (12 μg/m³) plus AQI contribution
        
        return {
            "aqi": round(aqi, 2),
            "category": category,
            "color": self.AQI_CATEGORIES[category]["color"],
            "co2": round(co2_level, 2),
            "co2Unit": "ppm",
            "voc": round(voc_level, 2),
            "vocUnit": "ppm",
            "pm25": round(pm25_level, 2),
            "pm25Unit": "μg/m³",
            "status": category,
            # Add data in format compatible with Azure IoT Central visualization
            "airQualityData": {
                "aqi": round(aqi, 2),
                "category": category,
                "color": self.AQI_CATEGORIES[category]["color"],
                "pollutants": {
                    "co2": round(co2_level, 2),
                    "voc": round(voc_level, 2),
                    "pm25": round(pm25_level, 2)
                }
            }
        }
    
    def set_aqi(self, aqi):
        """
        Manually set the current Air Quality Index.
        
        Args:
            aqi (float): AQI value to set
        """
        self.current_aqi = max(0.0, min(500.0, aqi))
    
    def get_category_for_aqi(self, aqi):
        """
        Get the air quality category for a given AQI value.
        
        Args:
            aqi (float): AQI value to categorize
        
        Returns:
            str: Air quality category
        """
        for category, props in self.AQI_CATEGORIES.items():
            min_val, max_val = props["range"]
            if min_val <= aqi <= max_val:
                return category
        return "hazardous"  # Default for values above 500


if __name__ == "__main__":
    # Example usage for testing
    air_quality_sensor = AirQualitySensor()
    
    # Generate 10 readings to demonstrate air quality changes
    for i in range(10):
        reading = air_quality_sensor.read(
            fill_level=random.uniform(0, 100),
            temperature=random.uniform(20, 35)
        )
        category = reading["category"].upper()
        print(f"Reading {i+1}: AQI {reading['aqi']} ({category})")
        print(f"  CO2: {reading['co2']} ppm, VOC: {reading['voc']} ppm, PM2.5: {reading['pm25']} μg/m³")
        print(f"JSON: {air_quality_sensor.to_json()}") 
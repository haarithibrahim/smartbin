"""
Odor sensor simulation for IoT waste bin monitoring system.
Simulates odor detection with configurable parameters.
"""

import random
from .sensor_base import SensorBase


class OdorSensor(SensorBase):
    """
    Odor sensor class that simulates odor detection in waste bins.
    
    Features:
    - Odor intensity measurement
    - Odor type classification
    - Odor threshold detection
    - Odor level correlation with fill level
    - Random odor variation
    """
    
    # Odor types and their characteristics
    ODOR_TYPES = {
        "organic": {
            "description": "Decomposing organic waste",
            "intensity_range": (0.1, 1.0),
            "correlation_with_fill": 0.8
        },
        "chemical": {
            "description": "Chemical waste or cleaning products",
            "intensity_range": (0.3, 0.9),
            "correlation_with_fill": 0.5
        },
        "mold": {
            "description": "Mold or mildew growth",
            "intensity_range": (0.2, 0.7),
            "correlation_with_fill": 0.6
        },
        "none": {
            "description": "No significant odor",
            "intensity_range": (0.0, 0.1),
            "correlation_with_fill": 0.1
        }
    }
    
    def __init__(self, device_id=None, 
                 odor_threshold=0.6,
                 fill_level_correlation=0.7,
                 odor_variation=0.1):
        """
        Initialize the odor sensor with detection parameters.
        
        Args:
            device_id (str, optional): Device ID to associate with this sensor
            odor_threshold (float): Threshold for significant odor detection (0-1)
            fill_level_correlation (float): Correlation factor between fill level and odor
            odor_variation (float): Random variation in odor intensity
        """
        super().__init__("odor", device_id)
        self.odor_threshold = odor_threshold
        self.fill_level_correlation = fill_level_correlation
        self.odor_variation = odor_variation
        self.current_odor_type = "none"
        self.current_intensity = 0.0
    
    def read(self, fill_level=None):
        """
        Generate simulated odor reading with random variation.
        
        Args:
            fill_level (float, optional): Current fill level percentage to correlate with odor
        
        Returns:
            dict: Dictionary containing odor data and status
        """
        # Determine odor type based on fill level correlation if provided
        if fill_level is not None:
            # Higher fill levels increase chance of stronger odors
            fill_factor = min(fill_level / 100.0, 1.0) * self.fill_level_correlation
            
            # Select odor type based on fill level
            if fill_factor > 0.8:
                odor_type = random.choices(
                    ["organic", "chemical", "mold", "none"],
                    weights=[0.5, 0.3, 0.15, 0.05],
                    k=1
                )[0]
            elif fill_factor > 0.5:
                odor_type = random.choices(
                    ["organic", "chemical", "mold", "none"],
                    weights=[0.3, 0.2, 0.3, 0.2],
                    k=1
                )[0]
            elif fill_factor > 0.2:
                odor_type = random.choices(
                    ["organic", "chemical", "mold", "none"],
                    weights=[0.1, 0.2, 0.2, 0.5],
                    k=1
                )[0]
            else:
                odor_type = random.choices(
                    ["organic", "chemical", "mold", "none"],
                    weights=[0.05, 0.1, 0.1, 0.75],
                    k=1
                )[0]
        else:
            # Random odor type selection if no fill level provided
            odor_type = random.choices(
                list(self.ODOR_TYPES.keys()),
                weights=[0.3, 0.2, 0.2, 0.3],
                k=1
            )[0]
        
        # Get intensity range for the selected odor type
        min_intensity, max_intensity = self.ODOR_TYPES[odor_type]["intensity_range"]
        
        # Calculate base intensity
        base_intensity = random.uniform(min_intensity, max_intensity)
        
        # Add random variation
        variation = random.uniform(-self.odor_variation, self.odor_variation)
        intensity = max(0.0, min(1.0, base_intensity + variation))
        
        # Update current state
        self.current_odor_type = odor_type
        self.current_intensity = intensity
        
        # Determine if odor is significant
        is_significant = intensity > self.odor_threshold
        
        return {
            "odorType": odor_type,
            "odorDescription": self.ODOR_TYPES[odor_type]["description"],
            "intensity": round(intensity, 3),
            "unit": "normalized",
            "isSignificant": is_significant,
            "status": "significant" if is_significant else "normal",
            # Add data in format compatible with Azure IoT Central visualization
            "odorData": {
                "type": odor_type,
                "intensity": round(intensity, 3),
                "status": "significant" if is_significant else "normal"
            }
        }
    
    def set_odor(self, odor_type, intensity):
        """
        Manually set the current odor type and intensity.
        
        Args:
            odor_type (str): Type of odor to set
            intensity (float): Odor intensity to set (0-1)
        """
        if odor_type in self.ODOR_TYPES:
            self.current_odor_type = odor_type
            self.current_intensity = max(0.0, min(1.0, intensity))


if __name__ == "__main__":
    # Example usage for testing
    odor_sensor = OdorSensor()
    
    # Generate 10 readings to demonstrate odor detection
    for i in range(10):
        reading = odor_sensor.read(fill_level=random.uniform(0, 100))
        status = reading["status"].upper()
        print(f"Reading {i+1}: {reading['odorType']} - Intensity: {reading['intensity']} ({status})")
        print(f"JSON: {odor_sensor.to_json()}") 
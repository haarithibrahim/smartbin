import random
from .sensor_base import SensorBase


class FillLevelSensor(SensorBase):

    def __init__(self, device_id=None, 
                 initial_fill_level=10.0,
                 fill_rate=0.05,
                 capacity=100.0,
                 fill_rate_variation=0.02,
                 overflow_threshold=95.0):

        super().__init__("fill_level", device_id)
        self.fill_level = min(initial_fill_level, capacity)
        self.fill_rate = fill_rate
        self.capacity = capacity
        self.fill_rate_variation = fill_rate_variation
        self.overflow_threshold = overflow_threshold
    
    def read(self):
        """
        Generate simulated fill level reading with random variation.
        
        Returns:
            dict: Dictionary containing fill level data and status
        """
        # Calculate random fill rate variation
        variation = random.uniform(-self.fill_rate_variation, self.fill_rate_variation)
        current_fill_rate = self.fill_rate + variation
        
        # Update fill level
        self.fill_level = min(self.fill_level + current_fill_rate, self.capacity)
        
        # Round fill level for cleaner display
        fill_level = round(self.fill_level, 2)
        
        # Determine status
        is_full = fill_level >= self.overflow_threshold
        is_overflowing = fill_level >= self.capacity
        
        return {
            "fillLevel": fill_level,
            "unit": "percentage",
            "capacity": self.capacity,
            "isFull": is_full,
            "isOverflowing": is_overflowing,
            "status": "overflow" if is_overflowing else ("full" if is_full else "normal"),
            # Add data in format compatible with Azure IoT Central visualization
            "fillLevelData": {
                "value": fill_level,
                "unit": "percentage",
                "status": "overflow" if is_overflowing else ("full" if is_full else "normal")
            }
        }
    
    def set_fill_level(self, fill_level):
        """
        Manually set the current fill level.
        
        Args:
            fill_level (float): Fill level percentage to set
        """
        self.fill_level = min(max(0.0, fill_level), self.capacity)
    
    def empty_bin(self):
        """
        Simulate emptying the bin by resetting fill level to 0.
        """
        self.fill_level = 0.0


if __name__ == "__main__":
    # Set fill_rate to 5.0 and fill_rate_variation to 0.0 for consistent increments
    fill_sensor = FillLevelSensor(initial_fill_level=20.0, fill_rate=5.0, fill_rate_variation=0.0)
    
    for i in range(10):
        reading = fill_sensor.read()
        status = reading["status"].upper()
        print(f"Reading {i+1}: {reading['fillLevel']}% ({status})")
        print(f"JSON: {fill_sensor.to_json()}") 
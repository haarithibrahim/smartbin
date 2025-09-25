import random
from .sensor_base import SensorBase


class TemperatureSensor(SensorBase):
    """
    Temperature sensor class that simulates temperature fluctuations.
    
    Features:
    - Configurable normal temperature range
    - Configurable anomaly thresholds
    - Abnormal temperature detection (e.g., potential fires)
    - Random temperature fluctuation simulation
    - Forced anomaly after 3 normal readings
    """
    
    def __init__(self, device_id=None, 
                 base_temperature=22.0,
                 normal_fluctuation=2.0,
                 anomaly_threshold_high=50.0,
                 anomaly_threshold_low=0.0,
                 anomaly_probability=0.05,
                 normal_readings_before_anomaly=3):
        """
        Initialize the temperature sensor with temperature parameters.
        
        Args:
            device_id (str, optional): Device ID to associate with this sensor
            base_temperature (float): Base temperature in Celsius
            normal_fluctuation (float): Normal range of temperature fluctuation
            anomaly_threshold_high (float): High temperature threshold for anomaly detection
            anomaly_threshold_low (float): Low temperature threshold for anomaly detection
            anomaly_probability (float): Probability of generating an anomaly reading (0-1)
            normal_readings_before_anomaly (int): Number of normal readings before forcing an anomaly
        """
        super().__init__("temperature", device_id)
        self.base_temperature = base_temperature
        self.normal_fluctuation = normal_fluctuation
        self.anomaly_threshold_high = anomaly_threshold_high
        self.anomaly_threshold_low = anomaly_threshold_low
        self.anomaly_probability = anomaly_probability
        self.normal_readings_before_anomaly = normal_readings_before_anomaly
        self.current_temperature = base_temperature
        self.normal_readings_count = 0
    
    def read(self):
        """
        Generate simulated temperature reading with possible anomalies.
        
        Returns:
            dict: Dictionary containing temperature value and anomaly status
        """
        #force anomaly for the sake of testing
        force_anomaly = self.normal_readings_count >= self.normal_readings_before_anomaly
        
        is_anomaly = force_anomaly or random.random() < self.anomaly_probability
        
        if is_anomaly:
            #reset the normal readings counter
            self.normal_readings_count = 0
            
            # Generate an  reading (either very high or very low)
            if random.random() < 0.7: 
                # High temperature anomaly (such as fire)
                self.current_temperature = self.anomaly_threshold_high + random.uniform(0, 20)
            else:
                # Low temperature anomaly (such as freezing)
                self.current_temperature = self.anomaly_threshold_low - random.uniform(0, 10)
        else:
            # Increment the normal readings counter
            self.normal_readings_count += 1
            
            # Generate a normal reading with random fluctuation
            fluctuation = random.uniform(-self.normal_fluctuation, self.normal_fluctuation)
            # Gradually drift back to base temperature
            self.current_temperature = (0.8 * self.current_temperature + 
                                       0.2 * self.base_temperature + 
                                       fluctuation)
        
        # Determine if the current temperature is outside normal range
        is_high_anomaly = self.current_temperature > self.anomaly_threshold_high
        is_low_anomaly = self.current_temperature < self.anomaly_threshold_low
        
        return {
            "temperature": round(self.current_temperature, 2),
            "unit": "Celsius",
            "isAnomaly": is_high_anomaly or is_low_anomaly,
            "anomalyType": "high" if is_high_anomaly else ("low" if is_low_anomaly else "none")
        }
    
    def set_temperature(self, temperature):
        """
        Manually set the current temperature of the sensor.
        
        Args:
            temperature (float): Temperature value to set in Celsius
        """
        self.current_temperature = temperature


if __name__ == "__main__":
    # Example usage for testing
    temp_sensor = TemperatureSensor()
    
    # Generate 10 readings to demonstrate normal and anomalous temperatures
    for i in range(10):
        reading = temp_sensor.read()
        status = "ANOMALY!" if reading["isAnomaly"] else "normal"
        print(f"Reading {i+1}: {reading['temperature']}°C ({status})")
        print(f"JSON: {temp_sensor.to_json()}")
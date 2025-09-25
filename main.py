
import asyncio
import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path

# Import sensor modules
from sensors.gps_sensor import GPSSensor
from sensors.temperature_sensor import TemperatureSensor
from sensors.recyclable_sensor import RecyclableSensor
from sensors.fill_level_sensor import FillLevelSensor
from sensors.odor_sensor import OdorSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.air_quality_sensor import AirQualitySensor

# Import token system
from token_system.token_manager import TokenManager, User

# Import Azure IoT client
from iot_azure.iot_client import AzureIoTCentralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WasteBinIoTSimulation:
    """
    Main class for the waste bin IoT simulation system.
    
    Integrates sensors, Azure IoT client, and token reward system.
    """
    
    def __init__(self, config_path="config/azure_config.json"):
        """
        Initialize the waste bin IoT simulation system.
        
        Args:
            config_path (str): Path to the Azure IoT Central configuration file
        """
        self.device_id = f"waste-bin-{random.randint(1000, 9999)}"
        logger.info(f"Initializing waste bin IoT simulation with device ID: {self.device_id}")
        
        # Initialize token manager
        self.token_manager = TokenManager()
        
        # Initialize sensors
        self.gps_sensor = GPSSensor(
            device_id=self.device_id,
            initial_latitude=1.3521,  #singapore
            initial_longitude=103.8198,
            movement_range=0.0001  
        )
        
        self.temp_sensor = TemperatureSensor(
            device_id=self.device_id,
            base_temperature=22.0,
            normal_fluctuation=2.0,
            anomaly_threshold_high=50.0,
            anomaly_threshold_low=0.0,
            anomaly_probability=0.05
        )
        
        self.recyclable_sensor = RecyclableSensor(
            device_id=self.device_id,
            detection_probabilities={
                "paper": 0.3,
                "plastic": 0.4,
                "metal": 0.15,
                "glass": 0.1,
                "e-waste": 0.05
            },
            token_manager=self.token_manager
        )
        
        # Initialize new sensors
        
        self.fill_level_sensor = FillLevelSensor(
            device_id=self.device_id,
            initial_fill_level=01.0,
            fill_rate=5.0,
            capacity=100.0,
            fill_rate_variation=0.1,
            overflow_threshold=100.0
        )
        
        self.odor_sensor = OdorSensor(
            device_id=self.device_id,
            odor_threshold=0.6,
            fill_level_correlation=0.7,
            odor_variation=0.1
        )
        
        self.humidity_sensor = HumiditySensor(
            device_id=self.device_id,
            base_humidity=50.0,
            humidity_variation=5.0,
            high_humidity_threshold=75.0,
            mold_risk_threshold=80.0,
            fill_level_correlation=0.6
        )
        
        self.air_quality_sensor = AirQualitySensor(
            device_id=self.device_id,
            base_aqi=50.0,
            aqi_variation=10.0,
            fill_level_correlation=0.7,
            temperature_correlation=0.5
        )
        
        # Initialize Azure IoT client
        try:
            self.azure_config_path = Path(config_path)
            if not self.azure_config_path.exists():
                logger.error(f"Azure IoT configuration file not found: {config_path}")
                raise FileNotFoundError(f"Azure IoT configuration file not found: {config_path}")
            else:
                self.azure_client = AzureIoTCentralClient(config_path=str(self.azure_config_path))
                logger.info("Azure IoT Central client initialized")
        except Exception as e:
            logger.error(f"Error initializing Azure IoT client: {e}")
            raise
        
        # Register sample users
        self.users = [
            self.token_manager.register_user("John Smith"),
            self.token_manager.register_user("Maria Garcia"),
            self.token_manager.register_user("Ahmed Hassan")
        ]
        
        # Print configuration
        self._print_configuration()
    
    def _print_configuration(self):
        """Print the configuration of the waste bin IoT simulation system."""
        print("\nIoT Waste Bin Monitoring System - Configuration")
        print("=" * 70)
        
        print("\nDevice Information:")
        print(f"  Device ID: {self.device_id}")
        
        print("\nToken System Configuration:")
        print("  Token values per kg:")
        for material, value in self.token_manager.token_values.items():
            print(f"    {material}: {value} tokens")
        
        print("\n  Redemption options:")
        for option, rate in self.token_manager.redemption_options.items():
            print(f"    {option}: {rate} currency units per token")
        
        print("\nRegistered Users:")
        for user in self.users:
            print(f"  {user}")
        
        print("\nAzure IoT Central Integration:")
        if self.azure_client:
            print("  Enabled")
            print(f"  Configuration file: {self.azure_config_path}")
        else:
            print("  Disabled")
        
        print("\n" + "=" * 70)
    
    def format_telemetry_for_azure(self, combined_data):
        """
        Format telemetry data for Azure IoT Central.
        
        Args:
            combined_data (dict): Combined sensor data
            
        Returns:
            dict: Formatted telemetry data for Azure IoT Central
        """
        # Format data according to Azure IoT Central requirements
        # Flatten the structure for better visualization in Data Explorer
        telemetry = {
            "deviceId": combined_data["deviceId"],
            "timestamp": combined_data["timestamp"],
            "userId": combined_data["userId"],
            "userName": combined_data["userName"],
            "tokenBalance": combined_data["tokenBalance"],
            "latitude": combined_data["location"]["latitude"],
            "longitude": combined_data["location"]["longitude"],
            # Add location data in format compatible with Azure IoT Central map visualization
            "location": combined_data["location"],
            "temperature": combined_data["temperature"]["value"],
            "temperatureUnit": combined_data["temperature"]["unit"],
            "temperatureAnomaly": combined_data["temperature"]["isAnomaly"],
            "temperatureAnomalyType": combined_data["temperature"]["anomalyType"],
            "materialDetected": combined_data["recyclable"]["materialDetected"],
            "materialType": combined_data["recyclable"]["materialType"] if combined_data["recyclable"]["materialDetected"] else "",
            "materialSubtype": combined_data["recyclable"]["materialSubtype"] if combined_data["recyclable"]["materialDetected"] else "",
            "materialWeight": combined_data["recyclable"]["weight"] if combined_data["recyclable"]["materialDetected"] else 0.0,
            "materialWeightUnit": combined_data["recyclable"]["weightUnit"],
            "tokensAwarded": combined_data["recyclable"]["tokensAwarded"]
        }
        
        # Add fill level data if available
        if "fill_level" in combined_data:
            fill_level_data = combined_data["fill_level"]
            telemetry.update({
                "fillLevel": fill_level_data.get("fillLevel", 0.0),
                "fillLevelUnit": fill_level_data.get("unit", "percentage"),
                "fillLevelStatus": fill_level_data.get("status", "normal"),
                "isFull": fill_level_data.get("isFull", False),
                "isOverflowing": fill_level_data.get("isOverflowing", False)
            })
        
        # Add odor data if available
        if "odor" in combined_data:
            odor_data = combined_data["odor"]
            telemetry.update({
                "odorType": odor_data.get("odorType", "none"),
                "odorIntensity": odor_data.get("intensity", 0.0),
                "odorUnit": odor_data.get("unit", "scale"),
                "isSignificantOdor": odor_data.get("isSignificant", False),
                "odorStatus": odor_data.get("status", "normal")
            })
        
        # Add humidity data if available
        if "humidity" in combined_data:
            humidity_data = combined_data["humidity"]
            telemetry.update({
                "humidity": humidity_data.get("humidity", 0.0),
                "humidityUnit": humidity_data.get("unit", "percentage"),
                "isHighHumidity": humidity_data.get("isHigh", False),
                "isMoldRisk": humidity_data.get("isMoldRisk", False),
                "moldRiskPercentage": humidity_data.get("moldRiskPercentage", 0.0),
                "humidityStatus": humidity_data.get("status", "normal")
            })
        
        # Add air quality data if available
        if "air_quality" in combined_data:
            air_quality_data = combined_data["air_quality"]
            telemetry.update({
                "aqi": air_quality_data.get("aqi", 0.0),
                "aqiCategory": air_quality_data.get("category", "unknown"),
                "aqiColor": air_quality_data.get("color", "gray"),
                "co2": air_quality_data.get("co2", 0.0),
                "co2Unit": air_quality_data.get("co2Unit", "ppm"),
                "voc": air_quality_data.get("voc", 0.0),
                "vocUnit": air_quality_data.get("vocUnit", "ppm"),
                "pm25": air_quality_data.get("pm25", 0.0),
                "pm25Unit": air_quality_data.get("pm25Unit", "μg/m³"),
                "airQualityStatus": air_quality_data.get("status", "normal")
            })
        
        return telemetry
    
    async def send_telemetry_to_azure(self, telemetry_data):
        """
        Send telemetry data to Azure IoT Central.
        
        Args:
            telemetry_data (dict): Telemetry data to send
            
        Returns:
            bool: True if data was sent successfully, False otherwise
        """
        if not self.azure_client:
            logger.warning("Azure IoT Central client not initialized, skipping telemetry")
            return False
        
        try:
            # Send telemetry data to Azure IoT Central
            success = await self.azure_client.send_telemetry(telemetry_data)
            if success:
                logger.info("Telemetry data sent to Azure IoT Central")
            else:
                logger.error("Failed to send telemetry data to Azure IoT Central")
            return success
        except Exception as e:
            logger.error(f"Error sending telemetry data to Azure IoT Central: {e}")
            return False
    
    async def run_simulation(self, num_readings=15, delay_seconds=2):
        """
        Run the waste bin IoT simulation.
        
        Args:
            num_readings (int): Number of readings to simulate
            delay_seconds (int): Delay between readings in seconds
        """
        print("\nStarting waste bin IoT simulation...")
        print("=" * 70)
        
        # Connect to Azure IoT Central if client is available
        if self.azure_client:
            connected = await self.azure_client.connect_with_retry()
            if connected:
                print("Connected to Azure IoT Central")
            else:
                print("Failed to connect to Azure IoT Central")
        
        try:
            for i in range(num_readings):
                print(f"\nReading #{i+1} - Timestamp: {self.gps_sensor.get_timestamp()}")
                print("-" * 70)
                
                # Select a random user for this reading
                current_user = self.users[i % len(self.users)]
                self.recyclable_sensor.set_current_user(current_user.user_id)
                
                print(f"Current User: {current_user.name} (ID: {current_user.user_id})")
                print(f"Token Balance: {current_user.get_token_balance()}")
                
                # Get GPS reading
                gps_data = self.gps_sensor.read()
                print(f"GPS: Lat {gps_data['latitude']}, Long {gps_data['longitude']}")
                
                # Get temperature reading
                temp_data = self.temp_sensor.read()
                status = "ANOMALY!" if temp_data["isAnomaly"] else "normal"
                print(f"Temperature: {temp_data['temperature']}°C ({status})")
                
                # Get recyclable reading
                recyclable_data = self.recyclable_sensor.read()
                if recyclable_data["materialDetected"]:
                    print(f"Recyclable: {recyclable_data['materialSubtype']} "
                          f"({recyclable_data['materialType']}) - "
                          f"{recyclable_data['weight']} kg")
                    print(f"Tokens Awarded: {recyclable_data['tokensAwarded']}")
                else:
                    print("Recyclable: No material detected")
                
                try:
                    # Get fill level reading
                    fill_level_data = self.fill_level_sensor.read()
                    fill_status = fill_level_data["status"].upper()
                    print(f"Fill Level: {fill_level_data['fillLevel']}% ({fill_status})")
                    
                    # Get odor reading
                    odor_data = self.odor_sensor.read(fill_level=fill_level_data["fillLevel"])
                    odor_status = odor_data["status"].upper()
                    print(f"Odor: {odor_data['odorType']} - Intensity: {odor_data['intensity']} ({odor_status})")
                    
                    # Get humidity reading
                    humidity_data = self.humidity_sensor.read(fill_level=fill_level_data["fillLevel"])
                    humidity_status = humidity_data["status"].upper()
                    print(f"Humidity: {humidity_data['humidity']}% ({humidity_status})")
                    if humidity_data["isMoldRisk"]:
                        print(f"  Mold Risk: {humidity_data['moldRiskPercentage']}%")
                    
                    # Get air quality reading
                    air_quality_data = self.air_quality_sensor.read(
                        fill_level=fill_level_data["fillLevel"],
                        temperature=temp_data["temperature"]
                    )
                    aqi_status = air_quality_data["category"].upper()
                    print(f"Air Quality: AQI {air_quality_data['aqi']} ({aqi_status})")
                    print(f"  CO2: {air_quality_data['co2']} ppm, VOC: {air_quality_data['voc']} ppm, "
                          f"PM2.5: {air_quality_data['pm25']} μg/m³")
                    
                    # Combine all sensor data into a single payload
                    combined_data = {
                        "deviceId": self.device_id,
                        "timestamp": self.gps_sensor.get_timestamp(),
                        "userId": current_user.user_id,
                        "userName": current_user.name,
                        "tokenBalance": current_user.get_token_balance(),
                        "location": {
                            "latitude": gps_data["latitude"],
                            "longitude": gps_data["longitude"]
                        },
                        "temperature": {
                            "value": temp_data["temperature"],
                            "unit": temp_data["unit"],
                            "isAnomaly": temp_data["isAnomaly"],
                            "anomalyType": temp_data["anomalyType"]
                        },
                        "recyclable": {
                            "materialDetected": recyclable_data["materialDetected"],
                            "materialType": recyclable_data.get("materialType", ""),
                            "materialSubtype": recyclable_data.get("materialSubtype", ""),
                            "weight": recyclable_data.get("weight", 0.0),
                            "weightUnit": recyclable_data.get("weightUnit", "kg"),
                            "tokensAwarded": recyclable_data.get("tokensAwarded", 0)
                        },
                        "fill_level": fill_level_data,
                        "odor": odor_data,
                        "humidity": humidity_data,
                        "air_quality": air_quality_data
                    }
                    
                    # Format data for Azure IoT Central
                    azure_telemetry = self.format_telemetry_for_azure(combined_data)
                    
                    # Send telemetry to Azure IoT Central
                    if self.azure_client:
                        success = await self.send_telemetry_to_azure(azure_telemetry)
                        print(f"Azure IoT Central Telemetry: {'Sent' if success else 'Failed'}")
                except Exception as e:
                    logger.error(f"Error during reading: {str(e)}")
                    # Continue with next reading
                
                # Simulate token redemption every 5 readings
                if i > 0 and i % 5 == 0:
                    await self._simulate_token_redemption(i)
                
                # Wait before next reading
                if i < num_readings - 1:
                    print(f"\nWaiting {delay_seconds} seconds before next reading...")
                    await asyncio.sleep(delay_seconds)
                
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        except Exception as e:
            logger.error(f"Error during simulation: {e}")
        finally:
            # Disconnect from Azure IoT Central
            if self.azure_client and self.azure_client.connected:
                await self.azure_client.disconnect()
                print("Disconnected from Azure IoT Central")
            
            # Print final results
            self._print_final_results()
    
    async def _simulate_token_redemption(self, iteration):
        """
        Simulate token redemption by a user.
        
        Args:
            iteration (int): Current iteration number
        """
        # Select a random user for redemption
        user = random.choice(self.users)
        
        # Get available redemption options
        available_options = [
            option for option, rate in self.token_manager.redemption_options.items()
            if user.get_token_balance() >= 1 / rate  # Check if user has enough tokens
        ]
        
        if not available_options:
            print(f"\nToken Redemption: {user.name} has insufficient tokens for redemption")
            return
        
        # Select a random redemption option
        option = random.choice(available_options)
        rate = self.token_manager.redemption_options[option]
        
        # Calculate maximum tokens to redeem (up to 10 tokens or all available)
        max_tokens = min(10, user.get_token_balance())
        tokens_to_redeem = random.randint(1, max_tokens)
        
        # Redeem tokens
        success = self.token_manager.redeem_tokens(user.user_id, tokens_to_redeem, option)
        
        if success:
            reward = tokens_to_redeem * rate
            print(f"\nToken Redemption: {user.name} redeemed {tokens_to_redeem} tokens for {reward} {option}")
            print(f"  New token balance: {user.get_token_balance()}")
        else:
            print(f"\nToken Redemption: Failed to redeem tokens for {user.name}")
    
    def _print_final_results(self):
        """Print the final results of the simulation."""
        print("\nSimulation Results")
        print("=" * 70)
        
        print("\nFinal Token Balances:")
        for user in self.users:
            print(f"  {user.name}: {user.get_token_balance()} tokens")
        
        print("\nToken Redemption History:")
        for user in self.users:
            print(f"  {user.name}:")
            for redemption in user.redemption_history:
                print(f"    {redemption['timestamp']}: {redemption['tokens']} tokens for "
                      f"{redemption['reward']} {redemption['option']}")
        
        print("\n" + "=" * 70)


async def main():
    """Main entry point for the application."""
    # Create and run the waste bin IoT simulation
    simulation = WasteBinIoTSimulation()
    
    # Run the simulation with 15 readings and 2 seconds delay
    await simulation.run_simulation(num_readings=15, delay_seconds=2)


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
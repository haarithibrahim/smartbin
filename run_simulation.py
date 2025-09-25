"""
Continuous simulation script for the waste bin IoT monitoring system.

This script runs the waste bin IoT simulation indefinitely until manually stopped.
It allows you to specify the delay between readings.
"""

import os
import sys
import logging
import asyncio
import signal
import argparse

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the main application
from main import WasteBinIoTSimulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag to control the simulation loop
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully stop the simulation."""
    global running
    logger.info("Stopping simulation...")
    running = False

async def run_continuous_simulation(delay_seconds=2):
    """
    Run the waste bin IoT simulation continuously until manually stopped.
    
    Args:
        delay_seconds (int): Delay between readings in seconds
    """
    try:
        # Get the path to the config file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config", "azure_config.json")
        
        logger.info(f"Loading configuration from: {config_path}")
        
        # Initialize the waste bin IoT simulation
        simulation = WasteBinIoTSimulation(config_path=config_path)
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        
        # Connect to Azure IoT Central
        if simulation.azure_client:
            connected = await simulation.azure_client.connect_with_retry()
            if connected:
                logger.info("Connected to Azure IoT Central")
            else:
                logger.error("Failed to connect to Azure IoT Central")
        
        # Run the simulation continuously
        reading_count = 0
        logger.info(f"Starting continuous simulation with {delay_seconds} seconds delay between readings...")
        logger.info("Press Ctrl+C to stop the simulation")
        
        while running:
            try:
                # Get sensor readings
                gps_data = simulation.gps_sensor.read()
                temp_data = simulation.temp_sensor.read()
                
                # Select a random user for this reading
                current_user = simulation.users[reading_count % len(simulation.users)]
                simulation.recyclable_sensor.set_current_user(current_user.user_id)
                
                # Get recyclable reading
                recyclable_data = simulation.recyclable_sensor.read()
                
                # Get fill level reading
                fill_level_data = simulation.fill_level_sensor.read()
                
                # Get odor reading
                odor_data = simulation.odor_sensor.read(fill_level=fill_level_data["fillLevel"])
                
                # Get humidity reading
                humidity_data = simulation.humidity_sensor.read(fill_level=fill_level_data["fillLevel"])
                
                # Get air quality reading
                air_quality_data = simulation.air_quality_sensor.read(
                    fill_level=fill_level_data["fillLevel"],
                    temperature=temp_data["temperature"]
                )
                
                # Combine all sensor data into a single payload
                combined_data = {
                    "deviceId": simulation.device_id,
                    "timestamp": simulation.gps_sensor.get_timestamp(),
                    "userId": current_user.user_id,
                    "userName": current_user.name,
                    "tokenBalance": current_user.get_token_balance(),
                    "location": {
                        "latitude": gps_data["latitude"],
                        "longitude": gps_data["longitude"],
                        "lat": gps_data["latitude"],
                        "lon": gps_data["longitude"],
                        "alt": 0.0,
                        "accuracy": 5.0
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
                azure_telemetry = simulation.format_telemetry_for_azure(combined_data)
                
                # Send telemetry to Azure IoT Central
                if simulation.azure_client:
                    success = await simulation.send_telemetry_to_azure(azure_telemetry)
                    if success:
                        logger.info(f"Reading #{reading_count+1}: Telemetry data sent to Azure IoT Central")
                    else:
                        logger.error(f"Reading #{reading_count+1}: Failed to send telemetry data")
                
                # Print reading information
                print(f"\nReading #{reading_count+1} - Timestamp: {simulation.gps_sensor.get_timestamp()}")
                print("-" * 70)
                print(f"Current User: {current_user.name} (ID: {current_user.user_id})")
                print(f"Token Balance: {current_user.get_token_balance()}")
                print(f"GPS: Lat {gps_data['latitude']}, Long {gps_data['longitude']}")
                print(f"Location: {combined_data['location']}")
                
                status = "ANOMALY!" if temp_data["isAnomaly"] else "normal"
                print(f"Temperature: {temp_data['temperature']}°C ({status})")
                
                if recyclable_data["materialDetected"]:
                    print(f"Recyclable: {recyclable_data['materialSubtype']} "
                          f"({recyclable_data['materialType']}) - "
                          f"{recyclable_data['weight']} kg")
                    print(f"Tokens Awarded: {recyclable_data['tokensAwarded']}")
                else:
                    print("Recyclable: No material detected")
                
                # Print fill level information
                fill_status = fill_level_data["status"].upper()
                print(f"Fill Level: {fill_level_data['fillLevel']}% ({fill_status})")
                
                # Print odor information
                odor_status = odor_data["status"].upper()
                print(f"Odor: {odor_data['odorType']} - Intensity: {odor_data['intensity']} ({odor_status})")
                
                # Print humidity information
                humidity_status = humidity_data["status"].upper()
                print(f"Humidity: {humidity_data['humidity']}% ({humidity_status})")
                if humidity_data["isMoldRisk"]:
                    print(f"  Mold Risk: {humidity_data['moldRiskPercentage']}%")
                
                # Print air quality information
                aqi_status = air_quality_data["category"].upper()
                print(f"Air Quality: AQI {air_quality_data['aqi']} ({aqi_status})")
                print(f"  CO2: {air_quality_data['co2']} ppm, VOC: {air_quality_data['voc']} ppm, "
                      f"PM2.5: {air_quality_data['pm25']} μg/m³")
                
                # Increment reading count
                reading_count += 1
                
                # Wait before next reading
                if running:
                    print(f"\nWaiting {delay_seconds} seconds before next reading...")
                    await asyncio.sleep(delay_seconds)
                
            except Exception as e:
                logger.error(f"Error during reading: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(1)
        
        # Disconnect from Azure IoT Central
        if simulation.azure_client and simulation.azure_client.connected:
            await simulation.azure_client.disconnect()
            logger.info("Disconnected from Azure IoT Central")
        
        # Print final token balances
        simulation._print_final_results()
        logger.info(f"Simulation stopped after {reading_count} readings")
        
    except Exception as e:
        logger.error(f"Error running continuous simulation: {e}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the waste bin IoT simulation continuously")
    parser.add_argument("--delay", type=int, default=2, help="Delay between readings in seconds (default: 2)")
    args = parser.parse_args()
    
    # Run the continuous simulation
    asyncio.run(run_continuous_simulation(delay_seconds=args.delay)) 
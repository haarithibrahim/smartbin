"""
Test script for the Azure IoT Central client.

This script tests the Azure IoT Central client by loading the configuration
and attempting to connect to Azure IoT Central.
"""

import os
import sys
import logging
import asyncio

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the Azure IoT client
from iot_azure.iot_client import AzureIoTCentralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_azure_client():
    """Test the Azure IoT Central client."""
    try:
        # Get the path to the config file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config", "azure_config.json")
        
        logger.info(f"Loading configuration from: {config_path}")
        
        # Initialize the Azure IoT client
        client = AzureIoTCentralClient(config_path=config_path)
        
        # Connect to Azure IoT Central
        logger.info("Connecting to Azure IoT Central...")
        connected = await client.connect()
        
        if connected:
            logger.info("Successfully connected to Azure IoT Central")
            
            # Send a test telemetry message
            test_data = {
                "temperature": 25.5,
                "humidity": 60.0,
                "location": {
                    "latitude": -33.865143,
                    "longitude": 151.209900
                }
            }
            
            logger.info("Sending test telemetry data...")
            success = await client.send_telemetry(test_data)
            
            if success:
                logger.info("Successfully sent telemetry data")
            else:
                logger.error("Failed to send telemetry data")
            
            # Disconnect from Azure IoT Central
            await client.disconnect()
            logger.info("Disconnected from Azure IoT Central")
        else:
            logger.error("Failed to connect to Azure IoT Central")
        
        return connected
    except Exception as e:
        logger.error(f"Error testing Azure IoT client: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_azure_client())
    if success:
        logger.info("Azure IoT client test passed")
    else:
        logger.error("Azure IoT client test failed") 
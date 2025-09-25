"""
Test script for Azure IoT Central Client

This script tests the functionality of the AzureIoTCentralClient class
by attempting to load configuration and connect to Azure IoT Central.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from src.azure.iot_client import AzureIoTCentralClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_client_initialization():
    """Test loading configuration and initializing the client."""
    try:
        # Get the absolute path to the config file
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  "config", "azure_config.json")
        
        logger.info(f"Loading configuration from: {config_path}")
        client = AzureIoTCentralClient(config_path=config_path)
        logger.info("Client initialized successfully")
        
        # Check if configuration was loaded correctly
        logger.info(f"Loaded configuration: ID Scope: {client.config['id_scope']}, "
                   f"Device ID: {client.config['device_id']}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing client: {e}")
        return False


async def test_client_connection():
    """Test connecting to Azure IoT Central."""
    try:
        # Get the absolute path to the config file
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  "config", "azure_config.json")
        
        client = AzureIoTCentralClient(config_path=config_path)
        
        # Check if the configuration has placeholder values
        if (client.config['id_scope'] == "YOUR_ID_SCOPE" or
            client.config['device_id'] == "YOUR_DEVICE_ID" or
            client.config['primary_key'] == "YOUR_PRIMARY_KEY"):
            logger.warning("Configuration contains placeholder values. "
                          "Update the config file with actual values before testing connection.")
            return False
        
        # Attempt to connect
        logger.info("Attempting to connect to Azure IoT Central...")
        connected = await client.connect_with_retry()
        
        if connected:
            logger.info("Successfully connected to Azure IoT Central")
            
            # Test sending a simple telemetry message
            test_data = {
                "test_value": 42,
                "message": "Test telemetry from waste bin IoT simulation"
            }
            
            formatted_data = client.format_telemetry(client.config['device_id'], test_data)
            success = await client.send_telemetry(formatted_data)
            
            if success:
                logger.info("Test telemetry sent successfully")
            else:
                logger.error("Failed to send test telemetry")
            
            # Disconnect
            await client.disconnect()
            return True
        else:
            logger.error("Failed to connect to Azure IoT Central")
            return False
            
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return False


async def run_tests():
    """Run all tests."""
    init_success = await test_client_initialization()
    if not init_success:
        logger.error("Client initialization test failed")
        return
    
    logger.info("Client initialization test passed")
    
    # Uncomment to test actual connection (requires valid credentials)
    # connection_success = await test_client_connection()
    # if connection_success:
    #     logger.info("Connection test passed")
    # else:
    #     logger.error("Connection test failed")


if __name__ == "__main__":
    asyncio.run(run_tests())
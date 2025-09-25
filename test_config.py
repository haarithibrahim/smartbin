"""
Simple test script to verify configuration loading

This script tests that the configuration file can be loaded correctly
without requiring the Azure IoT SDK to be installed.
"""

import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_config_loading():
    """Test loading the Azure IoT Central configuration file."""
    try:
        # Get the path to the config file
        # Use the correct path relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config", "azure_config.json")
        
        logger.info(f"Loading configuration from: {config_path}")
        
        # Load the configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check if all required keys are present
        required_keys = ['id_scope', 'device_id', 'primary_key']
        for key in required_keys:
            if key not in config:
                logger.error(f"Missing required configuration parameter: {key}")
                return False
        
        logger.info(f"Configuration loaded successfully:")
        logger.info(f"ID Scope: {config['id_scope']}")
        logger.info(f"Device ID: {config['device_id']}")
        logger.info(f"Primary Key: {'*' * len(config['primary_key'])}")  # Don't log the actual key
        
        return True
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        return False
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file: {config_path}")
        return False
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return False

if __name__ == "__main__":
    success = test_config_loading()
    if success:
        logger.info("Configuration test passed")
    else:
        logger.error("Configuration test failed")
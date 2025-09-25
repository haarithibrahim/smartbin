"""
Test script for the main waste bin IoT simulation application.

This script tests the main application by running a short simulation
with a small number of readings.
"""

import os
import sys
import logging
import asyncio

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

async def test_main_application():
    """Test the main waste bin IoT simulation application."""
    try:
        # Get the path to the config file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config", "azure_config.json")
        
        logger.info(f"Loading configuration from: {config_path}")
        
        # Initialize the waste bin IoT simulation
        simulation = WasteBinIoTSimulation(config_path=config_path)
        
        # Run a short simulation with 3 readings and a 1-second delay
        logger.info("Running simulation with 3 readings...")
        await simulation.run_simulation(num_readings=3, delay_seconds=1)
        
        logger.info("Simulation completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error testing main application: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_main_application())
    if success:
        logger.info("Main application test passed")
    else:
        logger.error("Main application test failed") 
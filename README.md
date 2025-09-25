# Waste Bin IoT Simulation System

## Project Overview

This project simulates an IoT-enabled waste bin monitoring system designed to track recyclable materials collected by informal waste collectors. The system uses various sensors to detect recyclable materials, awards tokens to users based on their collections, and sends telemetry data to Azure IoT Central for monitoring and analysis.

### Key Features

- **Sensor Simulation**: Simulates GPS location, temperature, and recyclable material detection
- **Token Reward System**: Awards tokens to users based on the type and weight of recyclables collected
- **Azure IoT Central Integration**: Connects to Azure IoT Central to send telemetry data
- **User Management**: Tracks users, their token balances, and redemption history
- **Redemption System**: Allows users to redeem tokens for various rewards

## System Architecture

The system is built with a modular architecture consisting of the following components:

### 1. Sensor Modules

- **Base Sensor**: Abstract base class providing common functionality for all sensors
- **GPS Sensor**: Simulates location data with configurable starting position and movement range
- **Temperature Sensor**: Simulates temperature readings with anomaly detection
- **Recyclable Sensor**: Simulates detection of different recyclable materials with weight estimation

### 2. Token System

- **Token Manager**: Manages token rewards, user registration, and redemption
- **User**: Represents a waste collector with token balance and history

### 3. Azure IoT Integration

- **IoT Client**: Handles connection to Azure IoT Central and sending telemetry data
- **Configuration**: Stores Azure IoT Central connection details

### 4. Main Application

- Integrates all components into a cohesive system
- Implements simulation loop
- Formats and sends data to Azure IoT Central
- Demonstrates token reward system in action

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Waste Bin IoT Simulation                  │
└───────────────────────────────┬─────────────────────────────┘
                                │
        ┌─────────────────────┬─┴───────────┬─────────────────┐
        │                     │             │                 │
┌───────▼───────┐     ┌───────▼───────┐    ┌▼────────────┐   ┌▼────────────┐
│  Sensor Layer │     │  Token System │    │ Azure IoT   │   │    Main     │
└───────┬───────┘     └───────┬───────┘    │ Integration │   │ Application │
        │                     │            └─────┬───────┘   └─────────────┘
        │                     │                  │
┌───────▼───────┐     ┌───────▼───────┐    ┌─────▼───────┐
│  GPS Sensor   │     │ Token Manager │    │ IoT Client  │
├───────────────┤     ├───────────────┤    └─────────────┘
│ Temperature   │     │     User      │
│    Sensor     │     │  Management   │
├───────────────┤     └───────────────┘
│  Recyclable   │
│    Sensor     │
└───────────────┘
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Azure IoT Central account (for IoT Central integration)
- Required Python packages:
  - azure-iot-device
  - asyncio

### Installation

1. Clone the repository:
   ```bash
   git clone <https://github.com/haarithibrahim/smartbin.git>
   cd waste_bin_iot_simulation
   ```

2. Install required packages:
   ```bash
   pip install azure-iot-device asyncio
   ```

3. Configure Azure IoT Central:
   - Create a device template in Azure IoT Central
   - Register a new device
   - Update the `config/azure_config.json` file with your credentials:
     ```json
     {
       "id_scope": "YOUR_ID_SCOPE",
       "device_id": "YOUR_DEVICE_ID",
       "primary_key": "YOUR_PRIMARY_KEY"
     }
     ```

### Azure IoT Central Configuration

To set up Azure IoT Central for this project:

1. Create a new application in Azure IoT Central
2. Create a device template with the following capabilities:
   - GPS location (latitude, longitude)
   - Temperature
   - Recyclable material detection (type, weight)
   - Token balance
3. Add views to visualize the data
4. Register a new device using the device template
5. Get the connection details (ID Scope, Device ID, Primary Key)
6. Update the configuration file

## Running the Simulation

To run the simulation:

```bash
cd waste_bin_iot_simulation
python src/main.py
```

The simulation will:
1. Initialize sensors, token manager, and Azure IoT client
2. Register sample users
3. Generate sensor readings at regular intervals
4. Award tokens based on recyclable detections
5. Send telemetry data to Azure IoT Central
6. Simulate token redemptions
7. Display results in the console

## Sample Console Output

```
IoT Waste Bin Monitoring System - Simulation with Azure IoT Central Integration
================================================================================

IoT Waste Bin Monitoring System - Configuration
======================================================================

Device Information:
  Device ID: waste-bin-1234

Token System Configuration:
  Token values per kg:
    paper: 5.0 tokens
    plastic: 10.0 tokens
    metal: 15.0 tokens
    glass: 8.0 tokens
    e-waste: 20.0 tokens

  Redemption options:
    cash: 0.1 currency units per token
    grocery_voucher: 0.12 currency units per token
    public_transport: 0.15 currency units per token
    mobile_credit: 0.11 currency units per token

Registered Users:
  User: John Smith (ID: 123e4567-e89b-12d3-a456-426614174000), Balance: 0.0 tokens
  User: Maria Garcia (ID: 223e4567-e89b-12d3-a456-426614174001), Balance: 0.0 tokens
  User: Ahmed Hassan (ID: 323e4567-e89b-12d3-a456-426614174002), Balance: 0.0 tokens

Azure IoT Central Integration:
  Enabled
  Configuration file: config/azure_config.json

======================================================================

Starting waste bin IoT simulation...
======================================================================
Connected to Azure IoT Central

Reading #1 - Timestamp: 2025-04-24T06:56:06.123456Z
----------------------------------------------------------------------
Current User: John Smith (ID: 123e4567-e89b-12d3-a456-426614174000)
Token Balance: 0.0
GPS: Lat -33.865143, Long 151.209900
Temperature: 22.5°C (normal)
Recyclable: PET bottle (plastic) - 0.25 kg
Tokens Awarded: 2.5
Azure IoT Central Telemetry: Sent

Waiting 2 seconds before next reading...

Reading #2 - Timestamp: 2025-04-24T06:56:08.234567Z
----------------------------------------------------------------------
Current User: Maria Garcia (ID: 223e4567-e89b-12d3-a456-426614174001)
Token Balance: 0.0
GPS: Lat -33.865142, Long 151.209901
Temperature: 21.8°C (normal)
Recyclable: aluminum can (metal) - 0.15 kg
Tokens Awarded: 2.25
Azure IoT Central Telemetry: Sent

Waiting 2 seconds before next reading...
```

## Token System Explanation

The token system rewards users for collecting recyclable materials:

1. **Token Values**: Different materials have different token values per kg:
   - Plastic: 10.0 tokens/kg
   - Paper: 5.0 tokens/kg
   - Metal: 15.0 tokens/kg
   - Glass: 8.0 tokens/kg
   - E-waste: 20.0 tokens/kg

2. **Token Awarding**: When a user deposits recyclable material, they are awarded tokens based on the material type and weight.

3. **Token Redemption**: Users can redeem tokens for various rewards:
   - Cash: 0.1 currency units per token
   - Grocery vouchers: 0.12 currency units per token
   - Public transport: 0.15 currency units per token
   - Mobile credit: 0.11 currency units per token

4. **User Tracking**: The system tracks each user's token balance, collection history, and redemption history.

## Extension Possibilities

The system can be extended in several ways:

1. **Additional Sensors**:
   - Add a fill level sensor to monitor bin capacity
   - Implement a moisture sensor to detect liquid contamination
   - Add a weight sensor for more accurate measurements

2. **Enhanced Token System**:
   - Implement tiered rewards for frequent collectors
   - Add expiration dates for tokens
   - Create a marketplace for token redemption

3. **Mobile Application**:
   - Develop a mobile app for users to track their tokens
   - Implement QR code scanning for bin identification
   - Add real-time notifications for token awards

4. **Advanced Analytics**:
   - Implement machine learning for predictive maintenance
   - Create heatmaps of collection activity
   - Analyze recycling patterns to optimize bin placement

5. **Blockchain Integration**:
   - Store token transactions on a blockchain for transparency
   - Implement smart contracts for automatic redemption
   - Create a decentralized marketplace for token exchange

## License

This project is licensed under the MIT License - see the LICENSE file for details.

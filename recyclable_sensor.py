"""
Recyclable classification sensor simulation for IoT waste bin monitoring system.
Simulates detection of different recyclable types with weight estimation.
"""

import random
from .sensor_base import SensorBase


class RecyclableSensor(SensorBase):
    """
    Recyclable classification sensor that simulates detection of different recyclable types.
    
    Features:
    - Detection of different recyclable materials (plastic, paper, metal, glass, etc.)
    - Weight estimation based on real-world average weights
    - Configurable detection probabilities for different materials
    - Integration with token reward system
    """
    
    # Material types and their properties based on real-world data
    MATERIAL_TYPES = {
        "paper": {
            "subtypes": ["newspaper", "cardboard", "magazine", "mixed paper"],
            "weight_range": (0.05, 2.0),  # kg
            "density": 75.0  # pounds per cubic yard (loose)
        },
        "plastic": {
            "subtypes": ["PET bottle", "HDPE container", "plastic bag", "plastic packaging"],
            "weight_range": (0.01, 0.5),  # kg
            "density": 35.0  # pounds per cubic yard (loose)
        },
        "metal": {
            "subtypes": ["aluminum can", "steel can", "metal lid", "foil"],
            "weight_range": (0.02, 0.5),  # kg
            "density": 62.5  # pounds per cubic yard (loose)
        },
        "glass": {
            "subtypes": ["clear bottle", "green bottle", "brown bottle", "glass jar"],
            "weight_range": (0.1, 1.0),  # kg
            "density": 500.0  # pounds per cubic yard (loose)
        },
        "e-waste": {
            "subtypes": ["battery", "small electronic", "cable", "charger"],
            "weight_range": (0.05, 2.0),  # kg
            "density": 350.0  # pounds per cubic yard (loose)
        }
    }
    
    def __init__(self, device_id=None, detection_probabilities=None, token_manager=None):
        """
        Initialize the recyclable classification sensor.
        
        Args:
            device_id (str, optional): Device ID to associate with this sensor
            detection_probabilities (dict, optional): Dictionary mapping material types
                                                     to their detection probabilities
            token_manager (TokenManager, optional): Token manager for awarding tokens
        """
        super().__init__("recyclable", device_id)
        
        # Default detection probabilities if none provided
        self.detection_probabilities = detection_probabilities or {
            "paper": 0.3,
            "plastic": 0.4,
            "metal": 0.15,
            "glass": 0.1,
            "e-waste": 0.05
        }
        
        # Token manager for awarding tokens
        self.token_manager = token_manager
        
        # Current user ID for token awards
        self.current_user_id = None
    
    def read(self):
        """
        Generate simulated recyclable detection with material type and weight.
        
        Returns:
            dict: Dictionary containing detected material type, subtype, and weight
        """
        # Determine if any material is detected
        if random.random() > 0.9:  # 10% chance of no detection
            return {
                "materialDetected": False,
                "materialType": None,
                "materialSubtype": None,
                "weight": 0.0,
                "weightUnit": "kg"
            }
        
        # Select material type based on detection probabilities
        material_type = random.choices(
            list(self.detection_probabilities.keys()),
            weights=list(self.detection_probabilities.values()),
            k=1
        )[0]
        
        # Select a random subtype for the material
        material_subtype = random.choice(self.MATERIAL_TYPES[material_type]["subtypes"])
        
        # Generate a random weight within the range for this material
        min_weight, max_weight = self.MATERIAL_TYPES[material_type]["weight_range"]
        weight = round(random.uniform(min_weight, max_weight), 3)
        
        # Award tokens if token manager and user ID are set
        tokens_awarded = 0.0
        if self.token_manager and self.current_user_id:
            success, tokens_awarded = self.token_manager.award_tokens(
                self.current_user_id,
                material_type,
                material_subtype,
                weight,
                self.get_timestamp()
            )
        
        return {
            "materialDetected": True,
            "materialType": material_type,
            "materialSubtype": material_subtype,
            "weight": weight,
            "weightUnit": "kg",
            "density": self.MATERIAL_TYPES[material_type]["density"],
            "densityUnit": "pounds/cubic_yard",
            "tokensAwarded": tokens_awarded,
            "userId": self.current_user_id
        }
    
    def set_detection_probabilities(self, detection_probabilities):
        """
        Update the detection probabilities for different material types.
        
        Args:
            detection_probabilities (dict): Dictionary mapping material types
                                          to their detection probabilities
        """
        # Validate that probabilities sum to approximately 1.0
        total_prob = sum(detection_probabilities.values())
        if not 0.99 <= total_prob <= 1.01:
            raise ValueError(f"Detection probabilities must sum to approximately 1.0, got {total_prob}")
        
        self.detection_probabilities = detection_probabilities
    
    def set_token_manager(self, token_manager):
        """
        Set the token manager for awarding tokens.
        
        Args:
            token_manager (TokenManager): Token manager for awarding tokens
        """
        self.token_manager = token_manager
    
    def set_current_user(self, user_id):
        """
        Set the current user ID for token awards.
        
        Args:
            user_id (str): User ID to associate with recyclable detections
        """
        self.current_user_id = user_id
    
    def detect_recyclable_for_user(self, user_id):
        """
        Detect recyclable material for a specific user.
        
        Args:
            user_id (str): User ID to associate with recyclable detection
        
        Returns:
            dict: Dictionary containing detected material type, subtype, weight, and tokens awarded
        """
        self.set_current_user(user_id)
        return self.read()


if __name__ == "__main__":
    # Example usage for testing
    recyclable_sensor = RecyclableSensor()
    
    # Generate 10 readings to demonstrate material detection
    for i in range(10):
        reading = recyclable_sensor.read()
        if reading["materialDetected"]:
            print(f"Reading {i+1}: Detected {reading['materialSubtype']} ({reading['materialType']}) - {reading['weight']} kg")
        else:
            print(f"Reading {i+1}: No material detected")
        print(f"JSON: {recyclable_sensor.to_json()}")
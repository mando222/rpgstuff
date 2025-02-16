from typing import Tuple, Optional
import math
import random

class Ballistics:
    @staticmethod
    def calculate_shot(shooter, target, weapon) -> Tuple[bool, str, float]:
        """Calculate if a shot hits, where it hits, and the damage multiplier"""
        
        distance = math.sqrt((shooter.x - target.x)**2 + (shooter.y - target.y)**2)
        if distance > weapon.range:
            return False, "none", 0.0
            
        # Base accuracy calculation
        accuracy = weapon.accuracy
        
        # Roll for hit
        if random.random() > accuracy:
            return False, "none", 0.0
            
        # Determine hit location
        locations = ["head", "torso", "left_arm", "right_arm", "left_leg", "right_leg"]
        weights = [0.1, 0.4, 0.125, 0.125, 0.125, 0.125]
        hit_location = random.choices(locations, weights)[0]
        
        # Calculate damage multiplier
        damage_mult = {
            "head": 4.0,
            "torso": 1.0,
            "left_arm": 0.7,
            "right_arm": 0.7,
            "left_leg": 0.6,
            "right_leg": 0.6
        }.get(hit_location, 1.0)
        
        # Apply distance falloff
        distance_mult = 1.0 - (distance / weapon.range) * 0.5
        damage_mult *= distance_mult
        
        return True, hit_location, damage_mult
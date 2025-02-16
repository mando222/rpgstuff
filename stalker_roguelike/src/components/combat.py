from typing import Dict, Optional, Tuple
from ..items.weapons import Weapon
from ..items.armor import Armor

class Combat:
    def __init__(self):
        self.bleeding_rate = 0.0
        self.radiation_level = 0
        self.status_effects: Dict[str, int] = {}  # effect -> duration
        
    def calculate_damage(self, weapon: Weapon, distance: float, hit_location: str) -> float:
        if distance > weapon.range:
            return 0
            
        base_damage = weapon.damage
        # Apply distance falloff
        damage_falloff = max(0, 1 - (distance / weapon.range))
        
        # Apply limb multiplier
        from ..constants import DAMAGE_MULTIPLIERS
        location_multiplier = DAMAGE_MULTIPLIERS.get(hit_location, 1.0)
        
        return base_damage * damage_falloff * location_multiplier
        
    def apply_damage(self, damage: float, damage_type: str, hit_location: str, 
                    armor: Optional[Armor] = None) -> Tuple[float, bool]:
        if armor:
            damage = armor.calculate_protection(damage_type, damage)
            armor.apply_damage(int(damage))
            
        # Critical hit check
        is_critical = hit_location == "head" and damage > 50
            
        # Apply bleeding chance based on damage
        if damage > 10 and damage_type == "physical":
            self.bleeding_rate += damage * 0.1
            
        return damage, is_critical
        
    def update_effects(self) -> float:
        """Update status effects and return damage dealt this tick"""
        damage = 0.0
        
        # Apply bleeding damage
        if self.bleeding_rate > 0:
            damage += self.bleeding_rate
            self.bleeding_rate = max(0, self.bleeding_rate - 0.1)  # Bleeding reduces over time
            
        # Update effect durations
        expired = []
        for effect, duration in self.status_effects.items():
            self.status_effects[effect] = duration - 1
            if self.status_effects[effect] <= 0:
                expired.append(effect)
                
        for effect in expired:
            del self.status_effects[effect]
            
        return damage

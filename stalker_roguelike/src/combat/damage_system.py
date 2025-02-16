from typing import Dict, List, Optional
import random
from ..entities.actor import Actor
from ..items.armor import Armor

class DamageSystem:
    @staticmethod
    def apply_damage(target: Actor, damage: float, damage_type: str, 
                    hit_location: str, attacker: Optional[Actor] = None) -> Dict:
        """Apply damage to target with detailed effects"""
        
        # Get armor at hit location
        armor = target.inventory.equipped.get(hit_location)
        
        # Calculate damage reduction from armor
        if armor:
            damage = armor.calculate_protection(damage_type, damage)
            armor.apply_damage(int(damage))
            
        # Apply final damage to health
        target.stats.modify_health(-damage)
        
        # Calculate additional effects
        effects = DamageSystem._calculate_effects(damage, damage_type, hit_location)
        
        # Apply effects
        for effect, duration in effects.items():
            target.combat.status_effects[effect] = duration
            
        # Calculate bleeding
        if damage > 10 and damage_type == "physical":
            bleeding_chance = min(0.8, damage / 100.0)
            if random.random() < bleeding_chance:
                target.combat.bleeding_rate += damage * 0.05
                
        return {
            "damage": damage,
            "effects": effects,
            "bleeding": target.combat.bleeding_rate > 0
        }
        
    @staticmethod
    def _calculate_effects(damage: float, damage_type: str, hit_location: str) -> Dict[str, int]:
        effects = {}
        
        if damage_type == "physical":
            if hit_location in ["left_leg", "right_leg"] and damage > 20:
                effects["limping"] = int(damage)
            elif hit_location in ["left_arm", "right_arm"] and damage > 15:
                effects["arm_damage"] = int(damage)
                
        elif damage_type == "radiation":
            effects["radiation_sickness"] = int(damage * 2)
            
        elif damage_type == "chemical":
            effects["poisoned"] = int(damage * 1.5)
            
        return effects 
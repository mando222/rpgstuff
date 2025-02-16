from typing import Optional, Dict
import math
from .entity import Entity
from ..components.stats import Stats
from ..components.inventory import Inventory
from ..components.combat import Combat
from ..combat.ballistics import Ballistics

class Actor(Entity):
    def __init__(self, x: int, y: int, char: str, color: tuple):
        super().__init__(x, y, char, color)
        self.stats = Stats()
        self.inventory = Inventory(20)  # Default capacity
        self.combat = Combat()
        self.facing = 0  # Angle in degrees
        self.faction = "neutral"
        self.ai = None
        
    def move(self, dx: int, dy: int) -> bool:
        # Check stamina cost
        stamina_cost = self._calculate_movement_cost(dx, dy)
        if self.stats.current_stamina >= stamina_cost:
            self.stats.modify_stamina(-stamina_cost)
            super().move(dx, dy)
            return True
        return False
        
    def _calculate_movement_cost(self, dx: int, dy: int) -> float:
        base_cost = 1.0
        # Apply armor movement penalties
        if self.inventory.equipped["torso"]:
            base_cost += self.inventory.equipped["torso"].movement_penalty
        if self.inventory.equipped["legs"]:
            base_cost += self.inventory.equipped["legs"].movement_penalty
        # Diagonal movement costs more
        if dx != 0 and dy != 0:
            base_cost *= 1.4
        return base_cost
        
    def attack(self, target: 'Actor', weapon: Optional[str] = "weapon_primary") -> Dict:
        equipped_weapon = self.inventory.equipped[weapon]
        if not equipped_weapon:
            return {"hit": False, "reason": "no_weapon"}
            
        # Calculate ballistics
        hit, location, damage_mult = Ballistics.calculate_shot(self, target, equipped_weapon)
        
        if not hit:
            return {"hit": False, "reason": "missed"}
            
        # Calculate and apply damage
        damage = equipped_weapon.damage * damage_mult
        target.stats.modify_health(-int(damage))
        
        return {
            "hit": True,
            "location": location,
            "damage": damage,
            "effects": {},
            "bleeding": False
        }
        
    def _determine_hit_location(self) -> str:
        # Simplified hit location determination
        import random
        locations = ["head", "torso", "left_arm", "right_arm", "left_leg", "right_leg"]
        weights = [0.1, 0.4, 0.125, 0.125, 0.125, 0.125]
        return random.choices(locations, weights)[0]
        
    def update(self) -> None:
        super().update()
        
        # Regenerate stamina
        if self.stats.current_stamina < self.stats.max_stamina:
            self.stats.modify_stamina(1)
            
        # Apply combat effects
        damage = self.combat.update_effects()
        if damage > 0:
            self.stats.modify_health(-damage)

    def distance_to(self, other: 'Actor') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

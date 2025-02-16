from typing import Dict
from .item import Item

class Weapon(Item):
    def __init__(self, name: str, description: str, weight: float):
        super().__init__(name, description, weight, "weapon", {"weapon_primary", "weapon_secondary"})
        self.damage = 0
        self.range = 0
        self.accuracy = 0
        self.rate_of_fire = 0
        self.ammo_type = ""
        self.current_ammo = 0
        self.max_ammo = 0
        self.jam_chance = 0.0

    def reload(self, ammo_count: int) -> int:
        space_left = self.max_ammo - self.current_ammo
        ammo_to_load = min(space_left, ammo_count)
        self.current_ammo += ammo_to_load
        return ammo_to_load

    def fire(self) -> bool:
        if self.current_ammo > 0 and self.stats.condition > 0:
            self.current_ammo -= 1
            self.degrade(1)
            return True
        return False

class RangedWeapon(Weapon):
    def __init__(self, name: str, description: str, weight: float):
        super().__init__(name, description, weight)
        self.effective_range = 0
        self.spread = 0.0
        self.recoil = 0.0

class MeleeWeapon(Weapon):
    def __init__(self, name: str, description: str, weight: float):
        super().__init__(name, description, weight)
        self.swing_speed = 0.0
        self.stamina_cost = 0 
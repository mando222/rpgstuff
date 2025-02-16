from typing import Dict
from .item import Item

class Armor(Item):
    def __init__(self, name: str, description: str, weight: float, slot: str):
        super().__init__(name, description, weight, "armor", {slot})
        self.protection = {
            "physical": 0,
            "radiation": 0,
            "anomaly": 0,
            "thermal": 0,
            "chemical": 0,
            "electrical": 0
        }
        self.movement_penalty = 0
        self.stamina_drain = 0
        self.noise_factor = 1.0

    def calculate_protection(self, damage_type: str, damage: float) -> float:
        if damage_type in self.protection:
            protection_factor = self.protection[damage_type] * (self.stats.condition / 100.0)
            return damage * (1 - protection_factor)
        return damage

    def apply_damage(self, amount: int) -> None:
        self.degrade(amount)
        # Reduce protection as condition decreases 
from .item import Item
from typing import Callable, Dict, Any

class Consumable(Item):
    def __init__(self, name: str, description: str, weight: float):
        super().__init__(name, description, weight, "consumable", set())
        self.uses = 1
        self.effects: Dict[str, Callable[[Any], None]] = {}
        
    def use(self, user) -> bool:
        if self.uses <= 0:
            return False
            
        for effect in self.effects.values():
            effect(user)
            
        self.uses -= 1
        return True

class MedKit(Consumable):
    def __init__(self):
        super().__init__("Medkit", "Basic medical supplies", 0.5)
        self.effects["heal"] = lambda user: user.stats.modify_health(50)

class Bandage(Consumable):
    def __init__(self):
        super().__init__("Bandage", "Stops bleeding", 0.1)
        self.effects["stop_bleeding"] = lambda user: user.remove_effect("bleeding")

class AntiRad(Consumable):
    def __init__(self):
        super().__init__("Anti-rad", "Reduces radiation", 0.2)
        self.effects["reduce_radiation"] = lambda user: user.modify_radiation(-500) 
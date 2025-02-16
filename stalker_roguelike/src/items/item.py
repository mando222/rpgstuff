from typing import Tuple, Set, Optional
from dataclasses import dataclass

@dataclass
class ItemStats:
    durability: int = 100
    condition: int = 100
    value: int = 0

class Item:
    def __init__(self, 
                 name: str, 
                 description: str,
                 weight: float,
                 item_type: str,
                 valid_slots: Set[str]):
        self.name = name
        self.description = description
        self.weight = weight
        self.item_type = item_type
        self.valid_slots = valid_slots
        self.stats = ItemStats()
        self.icon: Optional[str] = None

    def can_equip(self, slot: str) -> bool:
        return slot in self.valid_slots

    def use(self, user) -> bool:
        return False

    def degrade(self, amount: int) -> None:
        self.stats.condition = max(0, self.stats.condition - amount) 
from typing import List, Optional, Dict
from ..items.item import Item

class Inventory:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []
        self.weight = 0
        self.max_weight = 50.0  # kg
        
        # Equipment slots
        self.equipped: Dict[str, Optional[Item]] = {
            "weapon_primary": None,
            "weapon_secondary": None,
            "head": None,
            "torso": None,
            "legs": None
        }

    def add_item(self, item: Item) -> bool:
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item: Item) -> bool:
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def equip_item(self, item: Item, slot: str) -> Optional[Item]:
        if slot not in self.equipped:
            return None
            
        if not item.can_equip(slot):
            return None

        # Remove from inventory
        if item in self.items:
            self.remove_item(item)

        # Unequip current item in slot if any
        old_item = self.equipped[slot]
        if old_item:
            self.add_item(old_item)

        self.equipped[slot] = item
        return old_item

    def unequip_item(self, slot: str) -> Optional[Item]:
        if slot not in self.equipped or not self.equipped[slot]:
            return None

        item = self.equipped[slot]
        if self.add_item(item):
            self.equipped[slot] = None
            return item
        return None 
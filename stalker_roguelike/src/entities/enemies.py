from typing import Dict, Optional, Tuple
import random
import math
from .entity import Entity
from ..components.stats import Stats
from ..components.combat import Combat
from ..components.ai import AI
from ..items.weapons import RangedWeapon, MeleeWeapon
from ..items.armor import Armor

class Enemy(Entity):
    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int], 
                 enemy_type: str):
        super().__init__(x, y, char, color)
        self.enemy_type = enemy_type
        self.faction = self._get_faction()
        self.name = self._get_name()
        self.stats = self._get_stats()
        self.combat = Combat()
        self.game_state = None
        self.difficulty = 1.0
        self.ai = AI(self)
        self._setup_enemy()
        
    def update(self) -> None:
        super().update()
        if not self.game_state:
            return
            
        # Basic movement toward player if nearby
        player = self.game_state.player
        dist = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        
        if dist < 8:  # Aggro range
            # Move toward player
            dx = 0
            dy = 0
            if player.x > self.x:
                dx = 1
            elif player.x < self.x:
                dx = -1
            if player.y > self.y:
                dy = 1
            elif player.y < self.y:
                dy = -1
                
            # Try to move
            if self.game_state.current_zone.is_walkable(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                
            # Attack if adjacent
            if dist <= 1.5:
                damage = random.randint(5, 10)
                player.stats.modify_health(-damage)
                self.game_state.add_message(
                    f"{self.name} attacks for {damage} damage!", 
                    (255, 0, 0)
                )
                
    def _get_faction(self) -> str:
        return {
            "bandit": "bandits",
            "military": "military",
            "mutant": "mutants",
            "zombie": "mutants"
        }.get(self.enemy_type, "hostile")
        
    def _get_name(self) -> str:
        return {
            "bandit": "Bandit",
            "military": "Military Stalker",
            "mutant": "Mutant",
            "zombie": "Zombie Stalker"
        }.get(self.enemy_type, "Unknown Enemy")
        
    def _get_stats(self) -> Stats:
        health, stamina = {
            "bandit": (50, 100),
            "military": (75, 100),
            "mutant": (100, 150),
            "zombie": (40, 50)
        }.get(self.enemy_type, (50, 100))
        return Stats(health, stamina)

    def _setup_enemy(self) -> None:
        if self.enemy_type in ENEMY_TEMPLATES:
            template = ENEMY_TEMPLATES[self.enemy_type]
            self.name = template["name"]
            self.faction = template["faction"]
            
            # Scale stats with difficulty
            self.stats.max_health = int(template["health"] * self.difficulty)
            self.stats.current_health = self.stats.max_health
            
            # Equipment
            if "weapon" in template:
                self._equip_weapon(template["weapon"])
            if "armor" in template:
                self._equip_armor(template["armor"])
                
    def _equip_weapon(self, weapon_data: Dict) -> None:
        if weapon_data["type"] == "ranged":
            weapon = RangedWeapon(weapon_data["name"], 
                                weapon_data["description"], 
                                weapon_data["weight"])
            weapon.damage = weapon_data["damage"]
            weapon.range = weapon_data["range"]
            weapon.accuracy = weapon_data["accuracy"]
        else:
            weapon = MeleeWeapon(weapon_data["name"],
                               weapon_data["description"],
                               weapon_data["weight"])
            weapon.damage = weapon_data["damage"]
            weapon.swing_speed = weapon_data["speed"]
            
        self.inventory.equip_item(weapon, "weapon_primary")
        
    def _equip_armor(self, armor_data: Dict) -> None:
        armor = Armor(armor_data["name"],
                     armor_data["description"],
                     armor_data["weight"],
                     armor_data["slot"])
        armor.protection = armor_data["protection"]
        self.inventory.equip_item(armor, armor_data["slot"])

# Enemy templates
ENEMY_TEMPLATES = {
    "bandit": {
        "name": "Bandit",
        "faction": "bandits",
        "health": 80,
        "weapon": {
            "type": "ranged",
            "name": "Worn AK-74",
            "description": "A well-used assault rifle",
            "weight": 3.0,
            "damage": 25,
            "range": 8,
            "accuracy": 0.7
        },
        "armor": {
            "name": "Leather Jacket",
            "description": "Basic protection",
            "weight": 2.0,
            "slot": "torso",
            "protection": {
                "physical": 0.2,
                "radiation": 0.1
            }
        }
    },
    "military": {
        "name": "Military Stalker",
        "faction": "military",
        "health": 120,
        "weapon": {
            "type": "ranged",
            "name": "AN-94",
            "description": "Military-grade assault rifle",
            "weight": 3.5,
            "damage": 35,
            "range": 10,
            "accuracy": 0.85
        },
        "armor": {
            "name": "Military Armor",
            "description": "Standard military protection",
            "weight": 8.0,
            "slot": "torso",
            "protection": {
                "physical": 0.5,
                "radiation": 0.3,
                "anomaly": 0.2
            }
        }
    },
    "mutant_dog": {
        "name": "Blind Dog",
        "faction": "mutants",
        "health": 60,
        "weapon": {
            "type": "melee",
            "name": "Fangs",
            "description": "Sharp teeth",
            "weight": 0,
            "damage": 20,
            "speed": 1.2
        }
    }
}

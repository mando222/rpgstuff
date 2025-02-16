import pygame
from typing import Optional, Dict, List
from .entity import Entity
from ..items.item import Item
from ..constants import PLAYER_START_HEALTH, PLAYER_START_STAMINA
from ..components.stats import Stats
from ..components.inventory import Inventory
from ..components.combat import Combat

class Player(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "@", (255, 255, 255))  # White @ symbol
        self.name = "Stalker"
        self.level = 1
        self.experience = 0
        self.reputation = {
            "loners": 0,
            "bandits": -50,
            "military": 0,
            "scientists": 0
        }
        self.known_locations: List[str] = []
        self.active_quests: List[Dict] = []
        self.completed_quests: List[str] = []
        self.stats = Stats(PLAYER_START_HEALTH, PLAYER_START_STAMINA)
        self.inventory = Inventory(20)  # 20 slots
        self.combat = Combat()
        self.faction = "player"
        
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle player input"""
        if event.type == pygame.KEYDOWN:
            # Movement
            if event.key == pygame.K_UP:
                self.move(0, -1)
            elif event.key == pygame.K_DOWN:
                self.move(0, 1)
            elif event.key == pygame.K_LEFT:
                self.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.move(1, 0)
            # Diagonal movement
            elif event.key == pygame.K_y:  # Up-left
                self.move(-1, -1)
            elif event.key == pygame.K_u:  # Up-right
                self.move(1, -1)
            elif event.key == pygame.K_b:  # Down-left
                self.move(-1, 1)
            elif event.key == pygame.K_n:  # Down-right
                self.move(1, 1)
        
    def gain_experience(self, amount: int) -> bool:
        self.experience += amount
        # Check for level up
        exp_needed = self.level * 1000  # Simple level scaling
        if self.experience >= exp_needed:
            self.level_up()
            return True
        return False
        
    def level_up(self) -> None:
        self.level += 1
        # Increase base stats
        self.stats.max_health += 10
        self.stats.max_stamina += 5
        self.stats.modify_health(self.stats.max_health)  # Heal on level up
        
    def modify_reputation(self, faction: str, amount: int) -> None:
        if faction in self.reputation:
            self.reputation[faction] = max(-100, min(100, self.reputation[faction] + amount))
            
    def get_faction_standing(self, faction: str) -> str:
        rep = self.reputation.get(faction, 0)
        if rep >= 75:
            return "Trusted"
        elif rep >= 25:
            return "Friendly"
        elif rep >= -25:
            return "Neutral"
        elif rep >= -75:
            return "Hostile"
        else:
            return "Enemy"

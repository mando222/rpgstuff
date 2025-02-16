import pygame
import math
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
        self.is_moving = False
        self.move_cooldown = 0
        self.move_delay = 10  # Adjust this to control movement speed (higher = slower)
        
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle player input"""
        if event.type == pygame.KEYDOWN and not self.is_moving:
            # Only handle movement if not already moving and cooldown is done
            if self.move_cooldown <= 0:
                dx, dy = 0, 0
                
                # Movement keys (WASD and Arrow keys)
                if event.key in (pygame.K_UP, pygame.K_w):
                    dy = -1  # Up is negative y
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    dy = 1   # Down is positive y
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    dx = -1  # Left is negative x
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    dx = 1   # Right is positive x
                    
                # Diagonal movement (optional)
                elif event.key == pygame.K_q:  # Up-left
                    dx, dy = -1, -1
                elif event.key == pygame.K_e:  # Up-right
                    dx, dy = 1, -1
                elif event.key == pygame.K_z:  # Down-left
                    dx, dy = -1, 1
                elif event.key == pygame.K_c:  # Down-right
                    dx, dy = 1, 1
                    
                if dx != 0 or dy != 0:
                    # Try to move and set cooldown if successful
                    if self.move(dx, dy):
                        self.move_cooldown = self.move_delay
                        self.is_moving = True
                        
                        # Update facing direction
                        if dx != 0 or dy != 0:
                            self.facing = math.atan2(dy, dx)
                            
    def update(self) -> None:
        super().update()
        
        # Update movement cooldown
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            if self.move_cooldown <= 0:
                self.is_moving = False
                
        # Regenerate stamina when not moving
        if not self.is_moving and self.stats.current_stamina < self.stats.max_stamina:
            self.stats.modify_stamina(1)
            
        # Check for death
        if self.stats.current_health <= 0 and not hasattr(self, 'is_dead'):
            self.die()
        
    def move(self, dx: int, dy: int) -> bool:
        """Try to move by dx, dy. Return True if successful."""
        if self.is_moving and self.move_cooldown > 0:
            return False
            
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if the move is valid
        if self.game_state and self.game_state.current_zone.is_walkable(new_x, new_y):
            # Check stamina cost
            stamina_cost = self._calculate_movement_cost(dx, dy)
            if self.stats.current_stamina >= stamina_cost:
                # Apply the move
                self.x = new_x
                self.y = new_y
                self.stats.modify_stamina(-stamina_cost)
                self.move_cooldown = self.move_delay
                self.is_moving = True
                return True
        return False
        
    def _calculate_movement_cost(self, dx: int, dy: int) -> float:
        base_cost = 1.0
        
        # Get current tile properties
        if self.game_state:
            current_tile = self.game_state.current_zone.tiles[self.x][self.y]
            if current_tile.properties.is_water:
                base_cost *= 2.0  # Swimming costs more stamina
            
        # Apply armor movement penalties
        if self.inventory.equipped["torso"]:
            base_cost += self.inventory.equipped["torso"].movement_penalty
        if self.inventory.equipped["legs"]:
            base_cost += self.inventory.equipped["legs"].movement_penalty
            
        # Diagonal movement costs more
        if dx != 0 and dy != 0:
            base_cost *= 1.4
            
        return base_cost
        
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

    def die(self) -> None:
        """Handle player death"""
        self.is_dead = True
        if self.game_state:
            self.game_state.handle_player_death()

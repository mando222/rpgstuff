from typing import Optional, Tuple
import pygame
from ..constants import TILE_SIZE

class Entity:
    def __init__(self, x: int, y: int, char: str, color: tuple):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.game_state = None  # Set by game state when added to zone
        self.blocks_movement = False
        self.name = ""
        self.description = ""

    def move(self, dx: int, dy: int) -> bool:
        """Try to move by dx, dy. Return True if successful."""
        new_x = self.x + dx
        new_y = self.y + dy
        
        if self.game_state and self.game_state.current_zone.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False

    def distance_to(self, other) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def update(self) -> None:
        """Update entity state. Called once per game tick."""
        pass

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        screen_x = (self.x - camera_offset[0]) * TILE_SIZE
        screen_y = (self.y - camera_offset[1]) * TILE_SIZE
        
        # Draw entity
        pygame.draw.rect(surface, self.color, 
                        (screen_x, screen_y, TILE_SIZE, TILE_SIZE)) 
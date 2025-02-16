from typing import Tuple
import math
from ..constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class Camera:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Calculate view dimensions in tiles
        self.view_width = SCREEN_WIDTH // TILE_SIZE
        self.view_height = SCREEN_HEIGHT // TILE_SIZE
        
        # Keep player centered
        self.center_x = self.view_width // 2
        self.center_y = self.view_height // 2
        
    def update(self, target_x: int, target_y: int) -> None:
        """Update camera to keep target centered"""
        # Camera position is directly based on player position
        self.x = target_x - self.center_x
        self.y = target_y - self.center_y
        
        # Clamp camera to map bounds
        self.x = max(0, min(self.x, self.width - self.view_width))
        self.y = max(0, min(self.y, self.height - self.view_height))
        
    def get_offset(self) -> Tuple[int, int]:
        """Get current camera offset as integer coordinates"""
        return (int(self.x), int(self.y))
        
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x // TILE_SIZE + self.x
        world_y = screen_y // TILE_SIZE + self.y
        return (world_x, world_y)
        
    def world_to_screen(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.x) * TILE_SIZE
        screen_y = (world_y - self.y) * TILE_SIZE
        return (screen_x, screen_y) 
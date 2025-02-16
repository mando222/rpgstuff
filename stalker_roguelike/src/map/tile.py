from typing import Dict, Optional
from dataclasses import dataclass
import pygame
from ..constants import TILE_SIZE

@dataclass
class TileProperties:
    blocks_movement: bool = False
    blocks_sight: bool = False
    is_water: bool = False
    radiation_level: float = 0.0
    moisture_level: float = 0.0
    anomaly_type: Optional[str] = None
    danger_level: float = 0.0
    
class Tile:
    def __init__(self, terrain_type: str, properties: Optional[TileProperties] = None):
        self.terrain_type = terrain_type
        self.properties = properties or TileProperties()
        
    def make_walkable(self) -> None:
        """Make tile passable (for creating paths)"""
        self.properties.blocks_movement = False
        self.properties.blocks_sight = False
        
    def add_anomaly(self, anomaly_type: str, danger_level: float) -> None:
        """Add an anomaly to this tile"""
        self.properties.anomaly_type = anomaly_type
        self.properties.danger_level = danger_level
        
    def render(self, surface: pygame.Surface, x: int, y: int, 
               tile_size: int, light_level: float = 1.0) -> None:
        """Render tile with proper coloring based on properties"""
        # Base color from terrain type
        base_color = self._get_base_color()
        
        # Modify color based on properties
        if self.properties.is_water:
            base_color = self._blend_colors(base_color, (0, 0, 255), 0.3)
            
        if self.properties.radiation_level > 0:
            base_color = self._blend_colors(base_color, (0, 255, 0), 
                                          self.properties.radiation_level * 0.5)
            
        if self.properties.anomaly_type:
            anomaly_colors = {
                "thermal": (255, 100, 0),
                "gravity": (128, 0, 128),
                "chemical": (0, 255, 128),
                "electric": (255, 255, 0)
            }
            base_color = self._blend_colors(base_color, 
                                          anomaly_colors[self.properties.anomaly_type],
                                          self.properties.danger_level * 0.3)
            
        # Apply lighting
        final_color = tuple(int(c * light_level) for c in base_color)
        
        # Draw tile
        pygame.draw.rect(surface, final_color, 
                        (x * tile_size, y * tile_size, tile_size, tile_size))
        
    def _get_base_color(self) -> tuple:
        """Get base color for terrain type"""
        colors = {
            "floor": (100, 100, 100),
            "wall": (50, 50, 50),
            "water": (0, 0, 150),
            "radiation": (50, 100, 50)
        }
        return colors.get(self.terrain_type, (128, 128, 128))
        
    @staticmethod
    def _blend_colors(color1: tuple, color2: tuple, factor: float) -> tuple:
        """Blend two colors together"""
        return tuple(int(c1 * (1 - factor) + c2 * factor) 
                    for c1, c2 in zip(color1, color2))

# Tile definitions
TILE_PROPERTIES = {
    "floor": TileProperties(),
    "wall": TileProperties(blocks_movement=True, blocks_sight=True),
    "water": TileProperties(radiation_level=0.1),
    "deep_water": TileProperties(blocks_movement=True, radiation_level=0.3),
    "radiation": TileProperties(radiation_level=1.0),
    "rough": TileProperties(danger_level=0.2)
}

TILE_COLORS = {
    "floor": (100, 100, 100),
    "wall": (50, 50, 50),
    "water": (0, 0, 150),
    "deep_water": (0, 0, 100),
    "radiation": (0, 255, 0),
    "rough": (120, 100, 80)
}

ANOMALY_COLORS = {
    "thermal": (255, 100, 0),
    "gravity": (100, 0, 255),
    "chemical": (0, 255, 0),
    "electrical": (255, 255, 0)
} 
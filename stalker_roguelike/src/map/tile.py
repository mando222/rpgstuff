from typing import Dict, Optional
from dataclasses import dataclass
import pygame

@dataclass
class TileProperties:
    blocks_movement: bool = False
    blocks_sight: bool = False
    radiation_level: float = 0.0
    anomaly_type: Optional[str] = None
    danger_level: float = 0.0
    
class Tile:
    def __init__(self, tile_type: str):
        self.tile_type = tile_type
        self.explored = False
        self.visible = False
        self.properties = self._get_tile_properties(tile_type)
        self.items = []
        
    def _get_tile_properties(self, tile_type: str) -> TileProperties:
        return TILE_PROPERTIES.get(tile_type, TileProperties())
        
    def add_anomaly(self, anomaly_type: str, danger_level: float) -> None:
        self.properties.anomaly_type = anomaly_type
        self.properties.danger_level = danger_level
        
    def render(self, surface: pygame.Surface, x: int, y: int, tile_size: int,
              light_level: float) -> None:
        if not self.explored:
            return
            
        # Get base color
        color = TILE_COLORS[self.tile_type]
        
        # Apply lighting
        if not self.visible:
            # Explored but not visible tiles are darker
            color = tuple(max(0, c // 3) for c in color)
        else:
            # Apply current light level to visible tiles
            color = tuple(int(c * light_level) for c in color)
            
        pygame.draw.rect(surface, color, (x * tile_size, y * tile_size, tile_size, tile_size))
        
        # Draw anomaly effects if present and visible
        if self.properties.anomaly_type and self.visible:
            anomaly_color = ANOMALY_COLORS.get(self.properties.anomaly_type, (255, 0, 255))
            # Make anomaly color glow
            glow_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*anomaly_color, 128),
                             (tile_size//2, tile_size//2), tile_size//3)
            surface.blit(glow_surface, (x * tile_size, y * tile_size))

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
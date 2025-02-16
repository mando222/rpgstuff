from typing import Dict, Tuple, List
import pygame
from ..map.zone import Zone
from ..entities.player import Player

class Minimap:
    def __init__(self, size: int = 150, tile_size: int = 3):
        self.size = size
        self.tile_size = tile_size
        self.padding = 10
        self.surface = pygame.Surface((size, size))
        self.visible_range = size // tile_size
        
        # Colors for different elements
        self.colors = {
            "background": (0, 0, 0, 200),
            "border": (255, 255, 255),
            "player": (0, 255, 0),
            "enemy": (255, 0, 0),
            "wall": (128, 128, 128),
            "water": (0, 0, 150),
            "radiation": (0, 255, 0, 128),
            "anomaly": (255, 0, 255)
        }
        
    def render(self, surface: pygame.Surface, zone: Zone, player: Player) -> None:
        # Create transparent surface
        self.surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.surface.fill(self.colors["background"])
        
        # Calculate visible area
        half_range = self.visible_range // 2
        start_x = max(0, player.x - half_range)
        start_y = max(0, player.y - half_range)
        end_x = min(zone.width, start_x + self.visible_range)
        end_y = min(zone.height, start_y + self.visible_range)
        
        # Draw tiles
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                map_x = (x - start_x) * self.tile_size
                map_y = (y - start_y) * self.tile_size
                
                tile = zone.tiles[x][y]
                if not tile.explored:
                    continue
                    
                # Draw base tile
                color = self._get_tile_color(tile)
                pygame.draw.rect(self.surface, color,
                               (map_x, map_y, self.tile_size, self.tile_size))
                
                # Draw anomalies
                if tile.properties.anomaly_type:
                    pygame.draw.rect(self.surface, self.colors["anomaly"],
                                   (map_x, map_y, self.tile_size, self.tile_size))
                    
        # Draw entities
        for entity in zone.entities:
            if start_x <= entity.x < end_x and start_y <= entity.y < end_y:
                map_x = (entity.x - start_x) * self.tile_size
                map_y = (entity.y - start_y) * self.tile_size
                
                color = self.colors["player"] if isinstance(entity, Player) else self.colors["enemy"]
                pygame.draw.rect(self.surface, color,
                               (map_x, map_y, self.tile_size, self.tile_size))
                
        # Draw border
        pygame.draw.rect(self.surface, self.colors["border"], 
                        (0, 0, self.size, self.size), 1)
                        
        # Position minimap in top-right corner
        surface.blit(self.surface, 
                    (surface.get_width() - self.size - self.padding, self.padding))
        
    def _get_tile_color(self, tile) -> Tuple[int, int, int]:
        if tile.properties.blocks_movement:
            return self.colors["wall"]
        elif tile.properties.radiation_level > 0:
            return self.colors["radiation"]
        elif "water" in tile.tile_type:
            return self.colors["water"]
        return (50, 50, 50)  # Default floor color 
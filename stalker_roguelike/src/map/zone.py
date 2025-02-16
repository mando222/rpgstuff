from typing import List, Dict, Tuple, Optional
from .tile import Tile, TileProperties
import pygame
from ..constants import (
    TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
    TERRAIN_FLOOR, TERRAIN_WALL, TERRAIN_WATER  # Add terrain constants
)

class Zone:
    def __init__(self, width: int, height: int, zone_type: str):
        self.width = width
        self.height = height
        self.zone_type = zone_type
        self.game_state = None
        # Initialize with empty floor tiles
        self.tiles = [[Tile(TERRAIN_FLOOR, TileProperties()) 
                      for _ in range(height)] for _ in range(width)]
        self.entities = []
        self.items = []
        self.anomalies = []
        self.visible_tiles = [[False] * height for _ in range(width)]
        self.explored_tiles = [[False] * height for _ in range(width)]
        self.danger_level = 0
        self.radiation_level = 0
        self.connections: Dict[str, Tuple[int, int]] = {}  # Direction: (x, y)
        
    def is_walkable(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return not self.tiles[x][y].properties.blocks_movement
        
    def get_entities_at(self, x: int, y: int) -> List:
        return [e for e in self.entities if e.x == x and e.y == y]
        
    def get_items_at(self, x: int, y: int) -> List:
        return [i for i in self.items if i.x == x and i.y == y]
        
    def add_entity(self, entity) -> None:
        self.entities.append(entity)
        
    def remove_entity(self, entity) -> None:
        if entity in self.entities:
            self.entities.remove(entity)
            
    def add_anomaly(self, x: int, y: int, anomaly_type: str, danger_level: float) -> None:
        self.tiles[x][y].add_anomaly(anomaly_type, danger_level)
        self.anomalies.append({
            "x": x,
            "y": y,
            "type": anomaly_type,
            "danger": danger_level
        })
        
    def update(self) -> None:
        # Update entities
        for entity in self.entities:
            if hasattr(entity, "update"):
                entity.update()
                
        # Update anomalies
        self._update_anomalies()
        
    def _update_anomalies(self) -> None:
        for anomaly in self.anomalies:
            x, y = anomaly["x"], anomaly["y"]
            # Damage entities in anomaly
            for entity in self.get_entities_at(x, y):
                damage = anomaly["danger"] * 10
                entity.combat.apply_damage(damage, anomaly["type"], "torso")
                
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int], 
               light_level: float = 1.0) -> None:
        """Render the zone with fog of war and exploration"""
        view_width = SCREEN_WIDTH // TILE_SIZE + 2  # Add 1 tile buffer on each side
        view_height = SCREEN_HEIGHT // TILE_SIZE + 2
        
        start_x = max(0, int(camera_offset[0]) - 1)
        start_y = max(0, int(camera_offset[1]) - 1)
        
        # Render visible tiles
        for x in range(start_x, min(self.width, start_x + view_width)):
            for y in range(start_y, min(self.height, start_y + view_height)):
                screen_x = (x - camera_offset[0]) * TILE_SIZE
                screen_y = (y - camera_offset[1]) * TILE_SIZE
                
                # Skip if tile would be off screen
                if (screen_x < -TILE_SIZE or screen_x > SCREEN_WIDTH or 
                    screen_y < -TILE_SIZE or screen_y > SCREEN_HEIGHT):
                    continue
                
                if self.visible_tiles[x][y]:
                    # Render fully visible tile
                    self.tiles[x][y].render(surface, screen_x, screen_y, 
                                          TILE_SIZE, light_level)
                elif self.explored_tiles[x][y]:
                    # Render explored but not visible tile (darker)
                    self.tiles[x][y].render(surface, screen_x, screen_y, 
                                          TILE_SIZE, light_level * 0.5)
                    
        # Render entities in visible tiles
        for entity in self.entities:
            if (0 <= entity.x < self.width and 0 <= entity.y < self.height and
                self.visible_tiles[entity.x][entity.y]):
                entity.render(surface, camera_offset)
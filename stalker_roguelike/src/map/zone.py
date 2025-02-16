from typing import List, Dict, Tuple, Optional
from .tile import Tile
import pygame

class Zone:
    def __init__(self, width: int, height: int, zone_type: str):
        self.width = width
        self.height = height
        self.zone_type = zone_type
        self.tiles: List[List[Tile]] = []
        self.entities: List = []
        self.items: List = []
        self.anomalies: List[Dict] = []
        self.danger_level = 0
        self.radiation_level = 0
        self.connections: Dict[str, Tuple[int, int]] = {}  # Direction: (x, y)
        
    def initialize_tiles(self) -> None:
        self.tiles = [[Tile("floor") for y in range(self.height)]
                     for x in range(self.width)]
                     
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
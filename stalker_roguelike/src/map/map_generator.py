from typing import Dict, List, Tuple, Optional
import random
import noise
from .zone import Zone
from .tile import Tile
from ..entities.enemies import Enemy, ENEMY_TEMPLATES

class MapGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.zones: Dict[Tuple[int, int], Zone] = {}
        self.seed = random.randint(0, 1000000)
        
    def generate_zone(self, x: int, y: int, zone_type: str) -> Zone:
        zone = Zone(self.width, self.height, zone_type)
        zone.initialize_tiles()
        
        # Generate terrain using noise
        self._generate_terrain(zone)
        
        # Add anomalies
        self._add_anomalies(zone)
        
        # Add enemies
        self._populate_enemies(zone)
        
        # Add items
        self._add_items(zone)
        
        self.zones[(x, y)] = zone
        return zone
        
    def _generate_terrain(self, zone: Zone) -> None:
        # Use multiple noise layers for different features
        elevation = self._generate_noise_map(1.0)
        radiation = self._generate_noise_map(2.0)
        roughness = self._generate_noise_map(4.0)
        
        for x in range(zone.width):
            for y in range(zone.height):
                # Determine tile type based on noise values
                elev = elevation[x][y]
                rad = radiation[x][y]
                rough = roughness[x][y]
                
                if elev < 0.2:
                    tile_type = "deep_water"
                elif elev < 0.3:
                    tile_type = "water"
                elif rad > 0.7:
                    tile_type = "radiation"
                elif rough > 0.6:
                    tile_type = "rough"
                elif elev > 0.8:
                    tile_type = "wall"
                else:
                    tile_type = "floor"
                    
                zone.tiles[x][y] = Tile(tile_type)
                
    def _generate_noise_map(self, scale: float) -> List[List[float]]:
        noise_map = []
        for x in range(self.width):
            row = []
            for y in range(self.height):
                value = noise.pnoise3(x/scale/10, 
                                    y/scale/10, 
                                    self.seed,
                                    octaves=6,
                                    persistence=0.5,
                                    lacunarity=2.0)
                row.append((value + 1) / 2)  # Normalize to 0-1
            noise_map.append(row)
        return noise_map
        
    def _add_anomalies(self, zone: Zone) -> None:
        num_anomalies = random.randint(3, 8)
        anomaly_types = ["thermal", "gravity", "chemical", "electrical"]
        
        for _ in range(num_anomalies):
            x = random.randint(0, zone.width - 1)
            y = random.randint(0, zone.height - 1)
            
            if not zone.tiles[x][y].properties.blocks_movement:
                anomaly_type = random.choice(anomaly_types)
                danger_level = random.uniform(0.3, 1.0)
                zone.add_anomaly(x, y, anomaly_type, danger_level)
                
    def _populate_enemies(self, zone: Zone) -> None:
        num_enemies = random.randint(5, 12)
        enemy_types = list(ENEMY_TEMPLATES.keys())
        
        for _ in range(num_enemies):
            x = random.randint(0, zone.width - 1)
            y = random.randint(0, zone.height - 1)
            
            if not zone.tiles[x][y].properties.blocks_movement:
                enemy_type = random.choice(enemy_types)
                difficulty = random.uniform(0.8, 1.2)
                enemy = Enemy(x, y, "E", (255, 0, 0), enemy_type, difficulty)
                zone.add_entity(enemy)
                
    def _add_items(self, zone: Zone) -> None:
        # TODO: Implement item generation based on zone type and danger level
        pass 
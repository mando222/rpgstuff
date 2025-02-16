from typing import Dict, Tuple, List, Optional, Set
import random
import noise
from .zone import Zone
from .tile import Tile, TileProperties
from ..constants import (
    TERRAIN_FLOOR, TERRAIN_WALL, TERRAIN_WATER, TERRAIN_RADIATION,
    ENTITY_ANOMALY
)

class MapGenerator:
    def __init__(self, world_width: int, world_height: int):
        self.world_width = world_width
        self.world_height = world_height
        self.zones: Dict[Tuple[int, int], Zone] = {}
        self.seed = random.randint(0, 1000000)
        
        # Noise settings for different features
        self.elevation_scale = 50.0
        self.moisture_scale = 25.0
        self.radiation_scale = 75.0
        self.anomaly_scale = 100.0
        
    def generate_zone(self, zone_x: int, zone_y: int, zone_type: str) -> Zone:
        """Generate a new zone or return existing one"""
        if (zone_x, zone_y) in self.zones:
            return self.zones[(zone_x, zone_y)]
            
        # Create new zone
        zone = Zone(64, 64, zone_type)
        zone.game_state = self.game_state
        
        # Generate terrain based on zone type
        if zone_type == "wilderness":
            self._generate_wilderness(zone, zone_x, zone_y)
        elif zone_type == "forest":
            self._generate_forest(zone, zone_x, zone_y)
        elif zone_type == "underground":
            self._generate_underground(zone, zone_x, zone_y)
        else:
            self._generate_wilderness(zone, zone_x, zone_y)
            
        # Add enemies
        self._spawn_enemies(zone, zone_x, zone_y)
        
        # Add hazards and connect zones
        self._add_hazards(zone, zone_x, zone_y)
        self._connect_to_adjacent_zones(zone, zone_x, zone_y)
        
        self.zones[(zone_x, zone_y)] = zone
        return zone
        
    def _generate_wilderness(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Generate an open wilderness area with points of interest"""
        # Generate base terrain using noise
        self._generate_terrain_noise(zone, zone_x, zone_y)
        
        # Add points of interest
        self._add_points_of_interest(zone, zone_x, zone_y)
        
    def _generate_terrain_noise(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Generate natural terrain using multiple noise layers"""
        for x in range(zone.width):
            for y in range(zone.height):
                world_x = zone_x * zone.width + x
                world_y = zone_y * zone.height + y
                
                # Generate various noise values
                elevation = noise.pnoise2(
                    world_x / 50.0, 
                    world_y / 50.0, 
                    octaves=6,
                    persistence=0.5,
                    lacunarity=2.0,
                    base=self.seed
                )
                
                forest_density = noise.pnoise2(
                    world_x / 30.0,
                    world_y / 30.0,
                    octaves=3,
                    base=self.seed + 1
                )
                
                # Determine terrain type
                if elevation < -0.3:
                    # Water
                    zone.tiles[x][y] = Tile(TERRAIN_WATER, TileProperties(
                        is_water=True,
                        blocks_movement=True
                    ))
                elif elevation < -0.1:
                    # Swamp/marsh
                    zone.tiles[x][y] = Tile(TERRAIN_WATER, TileProperties(
                        is_water=True,
                        blocks_movement=False,
                        radiation_level=0.2
                    ))
                elif forest_density > 0.2:
                    # Forest
                    if random.random() < forest_density:
                        zone.tiles[x][y] = Tile(TERRAIN_WALL, TileProperties(
                            blocks_movement=True,
                            blocks_sight=True,
                            moisture_level=0.8
                        ))
                    else:
                        zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties())
                else:
                    # Open ground
                    zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties())
                    
    def _add_points_of_interest(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Add various points of interest to the wilderness"""
        # Use deterministic random based on zone coordinates
        rng = random.Random(hash((zone_x, zone_y, self.seed)))
        
        # Possible features to add
        features = [
            (self._add_small_village, 0.15),
            (self._add_military_outpost, 0.1),
            # Temporarily remove unimplemented features
            # (self._add_abandoned_factory, 0.1),
            # (self._add_research_facility, 0.05),
            (self._add_anomaly_field, 0.2),
            (self._add_crash_site, 0.1)
        ]
        
        for feature_func, probability in features:
            if rng.random() < probability:
                # Find suitable location
                attempts = 20
                while attempts > 0:
                    x = rng.randint(5, zone.width - 15)
                    y = rng.randint(5, zone.height - 15)
                    if self._is_suitable_location(zone, x, y, 10):
                        feature_func(zone, x, y, rng)
                        break
                    attempts -= 1
                    
    def _add_small_village(self, zone: Zone, x: int, y: int, rng: random.Random) -> None:
        """Add a small village with multiple buildings"""
        num_buildings = rng.randint(3, 7)
        
        # Create a road network
        self._create_village_roads(zone, x, y, 10)
        
        # Add buildings along roads
        for _ in range(num_buildings):
            bx = x + rng.randint(-5, 5)
            by = y + rng.randint(-5, 5)
            if self._is_suitable_location(zone, bx, by, 3):
                self._generate_building(zone, bx, by, rng.choice([
                    "house", "shop", "warehouse"
                ]))
                
    def _add_military_outpost(self, zone: Zone, x: int, y: int, rng: random.Random) -> None:
        """Add a military outpost with defensive structures"""
        # Create main building
        self._generate_building(zone, x, y, "military", 8, 12)
        
        # Add defensive walls
        self._create_defensive_perimeter(zone, x-2, y-2, 12, 16)
        
        # Add guard towers
        tower_positions = [(x-2, y-2), (x+8, y-2), (x-2, y+12), (x+8, y+12)]
        for tx, ty in tower_positions:
            self._generate_building(zone, tx, ty, "tower", 2, 2)
            
    def _is_suitable_location(self, zone: Zone, x: int, y: int, size: int) -> bool:
        """Check if an area is suitable for building (no water or existing structures)"""
        for dx in range(-1, size + 1):
            for dy in range(-1, size + 1):
                check_x = x + dx
                check_y = y + dy
                if not (0 <= check_x < zone.width and 0 <= check_y < zone.height):
                    return False
                tile = zone.tiles[check_x][check_y]
                if tile.properties.is_water or tile.properties.blocks_movement:
                    return False
        return True

    def _generate_rooms(self, zone: Zone) -> List[Dict]:
        """Generate a set of non-overlapping rooms"""
        rooms = []
        attempts = 0
        max_attempts = 100
        
        while len(rooms) < 15 and attempts < max_attempts:  # Try to place 15 rooms
            width = random.randint(6, 12)
            height = random.randint(6, 12)
            x = random.randint(1, zone.width - width - 1)
            y = random.randint(1, zone.height - height - 1)
            
            new_room = {"x": x, "y": y, "width": width, "height": height}
            
            # Check if room overlaps with existing rooms (including margin)
            margin = 2  # Space between rooms
            overlaps = any(self._rooms_overlap_with_margin(new_room, existing, margin) 
                         for existing in rooms)
            
            if not overlaps:
                self._create_room(zone, x, y, width, height)
                rooms.append(new_room)
            
            attempts += 1
            
        return rooms
        
    def _connect_rooms(self, zone: Zone, rooms: List[Dict]) -> None:
        """Connect rooms with corridors using minimum spanning tree"""
        if not rooms:
            return
            
        # Create a list of all possible connections
        connections = []
        for i, room1 in enumerate(rooms[:-1]):
            for j, room2 in enumerate(rooms[i+1:], i+1):
                center1 = (room1["x"] + room1["width"]//2, 
                          room1["y"] + room1["height"]//2)
                center2 = (room2["x"] + room2["width"]//2, 
                          room2["y"] + room2["height"]//2)
                distance = abs(center1[0] - center2[0]) + abs(center1[1] - center2[1])
                # Store tuple with distance and room indices
                connections.append((distance, (i, j)))
                
        # Sort connections by distance
        connections.sort(key=lambda x: x[0])
        
        # Create minimum spanning tree using room indices
        connected_indices = {0}  # Start with first room
        while len(connected_indices) < len(rooms):
            for distance, (i, j) in connections:
                if (i in connected_indices) != (j in connected_indices):
                    # Connect these rooms
                    room1, room2 = rooms[i], rooms[j]
                    self._create_l_corridor(zone,
                        room1["x"] + room1["width"]//2,
                        room1["y"] + room1["height"]//2,
                        room2["x"] + room2["width"]//2,
                        room2["y"] + room2["height"]//2
                    )
                    connected_indices.add(i)
                    connected_indices.add(j)
                    break
                    
        # Add a few extra connections for loops
        for _ in range(len(rooms) // 3):
            i = random.randrange(len(rooms))
            j = random.randrange(len(rooms))
            if i != j:
                room1, room2 = rooms[i], rooms[j]
                self._create_l_corridor(zone,
                    room1["x"] + room1["width"]//2,
                    room1["y"] + room1["height"]//2,
                    room2["x"] + room2["width"]//2,
                    room2["y"] + room2["height"]//2
                )
                
    def _create_l_corridor(self, zone: Zone, x1: int, y1: int, x2: int, y2: int) -> None:
        """Create an L-shaped corridor between two points"""
        # Randomly choose which direction to go first
        if random.random() < 0.5:
            # First horizontal, then vertical
            self._create_horizontal_corridor(zone, x1, x2, y1)
            self._create_vertical_corridor(zone, y1, y2, x2)
        else:
            # First vertical, then horizontal
            self._create_vertical_corridor(zone, y1, y2, x1)
            self._create_horizontal_corridor(zone, x1, x2, y2)
            
    def _ensure_connectivity(self, zone: Zone) -> None:
        """Ensure all floor tiles are reachable"""
        # Find a starting floor tile
        start = None
        for x in range(zone.width):
            for y in range(zone.height):
                if not zone.tiles[x][y].properties.blocks_movement:
                    start = (x, y)
                    break
            if start:
                break
                
        if not start:
            return
            
        # Do a flood fill from start
        reachable = self._flood_fill(zone, start[0], start[1])
        
        # Make all unreachable floor tiles into walls
        for x in range(zone.width):
            for y in range(zone.height):
                if (not zone.tiles[x][y].properties.blocks_movement and 
                    (x, y) not in reachable):
                    zone.tiles[x][y] = Tile(TERRAIN_WALL, TileProperties(
                        blocks_movement=True,
                        blocks_sight=True
                    ))
                    
    def _flood_fill(self, zone: Zone, start_x: int, start_y: int) -> Set[Tuple[int, int]]:
        """Return set of all reachable floor tiles from start position"""
        reachable = set()
        to_check = [(start_x, start_y)]
        
        while to_check:
            x, y = to_check.pop()
            if (x, y) not in reachable:
                reachable.add((x, y))
                # Check adjacent tiles
                for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < zone.width and 
                        0 <= new_y < zone.height and
                        not zone.tiles[new_x][new_y].properties.blocks_movement):
                        to_check.append((new_x, new_y))
                        
        return reachable

    def _create_room(self, zone: Zone, x: int, y: int, width: int, height: int) -> None:
        """Create a rectangular room."""
        for i in range(x, x + width):
            for j in range(y, y + height):
                zone.tiles[i][j] = Tile(TERRAIN_FLOOR, TileProperties())

    def _create_horizontal_corridor(self, zone: Zone, x1: int, x2: int, y: int) -> None:
        """Create a horizontal corridor between two points."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties())

    def _create_vertical_corridor(self, zone: Zone, y1: int, y2: int, x: int) -> None:
        """Create a vertical corridor between two points."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties())

    def _rooms_overlap(self, room1: dict, room2: dict) -> bool:
        """Check if two rooms overlap."""
        return not (
            room1["x"] + room1["width"] < room2["x"] or
            room2["x"] + room2["width"] < room1["x"] or
            room1["y"] + room1["height"] < room2["y"] or
            room2["y"] + room2["height"] < room1["y"]
        )

    def _rooms_overlap_with_margin(self, room1: dict, room2: dict, margin: int) -> bool:
        """Check if two rooms overlap with a given margin."""
        return not (
            room1["x"] + room1["width"] + margin < room2["x"] or
            room2["x"] + room2["width"] + margin < room1["x"] or
            room1["y"] + room1["height"] + margin < room2["y"] or
            room2["y"] + room2["height"] + margin < room1["y"]
        )

    def _add_zone_features(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Add features based on zone type and location."""
        # Add some noise-based features
        for x in range(zone.width):
            for y in range(zone.height):
                if zone.tiles[x][y].terrain_type == TERRAIN_FLOOR:
                    # World coordinates for consistent noise
                    world_x = zone_x * zone.width + x
                    world_y = zone_y * zone.height + y
                    
                    # Water features
                    if noise.pnoise2(world_x/20, world_y/20, base=self.seed) > 0.3:
                        zone.tiles[x][y] = Tile(TERRAIN_WATER, TileProperties(
                            is_water=True,
                            blocks_movement=False
                        ))

    def _add_hazards(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Add radiation zones and anomalies"""
        for x in range(zone.width):
            for y in range(zone.height):
                world_x = zone_x * zone.width + x
                world_y = zone_y * zone.height + y
                
                # Generate radiation levels
                radiation = noise.pnoise2(
                    world_x / self.radiation_scale,
                    world_y / self.radiation_scale,
                    octaves=3,
                    base=self.seed + 2
                )
                
                if radiation > 0.3:
                    zone.tiles[x][y].properties.radiation_level = (radiation - 0.3) * 2
                    
                # Generate anomalies
                anomaly = noise.pnoise2(
                    world_x / self.anomaly_scale,
                    world_y / self.anomaly_scale,
                    octaves=2,
                    base=self.seed + 3
                )
                
                if anomaly > 0.6 and not zone.tiles[x][y].properties.blocks_movement:
                    anomaly_types = ["thermal", "gravity", "chemical", "electric"]
                    zone.add_anomaly(x, y, random.choice(anomaly_types), 
                                   (anomaly - 0.6) * 3)
                    
    def _connect_to_adjacent_zones(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Create paths between adjacent zones"""
        # Check each adjacent zone
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            adjacent_pos = (zone_x + dx, zone_y + dy)
            if adjacent_pos in self.zones:
                adjacent = self.zones[adjacent_pos]
                self._create_connection(zone, adjacent, dx, dy)
                
    def _create_connection(self, zone1: Zone, zone2: Zone, dx: int, dy: int) -> None:
        """Create a path between two zones"""
        if dx == -1:  # Connect on left edge
            x1, x2 = 0, zone1.width-1
            y = random.randint(10, zone1.height-10)
            
            # Clear path in both zones
            for x in range(5):
                zone1.tiles[x][y].make_walkable()
                zone2.tiles[x2-x][y].make_walkable()
                
            # Store connection points
            zone1.connections["west"] = (0, y)
            zone2.connections["east"] = (x2, y)
            
        elif dx == 1:  # Connect on right edge
            # Similar to left edge...
            pass
            
        # Similar for dy connections... 

    def _add_forest_features(self, zone: Zone) -> None:
        """Add forest-specific features like trees and vegetation"""
        for x in range(zone.width):
            for y in range(zone.height):
                # Skip water and walls
                if zone.tiles[x][y].properties.is_water or zone.tiles[x][y].properties.blocks_movement:
                    continue
                    
                # Add trees (as walls) with some randomness
                if random.random() < 0.2:  # 20% chance for a tree
                    zone.tiles[x][y] = Tile(TERRAIN_WALL, TileProperties(
                        blocks_movement=True,
                        blocks_sight=True,
                        moisture_level=0.8  # Trees increase moisture
                    ))
                    
    def _add_swamp_features(self, zone: Zone) -> None:
        """Add swamp-specific features like water and mud"""
        for x in range(zone.width):
            for y in range(zone.height):
                if zone.tiles[x][y].properties.blocks_movement:
                    continue
                    
                # Add water patches
                if random.random() < 0.3:  # 30% chance for water
                    zone.tiles[x][y] = Tile(TERRAIN_WATER, TileProperties(
                        is_water=True,
                        radiation_level=0.1,  # Swamp water is slightly radioactive
                        moisture_level=1.0
                    ))
                    
    def _add_urban_features(self, zone: Zone) -> None:
        """Add urban-specific features like buildings and roads"""
        # Create a grid of buildings
        for x in range(2, zone.width - 2, 8):
            for y in range(2, zone.height - 2, 8):
                if random.random() < 0.7:  # 70% chance for a building
                    self._generate_building(zone, x, y)
                    
        # Add roads between buildings
        self._generate_roads(zone)
        
    def _add_underground_features(self, zone: Zone) -> None:
        """Add underground-specific features like tunnels and caves"""
        # Start with all walls
        for x in range(zone.width):
            for y in range(zone.height):
                zone.tiles[x][y] = Tile(TERRAIN_WALL, TileProperties(
                    blocks_movement=True,
                    blocks_sight=True
                ))
                
        # Carve out tunnels using drunkard's walk
        self._generate_tunnels(zone)
        
    def _generate_building(self, zone: Zone, x: int, y: int, building_type: str,
                          width: Optional[int] = None, height: Optional[int] = None) -> None:
        """Generate a building with realistic floor plan"""
        if width is None:
            width = random.randint(8, 12)  # Larger buildings for more rooms
        if height is None:
            height = random.randint(8, 12)
            
        # Create outer walls
        for bx in range(x, x + width):
            for by in range(y, y + height):
                is_wall = (bx == x or bx == x + width - 1 or
                          by == y or by == y + height - 1)
                if is_wall:
                    zone.tiles[bx][by] = Tile(TERRAIN_WALL, TileProperties(
                        blocks_movement=True,
                        blocks_sight=True
                    ))
                else:
                    zone.tiles[bx][by] = Tile(TERRAIN_FLOOR, TileProperties())
                    
        # Add interior walls and rooms
        self._generate_interior_layout(zone, x, y, width, height, building_type)
        
    def _generate_interior_layout(self, zone: Zone, x: int, y: int, 
                                width: int, height: int, building_type: str) -> None:
        """Generate interior layout with rooms and hallways"""
        # Create a grid for room placement
        grid_size = 4  # Size of each grid cell
        grid_width = (width - 2) // grid_size
        grid_height = (height - 2) // grid_size
        
        # Create central hallway
        hallway_x = x + width // 2
        for hy in range(y + 1, y + height - 1):
            zone.tiles[hallway_x][hy] = Tile(TERRAIN_FLOOR, TileProperties())
            
        # Add rooms on both sides of hallway
        for side in [-1, 1]:  # Left and right of hallway
            room_x = hallway_x + (side * 2)  # Start 2 tiles from hallway
            for room_y in range(y + 2, y + height - 3, 4):
                if random.random() < 0.8:  # 80% chance for room
                    # Create room
                    room_width = random.randint(3, 4)
                    room_height = random.randint(3, 4)
                    
                    # Adjust room position based on side
                    if side < 0:
                        room_x = max(x + 1, hallway_x - room_width - 1)
                    else:
                        room_x = min(x + width - room_width - 1, hallway_x + 2)
                        
                    # Add walls
                    self._create_room_with_door(zone, room_x, room_y, 
                                              room_width, room_height,
                                              hallway_x, building_type)
                    
    def _create_room_with_door(self, zone: Zone, x: int, y: int, width: int, height: int,
                              hallway_x: int, building_type: str) -> None:
        """Create a room with walls and a door connecting to hallway"""
        # Create room walls
        for rx in range(x, x + width):
            for ry in range(y, y + height):
                is_wall = (rx == x or rx == x + width - 1 or
                          ry == y or ry == y + height - 1)
                if is_wall:
                    zone.tiles[rx][ry] = Tile(TERRAIN_WALL, TileProperties(
                        blocks_movement=True,
                        blocks_sight=True
                    ))
                    
        # Add door connecting to hallway
        door_y = y + height // 2
        if x < hallway_x:  # Room is left of hallway
            door_x = x + width - 1
        else:  # Room is right of hallway
            door_x = x
            
        # Create door and path to hallway
        zone.tiles[door_x][door_y] = Tile(TERRAIN_FLOOR, TileProperties())
        
        # Add room-specific features
        self._add_room_features(zone, x, y, width, height, building_type)
        
    def _add_room_features(self, zone: Zone, x: int, y: int, width: int, height: int,
                          building_type: str) -> None:
        """Add features specific to room type"""
        if building_type == "house":
            if random.random() < 0.3:  # Bedroom
                # Add bed
                bed_x = x + 1
                bed_y = y + 1
                zone.tiles[bed_x][bed_y].add_furniture("bed")
                zone.tiles[bed_x + 1][bed_y].add_furniture("bed")
            elif random.random() < 0.3:  # Kitchen
                # Add counter
                for cx in range(x + 1, x + width - 1):
                    zone.tiles[cx][y + 1].add_furniture("counter")
                    
        elif building_type == "military":
            if random.random() < 0.4:  # Barracks
                # Add beds
                for bx in range(x + 1, x + width - 1, 2):
                    zone.tiles[bx][y + 1].add_furniture("bed")
            elif random.random() < 0.3:  # Armory
                # Add weapon racks
                for wx in range(x + 1, x + width - 1):
                    zone.tiles[wx][y + 1].add_furniture("weapon_rack")

    def _generate_roads(self, zone: Zone) -> None:
        """Generate roads connecting buildings"""
        # Simple grid-based roads
        for x in range(0, zone.width, 8):
            for y in range(zone.height):
                if not zone.tiles[x][y].properties.blocks_movement:
                    zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties(
                        blocks_movement=False,
                        blocks_sight=False
                    ))
                    
        for y in range(0, zone.height, 8):
            for x in range(zone.width):
                if not zone.tiles[x][y].properties.blocks_movement:
                    zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties(
                        blocks_movement=False,
                        blocks_sight=False
                    ))
                    
    def _generate_tunnels(self, zone: Zone) -> None:
        """Generate underground tunnels using drunkard's walk"""
        num_walks = zone.width * zone.height // 50
        for _ in range(num_walks):
            x = random.randint(0, zone.width - 1)
            y = random.randint(0, zone.height - 1)
            
            # Perform random walk
            for _ in range(50):
                zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties())
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
                x = max(1, min(zone.width - 2, x + dx))
                y = max(1, min(zone.height - 2, y + dy))

    def _add_anomaly_field(self, zone: Zone, x: int, y: int, rng: random.Random) -> None:
        """Add a cluster of anomalies"""
        anomaly_types = ["thermal", "gravity", "chemical", "electric"]
        num_anomalies = rng.randint(3, 8)
        
        for _ in range(num_anomalies):
            ax = x + rng.randint(-3, 3)
            ay = y + rng.randint(-3, 3)
            if 0 <= ax < zone.width and 0 <= ay < zone.height:
                anomaly_type = rng.choice(anomaly_types)
                danger_level = rng.uniform(0.3, 1.0)
                zone.add_anomaly(ax, ay, anomaly_type, danger_level)

    def _add_crash_site(self, zone: Zone, x: int, y: int, rng: random.Random) -> None:
        """Add a crashed helicopter or vehicle with debris"""
        # Create central wreckage
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) <= 3:  # Diamond shape
                    wx = x + dx
                    wy = y + dy
                    if 0 <= wx < zone.width and 0 <= wy < zone.height:
                        # Add debris and radiation
                        zone.tiles[wx][wy] = Tile(TERRAIN_WALL, TileProperties(
                            blocks_movement=True,
                            blocks_sight=False,
                            radiation_level=0.3
                        ))
        
        # Add scattered debris
        for _ in range(rng.randint(4, 8)):
            dx = rng.randint(-5, 5)
            dy = rng.randint(-5, 5)
            debris_x = x + dx
            debris_y = y + dy
            if 0 <= debris_x < zone.width and 0 <= debris_y < zone.height:
                zone.tiles[debris_x][debris_y] = Tile(TERRAIN_WALL, TileProperties(
                    blocks_movement=True,
                    blocks_sight=False
                ))

    def _generate_forest(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Generate a forest zone"""
        # Start with basic terrain
        self._generate_terrain_noise(zone, zone_x, zone_y)
        
        # Add more trees
        for x in range(zone.width):
            for y in range(zone.height):
                if (not zone.tiles[x][y].properties.blocks_movement and
                    not zone.tiles[x][y].properties.is_water):
                    if random.random() < 0.3:  # 30% chance for trees
                        zone.tiles[x][y] = Tile(TERRAIN_WALL, TileProperties(
                            blocks_movement=True,
                            blocks_sight=True,
                            moisture_level=0.8
                        ))
                        
        # Add forest clearings and paths
        self._add_forest_clearings(zone)
        self._add_forest_paths(zone)
        
    def _generate_underground(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Generate an underground zone with tunnels and caves"""
        # Fill with walls
        for x in range(zone.width):
            for y in range(zone.height):
                zone.tiles[x][y] = Tile(TERRAIN_WALL, TileProperties(
                    blocks_movement=True,
                    blocks_sight=True
                ))
                
        # Generate cave system
        self._generate_tunnels(zone)
        
        # Add some rooms
        rooms = self._generate_rooms(zone)
        self._connect_rooms(zone, rooms)
        
    def _add_forest_clearings(self, zone: Zone) -> None:
        """Add some clearings in the forest"""
        num_clearings = random.randint(2, 4)
        for _ in range(num_clearings):
            x = random.randint(5, zone.width - 10)
            y = random.randint(5, zone.height - 10)
            radius = random.randint(3, 6)
            
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx*dx + dy*dy <= radius*radius:
                        clear_x = x + dx
                        clear_y = y + dy
                        if (0 <= clear_x < zone.width and 
                            0 <= clear_y < zone.height):
                            zone.tiles[clear_x][clear_y] = Tile(
                                TERRAIN_FLOOR, 
                                TileProperties()
                            )
                            
    def _add_forest_paths(self, zone: Zone) -> None:
        """Add winding paths through the forest"""
        # Create a few random paths
        num_paths = random.randint(2, 4)
        for _ in range(num_paths):
            # Start from edge
            if random.random() < 0.5:
                x = random.choice([0, zone.width - 1])
                y = random.randint(0, zone.height - 1)
            else:
                x = random.randint(0, zone.width - 1)
                y = random.choice([0, zone.height - 1])
                
            # Winding path
            for _ in range(50):
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.tiles[x][y] = Tile(TERRAIN_FLOOR, TileProperties())
                    # Random direction with tendency toward center
                    dx = random.choice([-1, 0, 1])
                    dy = random.choice([-1, 0, 1])
                    if x < zone.width // 2:
                        dx += random.choice([0, 1])
                    else:
                        dx += random.choice([-1, 0])
                    if y < zone.height // 2:
                        dy += random.choice([0, 1])
                    else:
                        dy += random.choice([-1, 0])
                    x = max(0, min(zone.width - 1, x + dx))
                    y = max(0, min(zone.height - 1, y + dy))

    def _spawn_enemies(self, zone: Zone, zone_x: int, zone_y: int) -> None:
        """Spawn enemies in the zone"""
        from ..entities.enemies import Enemy  # Import here to avoid circular imports
        
        # Use deterministic random based on zone coordinates
        rng = random.Random(hash((zone_x, zone_y, self.seed + 1)))
        
        # Define enemy types and spawn chances for each zone type
        spawn_tables = {
            "wilderness": [
                ("bandit", 0.3),
                ("mutant", 0.4),
                ("zombie", 0.2)
            ],
            "forest": [
                ("mutant", 0.5),
                ("zombie", 0.3)
            ],
            "underground": [
                ("zombie", 0.4),
                ("mutant", 0.3)
            ]
        }
        
        # Get spawn table for this zone type
        spawns = spawn_tables.get(zone.zone_type, [])
        
        # Determine number of enemies to spawn
        num_enemies = rng.randint(3, 8)
        
        # Try to spawn enemies
        for _ in range(num_enemies):
            if spawns:
                enemy_type, chance = rng.choice(spawns)
                if rng.random() < chance:
                    # Find valid spawn location
                    for _ in range(20):  # Try 20 times to find spot
                        x = rng.randint(5, zone.width - 5)
                        y = rng.randint(5, zone.height - 5)
                        if zone.is_walkable(x, y):
                            # Create enemy
                            enemy = Enemy(x, y, "E", (255, 0, 0), enemy_type)
                            enemy.game_state = zone.game_state
                            zone.add_entity(enemy)
                            break 

    def _create_village_roads(self, zone: Zone, center_x: int, center_y: int, size: int) -> None:
        """Create a simple road network for a village"""
        # Create main road (horizontal)
        for x in range(center_x - size, center_x + size):
            if 0 <= x < zone.width and 0 <= center_y < zone.height:
                zone.tiles[x][center_y] = Tile(TERRAIN_FLOOR, TileProperties(
                    blocks_movement=False,
                    blocks_sight=False
                ))
                
        # Create cross road (vertical)
        for y in range(center_y - size, center_y + size):
            if 0 <= center_x < zone.width and 0 <= y < zone.height:
                zone.tiles[center_x][y] = Tile(TERRAIN_FLOOR, TileProperties(
                    blocks_movement=False,
                    blocks_sight=False
                ))
                
        # Add some smaller side roads
        for _ in range(3):  # Add 3 side roads
            # Choose random points along main roads
            if random.random() < 0.5:
                # Horizontal side road
                x = center_x + random.randint(-size+2, size-2)
                y = center_y + random.choice([-size//2, size//2])
                length = random.randint(3, 6)
                
                for dy in range(length):
                    road_y = y + dy if y < center_y else y - dy
                    if 0 <= x < zone.width and 0 <= road_y < zone.height:
                        zone.tiles[x][road_y] = Tile(TERRAIN_FLOOR, TileProperties(
                            blocks_movement=False,
                            blocks_sight=False
                        ))
            else:
                # Vertical side road
                x = center_x + random.choice([-size//2, size//2])
                y = center_y + random.randint(-size+2, size-2)
                length = random.randint(3, 6)
                
                for dx in range(length):
                    road_x = x + dx if x < center_x else x - dx
                    if 0 <= road_x < zone.width and 0 <= y < zone.height:
                        zone.tiles[road_x][y] = Tile(TERRAIN_FLOOR, TileProperties(
                            blocks_movement=False,
                            blocks_sight=False
                        )) 
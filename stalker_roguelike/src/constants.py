import os

# Asset paths
ASSETS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
SOUND_EFFECTS_PATH = os.path.join(ASSETS_PATH, "sounds", "effects")
MUSIC_PATH = os.path.join(ASSETS_PATH, "sounds", "music") 

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32
TITLE = "STALKER Roguelike"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Directions
DIRECTIONS = [
    (0, -1),  # North
    (1, -1),  # Northeast
    (1, 0),   # East
    (1, 1),   # Southeast
    (0, 1),   # South
    (-1, 1),  # Southwest
    (-1, 0),  # West
    (-1, -1)  # Northwest
]

# Entity types
ENTITY_PLAYER = "player"
ENTITY_ENEMY = "enemy"
ENTITY_ITEM = "item"
ENTITY_ANOMALY = "anomaly"

# Item types
ITEM_WEAPON = "weapon"
ITEM_ARMOR = "armor"
ITEM_CONSUMABLE = "consumable"
ITEM_ARTIFACT = "artifact"

# Terrain types
TERRAIN_FLOOR = "floor"
TERRAIN_WALL = "wall"
TERRAIN_WATER = "water"
TERRAIN_RADIATION = "radiation"

# Game settings
FPS = 60
PLAYER_START_HEALTH = 100
PLAYER_START_STAMINA = 100

from enum import Enum
from typing import Dict, List

class SoundEffects(Enum):
    # Combat sounds
    GUNSHOT = "gunshot"
    RELOAD = "reload"
    MELEE_SWING = "melee_swing"
    MELEE_HIT = "melee_hit"
    BULLET_IMPACT = "bullet_impact"
    
    # Player sounds
    FOOTSTEP = "footstep"
    JUMP = "jump"
    HURT = "hurt"
    HEAL = "heal"
    ITEM_PICKUP = "item_pickup"
    INVENTORY_OPEN = "inventory_open"
    
    # Environment sounds
    ANOMALY_THERMAL = "anomaly_thermal"
    ANOMALY_GRAVITY = "anomaly_gravity"
    ANOMALY_CHEMICAL = "anomaly_chemical"
    RADIATION_GEIGER = "radiation_geiger"
    THUNDER = "thunder"
    RAIN = "rain"
    WIND = "wind"
    
    # UI sounds
    MENU_SELECT = "menu_select"
    MENU_CONFIRM = "menu_confirm"
    MENU_BACK = "menu_back"
    QUEST_COMPLETE = "quest_complete"
    LEVEL_UP = "level_up"

class MusicTracks(Enum):
    MAIN_MENU = "main_menu"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    AMBIENT_FOREST = "ambient_forest"
    AMBIENT_UNDERGROUND = "ambient_underground"
    AMBIENT_STORM = "ambient_storm"

# Sound variations for more variety
FOOTSTEP_VARIATIONS: Dict[str, List[str]] = {
    "concrete": ["footstep_concrete_1", "footstep_concrete_2", "footstep_concrete_3"],
    "grass": ["footstep_grass_1", "footstep_grass_2", "footstep_grass_3"],
    "water": ["footstep_water_1", "footstep_water_2", "footstep_water_3"],
    "metal": ["footstep_metal_1", "footstep_metal_2", "footstep_metal_3"]
}

WEAPON_SOUNDS: Dict[str, Dict[str, str]] = {
    "ak74": {
        "fire": "ak74_fire",
        "reload": "ak74_reload",
        "empty": "ak74_empty"
    },
    "pistol": {
        "fire": "pistol_fire",
        "reload": "pistol_reload",
        "empty": "pistol_empty"
    }
} 
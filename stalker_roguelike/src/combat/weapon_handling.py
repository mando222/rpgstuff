from typing import Optional
import random
from ..items.weapons import Weapon
from ..audio.sound_effects import WEAPON_SOUNDS

class WeaponHandling:
    @staticmethod
    def handle_weapon_fire(weapon: Weapon, sound_manager) -> bool:
        """Handle weapon firing mechanics including jamming and sounds"""
        
        if weapon.current_ammo <= 0:
            # Play empty click sound
            if weapon.name.lower() in WEAPON_SOUNDS:
                sound_manager.play_sound(WEAPON_SOUNDS[weapon.name.lower()]["empty"])
            return False
            
        # Check for jam based on weapon condition
        if WeaponHandling._check_weapon_jam(weapon):
            return False
            
        # Fire the weapon
        weapon.current_ammo -= 1
        weapon.stats.condition -= 0.1  # Slight wear from firing
        
        # Play appropriate sound
        if weapon.name.lower() in WEAPON_SOUNDS:
            sound_manager.play_sound(WEAPON_SOUNDS[weapon.name.lower()]["fire"])
        else:
            sound_manager.play_sound("gunshot")  # Generic fallback
            
        return True
        
    @staticmethod
    def handle_reload(weapon: Weapon, ammo_count: int, sound_manager) -> int:
        """Handle weapon reloading mechanics and sounds"""
        
        if weapon.name.lower() in WEAPON_SOUNDS:
            sound_manager.play_sound(WEAPON_SOUNDS[weapon.name.lower()]["reload"])
        else:
            sound_manager.play_sound("reload")  # Generic fallback
            
        return weapon.reload(ammo_count)
        
    @staticmethod
    def _check_weapon_jam(weapon: Weapon) -> bool:
        # Base jam chance increases as condition decreases
        base_jam_chance = weapon.jam_chance + (1.0 - weapon.stats.condition / 100.0) * 0.1
        
        # Additional factors could be added (weather, ammo quality, etc.)
        
        return random.random() < base_jam_chance 
from typing import Dict, Optional
import pygame
import os
from enum import Enum
from ..constants import SOUND_EFFECTS_PATH, MUSIC_PATH

class SoundType(Enum):
    AMBIENT = "ambient"
    EFFECT = "effect"
    MUSIC = "music"

class SoundManager:
    def __init__(self):
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.music_tracks: Dict[str, str] = {}
        self.current_music = None
        self.sound_enabled = True
        self.music_enabled = True
        
        # Initialize mixer
        pygame.mixer.init()
        
        # Create directories if they don't exist
        os.makedirs(SOUND_EFFECTS_PATH, exist_ok=True)
        os.makedirs(MUSIC_PATH, exist_ok=True)
        
        self._load_sounds()
        
    def _load_sounds(self) -> None:
        """Load all sound effects from the assets directory"""
        try:
            for filename in os.listdir(SOUND_EFFECTS_PATH):
                if filename.endswith('.wav') or filename.endswith('.ogg'):
                    sound_name = os.path.splitext(filename)[0]
                    try:
                        self.sounds[sound_name] = pygame.mixer.Sound(
                            os.path.join(SOUND_EFFECTS_PATH, filename)
                        )
                    except pygame.error:
                        print(f"Warning: Could not load sound {filename}")
                        self.sounds[sound_name] = None
        except FileNotFoundError:
            print("Warning: Sound effects directory not found")
            
    def play_sound(self, sound_name: str) -> None:
        """Play a sound effect if it exists and sound is enabled"""
        if self.sound_enabled and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()
            
    def play_music(self, track_name: str, loop: bool = True) -> None:
        """Play a music track if it exists and music is enabled"""
        if not self.music_enabled:
            return
            
        if track_name != self.current_music:
            self.current_music = track_name
            try:
                pygame.mixer.music.load(os.path.join(MUSIC_PATH, f"{track_name}.ogg"))
                pygame.mixer.music.play(-1 if loop else 0)
            except pygame.error:
                print(f"Warning: Could not load music track {track_name}")
                
    def stop_music(self) -> None:
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
        self.current_music = None
        
    def toggle_sound(self) -> None:
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
        
    def toggle_music(self) -> None:
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        
    def play_ambient(self, ambient_id: str, fade_ms: int = 1000) -> None:
        if ambient_id in self.sounds and ambient_id != self.current_music:
            self.sounds[ambient_id].set_volume(0.3)
            self.sounds[ambient_id].play()
            self.current_music = ambient_id
            
    def stop_ambient(self, fade_ms: int = 1000) -> None:
        for sound_id, sound in self.sounds.items():
            if sound_id != self.current_music:
                sound.set_volume(0.0)
        self.current_music = None
        
    def set_music_volume(self, volume: float) -> None:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        
    def set_effects_volume(self, volume: float) -> None:
        for sound_id, sound in self.sounds.items():
            if sound:
                sound.set_volume(max(0.0, min(1.0, volume)))
            
    def set_ambient_volume(self, volume: float) -> None:
        for sound_id, sound in self.sounds.items():
            if sound_id != self.current_music:
                sound.set_volume(max(0.0, min(1.0, volume))) 
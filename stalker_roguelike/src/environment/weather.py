from enum import Enum
from typing import Dict, Optional
import random
from dataclasses import dataclass

class WeatherType(Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    RADIATION_STORM = "radiation_storm"
    ANOMALY_SURGE = "anomaly_surge"

@dataclass
class WeatherEffects:
    visibility: float = 1.0  # Multiplier for view distance
    accuracy: float = 1.0    # Multiplier for weapon accuracy
    noise_level: float = 1.0 # Affects stealth
    radiation: float = 0.0   # Additional radiation damage
    anomaly_strength: float = 1.0  # Multiplier for anomaly damage
    movement_speed: float = 1.0    # Movement speed modifier

class WeatherSystem:
    def __init__(self, sound_manager):
        self.current_weather = WeatherType.CLEAR
        self.weather_intensity = 0.0  # 0.0 to 1.0
        self.transition_time = 0
        self.sound_manager = sound_manager
        
        self.weather_effects = {
            WeatherType.CLEAR: WeatherEffects(),
            WeatherType.CLOUDY: WeatherEffects(
                visibility=0.8,
                accuracy=0.9
            ),
            WeatherType.RAIN: WeatherEffects(
                visibility=0.6,
                accuracy=0.7,
                noise_level=0.5,
                movement_speed=0.9
            ),
            WeatherType.STORM: WeatherEffects(
                visibility=0.4,
                accuracy=0.5,
                noise_level=0.2,
                movement_speed=0.8,
                anomaly_strength=1.2
            ),
            WeatherType.RADIATION_STORM: WeatherEffects(
                visibility=0.5,
                accuracy=0.6,
                radiation=0.5,
                anomaly_strength=1.5
            ),
            WeatherType.ANOMALY_SURGE: WeatherEffects(
                visibility=0.7,
                anomaly_strength=2.0,
                radiation=0.3
            )
        }
        
        # Weather transition probabilities
        self.weather_transitions = {
            WeatherType.CLEAR: {
                WeatherType.CLOUDY: 0.3,
                WeatherType.RADIATION_STORM: 0.05
            },
            WeatherType.CLOUDY: {
                WeatherType.CLEAR: 0.3,
                WeatherType.RAIN: 0.4,
                WeatherType.RADIATION_STORM: 0.1
            },
            WeatherType.RAIN: {
                WeatherType.CLOUDY: 0.4,
                WeatherType.STORM: 0.3
            },
            WeatherType.STORM: {
                WeatherType.RAIN: 0.5,
                WeatherType.ANOMALY_SURGE: 0.2
            }
        }
        
    def update(self, game_time: int) -> None:
        # Update weather every 5 minutes of game time
        if game_time % 300 == 0:
            self._update_weather()
            
        # Update weather intensity
        if self.transition_time > 0:
            self.transition_time -= 1
            self.weather_intensity = min(1.0, self.weather_intensity + 0.1)
        
        # Update weather effects
        self._apply_weather_effects()
        
    def _update_weather(self) -> None:
        # Check for weather transition
        if random.random() < 0.2:  # 20% chance to change weather
            possible_transitions = self.weather_transitions.get(self.current_weather, {})
            if possible_transitions:
                # Choose new weather based on transition probabilities
                total_prob = sum(possible_transitions.values())
                roll = random.random() * total_prob
                
                cumulative = 0
                for weather, prob in possible_transitions.items():
                    cumulative += prob
                    if roll <= cumulative:
                        self._transition_to_weather(weather)
                        break
                        
    def _transition_to_weather(self, new_weather: WeatherType) -> None:
        self.current_weather = new_weather
        self.weather_intensity = 0.0
        self.transition_time = 10  # Takes 10 updates to reach full intensity
        
        # Update ambient sounds
        if new_weather == WeatherType.RAIN:
            self.sound_manager.play_ambient("rain")
        elif new_weather == WeatherType.STORM:
            self.sound_manager.play_ambient("storm")
            self.sound_manager.play_sound("thunder")
        elif new_weather == WeatherType.RADIATION_STORM:
            self.sound_manager.play_ambient("radiation_storm")
        else:
            self.sound_manager.stop_ambient()
            
    def _apply_weather_effects(self) -> None:
        effects = self.weather_effects[self.current_weather]
        # Scale effects by intensity
        self.current_effects = WeatherEffects(
            visibility=1.0 - ((1.0 - effects.visibility) * self.weather_intensity),
            accuracy=1.0 - ((1.0 - effects.accuracy) * self.weather_intensity),
            noise_level=1.0 - ((1.0 - effects.noise_level) * self.weather_intensity),
            radiation=effects.radiation * self.weather_intensity,
            anomaly_strength=1.0 + ((effects.anomaly_strength - 1.0) * self.weather_intensity),
            movement_speed=1.0 - ((1.0 - effects.movement_speed) * self.weather_intensity)
        )
        
    def get_current_effects(self) -> WeatherEffects:
        return self.current_effects 
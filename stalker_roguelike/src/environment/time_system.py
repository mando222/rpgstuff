from dataclasses import dataclass
from typing import Tuple
import math

@dataclass
class TimeOfDay:
    hour: int
    minute: int
    
    def __str__(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"

class TimeSystem:
    def __init__(self):
        self.minutes_per_tick = 1  # How many game minutes per update
        self.current_time = TimeOfDay(6, 0)  # Start at 6 AM
        self.day = 1
        
    def update(self) -> None:
        self.current_time.minute += self.minutes_per_tick
        if self.current_time.minute >= 60:
            self.current_time.minute = 0
            self.current_time.hour += 1
            
        if self.current_time.hour >= 24:
            self.current_time.hour = 0
            self.day += 1
            
    def get_light_level(self) -> float:
        """Returns light level between 0.0 (dark) and 1.0 (full daylight)"""
        hour = self.current_time.hour + self.current_time.minute / 60.0
        
        if 6 <= hour < 8:  # Dawn
            return (hour - 6) / 2
        elif 8 <= hour < 18:  # Day
            return 1.0
        elif 18 <= hour < 20:  # Dusk
            return 1.0 - (hour - 18) / 2
        else:  # Night
            return 0.2  # Some ambient light
            
    def get_temperature(self) -> float:
        """Returns temperature in Celsius"""
        hour = self.current_time.hour + self.current_time.minute / 60.0
        
        # Base temperature curve
        base_temp = math.sin((hour - 4) * math.pi / 24) * 10 + 15
        
        # Add some random variation
        variation = (hash(f"temp{self.day}") % 100) / 100.0 * 4 - 2
        return base_temp + variation 
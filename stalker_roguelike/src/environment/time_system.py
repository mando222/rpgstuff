from dataclasses import dataclass
from typing import Tuple
import math
import time

@dataclass
class TimeOfDay:
    hour: int
    minute: int
    
    def __str__(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"

class TimeSystem:
    def __init__(self):
        self.start_time = time.time()
        self.day_length = 60 * 60  # 60 minutes in seconds
        self.day_portion = self.day_length / 2  # 30 minutes for day
        self.night_portion = self.day_length / 2  # 30 minutes for night
        self.dawn_dusk_duration = 300  # 5 minutes for transition
        
    def update(self) -> None:
        """Update time system. Called every frame."""
        pass  # No need for update as we use real time
        
    def get_time_of_day(self) -> float:
        """Get current time of day as a value between 0 and 1"""
        current_time = time.time() - self.start_time
        return (current_time % self.day_length) / self.day_length
        
    def get_light_level(self) -> float:
        """Get current light level between 0 (dark) and 1 (bright)"""
        time_of_day = self.get_time_of_day()
        
        # Dawn (0.0 to 0.1)
        if time_of_day < 0.1:
            return self._smooth_transition(time_of_day, 0.0, 0.1)
            
        # Day (0.1 to 0.4)
        elif time_of_day < 0.4:
            return 1.0
            
        # Dusk (0.4 to 0.5)
        elif time_of_day < 0.5:
            return self._smooth_transition(time_of_day, 0.4, 0.5, reverse=True)
            
        # Night (0.5 to 1.0)
        else:
            return 0.3  # Some ambient light at night
            
    def _smooth_transition(self, 
                         current: float, 
                         start: float, 
                         end: float, 
                         reverse: bool = False) -> float:
        """Create a smooth transition between two values"""
        progress = (current - start) / (end - start)
        if reverse:
            progress = 1 - progress
        # Use sine curve for smoother transition
        transition = (1 - math.cos(progress * math.pi)) / 2
        return 0.3 + (transition * 0.7)  # Transition between 0.3 and 1.0
        
    def get_period(self) -> str:
        """Get current period of the day"""
        time_of_day = self.get_time_of_day()
        if time_of_day < 0.1:
            return "dawn"
        elif time_of_day < 0.4:
            return "day"
        elif time_of_day < 0.5:
            return "dusk"
        else:
            return "night"
            
    def get_time_string(self) -> str:
        """Get formatted time string"""
        time_of_day = self.get_time_of_day()
        minutes = int(time_of_day * 60)
        hours = (minutes // 5) + 6  # Start at 6 AM
        if hours > 23:
            hours -= 24
        minutes = minutes % 5 * 12
        return f"{hours:02d}:{minutes:02d}"
        
    def get_sky_color(self) -> Tuple[int, int, int]:
        """Get current sky color based on time of day"""
        time_of_day = self.get_time_of_day()
        
        # Define colors for different times
        dawn_color = (255, 200, 150)   # Warm orange
        day_color = (135, 206, 235)    # Sky blue
        dusk_color = (255, 150, 100)   # Deep orange
        night_color = (10, 10, 35)     # Dark blue
        
        if time_of_day < 0.1:  # Dawn
            return self._blend_colors(night_color, dawn_color, time_of_day * 10)
        elif time_of_day < 0.4:  # Day
            return day_color
        elif time_of_day < 0.5:  # Dusk
            return self._blend_colors(day_color, dusk_color, (time_of_day - 0.4) * 10)
        else:  # Night
            return night_color
            
    def _blend_colors(self, color1: Tuple[int, int, int], 
                     color2: Tuple[int, int, int], 
                     factor: float) -> Tuple[int, int, int]:
        """Blend between two colors"""
        return tuple(int(c1 + (c2 - c1) * factor) 
                    for c1, c2 in zip(color1, color2))

    def get_temperature(self) -> float:
        """Returns temperature in Celsius"""
        time_of_day = self.get_time_of_day()
        
        # Base temperature curve
        base_temp = math.sin((time_of_day - 0.25) * math.pi) * 10 + 15
        
        # Add some random variation
        variation = (hash(f"temp{self.day}") % 100) / 100.0 * 4 - 2
        return base_temp + variation 
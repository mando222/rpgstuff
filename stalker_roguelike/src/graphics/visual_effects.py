from typing import List, Dict, Tuple
import pygame
import random
from ..environment.weather import WeatherType
from ..environment.time_system import TimeSystem
import math
import time
from ..constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 lifetime: int = 60, size: int = 2):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.lifetime = lifetime
        self.age = 0
        self.size = size
        
    def update(self) -> bool:
        """Update particle and return False when it should be removed"""
        self.age += 1
        if self.age >= self.lifetime:
            return False
            
        # Fade out
        self.alpha = int(255 * (1 - self.age / self.lifetime))
        return True
        
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        # Create a surface for the particle with alpha
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Create color with alpha
        color_with_alpha = (*self.color, self.alpha)
        particle_surface.fill(color_with_alpha)
        
        # Calculate screen position
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Only draw if on screen
        if (0 <= screen_x <= SCREEN_WIDTH and 
            0 <= screen_y <= SCREEN_HEIGHT):
            surface.blit(particle_surface, (screen_x, screen_y))

class VisualEffects:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.weather_particles: List[Particle] = []
        
    def update(self, weather_type: str, intensity: float, time_system) -> None:
        # Update existing particles
        self.particles = [p for p in self.particles if p.update()]
        self.weather_particles = [p for p in self.weather_particles if p.update()]
        
        # Generate weather particles
        if weather_type == "rain":
            self._generate_rain(intensity)
        elif weather_type == "radiation_storm":
            self._generate_radiation(intensity)
            
    def add_particle(self, x: float, y: float, color: Tuple[int, int, int], 
                    lifetime: int = 60, size: int = 2) -> None:
        """Add a new particle effect"""
        self.particles.append(Particle(x, y, color, lifetime, size))
        
    def _generate_rain(self, intensity: float) -> None:
        """Generate rain particles based on intensity"""
        drops = int(intensity * 5)  # 0-5 drops per frame
        for _ in range(drops):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.weather_particles.append(
                Particle(x, y, (100, 100, 255), 20, 2)
            )
            
    def _generate_radiation(self, intensity: float) -> None:
        """Generate radiation particles based on intensity"""
        particles = int(intensity * 3)  # 0-3 particles per frame
        for _ in range(particles):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.weather_particles.append(
                Particle(x, y, (0, 255, 0), 40, 3)
            )
            
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        """Render all visual effects"""
        # Create a surface for effects with alpha
        effects_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Render particles
        for particle in self.particles:
            particle.render(effects_surface, camera_offset)
            
        # Render weather particles
        for particle in self.weather_particles:
            particle.render(effects_surface, camera_offset)
            
        # Blend effects surface onto main surface
        surface.blit(effects_surface, (0, 0)) 
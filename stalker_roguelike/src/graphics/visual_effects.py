from typing import List, Dict, Tuple
import pygame
import random
from ..environment.weather import WeatherType
from ..environment.time_system import TimeSystem
import math
import time

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 velocity: Tuple[float, float], lifetime: int, size: int = 2):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.size = size
        self.alpha = 255
        
    def update(self) -> bool:
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.alpha = int((self.lifetime / 30) * 255)  # Fade out
        return self.lifetime > 0
        
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        if 0 <= screen_x < surface.get_width() and 0 <= screen_y < surface.get_height():
            color_with_alpha = (*self.color, self.alpha)
            particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            particle_surface.fill(color_with_alpha)
            surface.blit(particle_surface, (screen_x, screen_y))

class VisualEffects:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particles: List[Particle] = []
        self.overlay_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # Weather particle settings
        self.weather_particles = {
            WeatherType.RAIN: {
                "color": (150, 150, 255),
                "velocity": (-2, 15),
                "lifetime": 40,
                "size": 3,
                "spawn_rate": 10
            },
            WeatherType.STORM: {
                "color": (100, 100, 200),
                "velocity": (-4, 20),
                "lifetime": 30,
                "size": 4,
                "spawn_rate": 20
            },
            WeatherType.RADIATION_STORM: {
                "color": (0, 255, 0),
                "velocity": (-1, 5),
                "lifetime": 60,
                "size": 2,
                "spawn_rate": 15
            }
        }
        
    def update(self, weather_type: WeatherType, weather_intensity: float, 
               time_system: TimeSystem) -> None:
        # Update existing particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Generate new weather particles
        if weather_type in self.weather_particles:
            settings = self.weather_particles[weather_type]
            spawn_count = int(settings["spawn_rate"] * weather_intensity)
            
            for _ in range(spawn_count):
                self._spawn_weather_particle(weather_type)
                
        # Update overlay effects
        self._update_overlay(weather_type, weather_intensity, time_system)
        
    def _spawn_weather_particle(self, weather_type: WeatherType) -> None:
        settings = self.weather_particles[weather_type]
        
        # Randomize spawn position above screen
        x = random.randint(0, self.screen_width)
        y = random.randint(-20, 0)
        
        # Add some randomness to velocity
        base_vel = settings["velocity"]
        vel_x = base_vel[0] + random.uniform(-1, 1)
        vel_y = base_vel[1] + random.uniform(-2, 2)
        
        self.particles.append(Particle(
            x, y,
            settings["color"],
            (vel_x, vel_y),
            settings["lifetime"],
            settings["size"]
        ))
        
    def _update_overlay(self, weather_type: WeatherType, weather_intensity: float,
                       time_system: TimeSystem) -> None:
        self.overlay_surface.fill((0, 0, 0, 0))  # Clear overlay
        
        # Apply time of day lighting
        light_level = time_system.get_light_level()
        darkness = int((1.0 - light_level) * 160)  # Max darkness alpha
        pygame.draw.rect(self.overlay_surface, (0, 0, 20, darkness), 
                        (0, 0, self.screen_width, self.screen_height))
        
        # Apply weather overlays
        if weather_type == WeatherType.RADIATION_STORM:
            green_intensity = int(40 * weather_intensity)
            pygame.draw.rect(self.overlay_surface, (0, 255, 0, green_intensity),
                           (0, 0, self.screen_width, self.screen_height))
            
        elif weather_type == WeatherType.STORM:
            darkness = int(60 * weather_intensity)
            pygame.draw.rect(self.overlay_surface, (0, 0, 50, darkness),
                           (0, 0, self.screen_width, self.screen_height))
            
        elif weather_type == WeatherType.ANOMALY_SURGE:
            # Create distortion effect (wavy pattern)
            for y in range(0, self.screen_height, 4):
                wave = int(math.sin(y * 0.1 + time.time() * 2) * 10 * weather_intensity)
                pygame.draw.line(self.overlay_surface, (255, 0, 255, 30),
                               (0, y), (self.screen_width, y + wave))
        
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        # Render particles
        for particle in self.particles:
            particle.render(surface, camera_offset)
            
        # Apply overlay effects
        surface.blit(self.overlay_surface, (0, 0)) 
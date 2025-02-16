import pygame
from typing import Optional, List, Dict
from ..map.map_generator import MapGenerator
from ..entities.player import Player
from ..ui.hud import HUD
from ..ui.inventory_screen import InventoryScreen
from ..ui.menu import Menu
from ..audio.sound_manager import SoundManager
from ..audio.sound_effects import SoundEffects, MusicTracks
from ..environment.weather import WeatherSystem
from ..environment.time_system import TimeSystem
from ..graphics.visual_effects import VisualEffects
from ..constants import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    TILE_SIZE,
    BLACK
)
from ..graphics.camera import Camera
import random

class GameState:
    def __init__(self):
        self.map_generator = MapGenerator(100, 100)  # 100x100 zones
        self.map_generator.game_state = self
        self.current_zone = None
        self.player: Optional[Player] = None
        self.game_time = 0
        self.current_ui_state = "game"  # game, inventory, menu
        self.hud = HUD()
        self.inventory_screen = InventoryScreen()
        self.menu = Menu()
        self.messages: List[Dict] = []  # List of message dicts with text and color
        self.sound_manager = SoundManager()
        self.weather_system = WeatherSystem(self.sound_manager)
        self.time_system = TimeSystem()
        self.visual_effects = VisualEffects(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera = Camera(100, 100)  # Initialize with map size
        self.game_over = False
        self.death_message = ""
        
        self._initialize_game()
        
    def _initialize_game(self) -> None:
        """Initialize a new game"""
        # Create starting zone with wilderness type
        self.current_zone = self.map_generator.generate_zone(0, 0, "wilderness")
        
        # Find valid starting position
        start_pos = self._find_valid_spawn()
        self.player = Player(start_pos[0], start_pos[1])
        self.player.game_state = self
        self.current_zone.add_entity(self.player)
        
        self.sound_manager.play_music(MusicTracks.EXPLORATION.value)
        
    def _find_valid_spawn(self) -> tuple[int, int]:
        """Find a valid spawn position in the current zone."""
        # Try to spawn in the center of a room
        center_x = self.current_zone.width // 2
        center_y = self.current_zone.height // 2
        
        # Spiral out from center until we find a valid spot
        for radius in range(max(self.current_zone.width, self.current_zone.height)):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    x = center_x + dx
                    y = center_y + dy
                    if (0 <= x < self.current_zone.width and 
                        0 <= y < self.current_zone.height and
                        self.current_zone.is_walkable(x, y)):
                        return (x, y)
        
        raise Exception("No valid spawn location found")
        
    def handle_input(self, event: pygame.event.Event) -> None:
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self._restart_game()
        elif self.current_ui_state == "game":
            self._handle_game_input(event)
        elif self.current_ui_state == "inventory":
            self._handle_inventory_input(event)
        elif self.current_ui_state == "menu":
            self._handle_menu_input(event)
            
    def _handle_game_input(self, event: pygame.event.Event) -> None:
        # Handle key press events
        if event.type == pygame.KEYDOWN:
            # UI state changes
            if event.key == pygame.K_i:
                self.current_ui_state = "inventory"
            elif event.key == pygame.K_ESCAPE:
                self.current_ui_state = "menu"
            elif event.key == pygame.K_e:
                self._handle_interaction()
            elif event.key == pygame.K_SPACE:
                self._handle_attack()
                
    def _try_move_player(self, dx: int, dy: int) -> None:
        # Convert float movement values to integers
        new_x = self.player.x + int(round(dx))
        new_y = self.player.y + int(round(dy))
        
        # Check for zone transition
        if not (0 <= new_x < self.current_zone.width and 0 <= new_y < self.current_zone.height):
            self._handle_zone_transition(new_x, new_y)
            return
            
        if self.current_zone.is_walkable(new_x, new_y):
            self.player.move(int(round(dx)), int(round(dy)))
            
    def _handle_zone_transition(self, x: int, y: int) -> None:
        # Determine new zone coordinates
        current_zone_pos = next(pos for pos, zone in self.map_generator.zones.items()
                              if zone == self.current_zone)
        new_zone_x = current_zone_pos[0]
        new_zone_y = current_zone_pos[1]
        
        if x < 0:
            new_zone_x -= 1
            new_x = self.current_zone.width - 1
        elif x >= self.current_zone.width:
            new_zone_x += 1
            new_x = 0
        else:
            new_x = x
            
        if y < 0:
            new_zone_y -= 1
            new_y = self.current_zone.height - 1
        elif y >= self.current_zone.height:
            new_zone_y += 1
            new_y = 0
        else:
            new_y = y
            
        # Generate or load new zone
        if (new_zone_x, new_zone_y) not in self.map_generator.zones:
            new_zone = self.map_generator.generate_zone(new_zone_x, new_zone_y, "forest")
        else:
            new_zone = self.map_generator.zones[(new_zone_x, new_zone_y)]
            
        # Transfer player
        self.current_zone.remove_entity(self.player)
        self.current_zone = new_zone
        self.player.x = new_x
        self.player.y = new_y
        self.current_zone.add_entity(self.player)
        
        self.sound_manager.play_sound(SoundEffects.FOOTSTEP.value)
        
        # Change ambient sound based on new zone type
        if self.current_zone.zone_type == "forest":
            self.sound_manager.play_ambient(MusicTracks.AMBIENT_FOREST.value)
        elif self.current_zone.zone_type == "underground":
            self.sound_manager.play_ambient(MusicTracks.AMBIENT_UNDERGROUND.value)
        
    def update(self) -> None:
        if self.current_ui_state == "game":
            # Handle continuous movement
            keys = pygame.key.get_pressed()
            dx = dy = 0
            
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx = 1
                
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                # Instead of using 0.707, we'll just move in one direction at a time
                # This gives better grid-based movement
                if random.random() < 0.5:
                    dx = 0
                else:
                    dy = 0
                
            if dx != 0 or dy != 0:
                self._try_move_player(dx, dy)
            
            # Rest of update code...
            self.current_zone.update()
            self.game_time += 1
            
            # Update camera to follow player
            self.camera.update(self.player.x, self.player.y)
            
            # Update player effects
            if self.game_time % 10 == 0:  # Every 10 ticks
                self._update_environmental_effects()
            
            self.weather_system.update(self.game_time)
            self.time_system.update()
            
            # Apply environmental effects more frequently in bad weather
            if (self.game_time % 5 == 0 and 
                self.weather_system.current_weather.value in ["radiation_storm", "anomaly_surge"]):
                self._update_environmental_effects()
                
    def _update_environmental_effects(self) -> None:
        current_tile = self.current_zone.tiles[self.player.x][self.player.y]
        weather_effects = self.weather_system.get_current_effects()
        
        # Apply radiation from weather
        if weather_effects.radiation > 0:
            radiation_damage = weather_effects.radiation * 5
            self.player.stats.modify_health(-radiation_damage)
            self.add_message(f"Taking radiation damage from storm: {radiation_damage}", (255, 0, 0))
            
        # Apply base radiation modified by weather
        if current_tile.properties.radiation_level > 0:
            radiation_damage = (current_tile.properties.radiation_level * 
                              weather_effects.radiation * 5)
            self.player.stats.modify_health(-radiation_damage)
            self.add_message(f"Taking radiation damage: {radiation_damage}", (255, 0, 0))
            
        # Apply anomaly damage modified by weather
        if current_tile.properties.anomaly_type:
            anomaly_damage = (current_tile.properties.danger_level * 
                            weather_effects.anomaly_strength * 10)
            self.player.combat.apply_damage(anomaly_damage, 
                                          current_tile.properties.anomaly_type,
                                          "torso")
        
    def render(self, surface: pygame.Surface) -> None:
        if self.current_ui_state == "game":
            self._render_game(surface)
        elif self.current_ui_state == "inventory":
            self.inventory_screen.render(surface, self.player)
        elif self.current_ui_state == "menu":
            self.menu.render(surface)
        elif self.current_ui_state == "game_over":
            self._render_game_over(surface)
            
    def _render_game(self, surface: pygame.Surface) -> None:
        # Clear screen
        surface.fill(BLACK)
        
        # Get camera offset
        camera_offset = self.camera.get_offset()
        
        # Render current zone with camera offset
        self._render_zone(surface, camera_offset)
        
        # Update and render visual effects
        self.visual_effects.update(
            self.weather_system.current_weather,
            self.weather_system.weather_intensity,
            self.time_system
        )
        self.visual_effects.render(surface, camera_offset)
        
        # Render HUD
        self.hud.render(surface, self.player, self.messages[-5:])
        
    def _render_zone(self, surface: pygame.Surface, camera_offset: tuple[int, int]) -> None:
        # Get visible area
        view_width = SCREEN_WIDTH // TILE_SIZE
        view_height = SCREEN_HEIGHT // TILE_SIZE
        
        # Render visible tiles
        for x in range(view_width):
            for y in range(view_height):
                map_x = camera_offset[0] + x
                map_y = camera_offset[1] + y
                if 0 <= map_x < self.current_zone.width and 0 <= map_y < self.current_zone.height:
                    self.current_zone.tiles[map_x][map_y].render(
                        surface, x, y, TILE_SIZE,
                        self.time_system.get_light_level()
                    )
                    
        # Render entities
        for entity in self.current_zone.entities:
            screen_x = entity.x - camera_offset[0]
            screen_y = entity.y - camera_offset[1]
            if 0 <= screen_x < view_width and 0 <= screen_y < view_height:
                entity.render(surface, camera_offset)
                
    def add_message(self, text: str, color: tuple[int, int, int]) -> None:
        self.messages.append({"text": text, "color": color})
        if len(self.messages) > 50:  # Keep last 50 messages
            self.messages.pop(0) 

    def _handle_interaction(self) -> None:
        # Implementation of _handle_interaction method
        pass

    def _handle_attack(self) -> None:
        # Implementation of _handle_attack method
        pass

    def _handle_inventory_input(self, event: pygame.event.Event) -> None:
        # Implementation of _handle_inventory_input method
        pass

    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        # Implementation of _handle_menu_input method
        pass

    def handle_player_death(self) -> None:
        """Handle player death and game over state"""
        self.game_over = True
        self.death_message = self._get_death_message()
        self.current_ui_state = "game_over"
        self.sound_manager.play_sound(SoundEffects.PLAYER_DEATH.value)
        
    def _get_death_message(self) -> str:
        """Get a contextual death message based on how the player died"""
        if self.player.stats.current_radiation > 50:
            return "You succumbed to severe radiation poisoning..."
        elif self.current_zone.tiles[self.player.x][self.player.y].properties.anomaly_type:
            return f"You were killed by a {self.current_zone.tiles[self.player.x][self.player.y].properties.anomaly_type} anomaly..."
        else:
            return "You died in the Zone..."

    def _render_game_over(self, surface: pygame.Surface) -> None:
        """Render game over screen"""
        # Darken the game screen
        dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dark_overlay.fill((0, 0, 0))
        dark_overlay.set_alpha(128)
        surface.blit(dark_overlay, (0, 0))
        
        # Render death message
        font = pygame.font.Font(None, 48)
        death_text = font.render("GAME OVER", True, (255, 0, 0))
        message_text = font.render(self.death_message, True, (255, 255, 255))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        
        # Center text on screen
        surface.blit(death_text, 
                    (SCREEN_WIDTH//2 - death_text.get_width()//2, 
                     SCREEN_HEIGHT//2 - 60))
        surface.blit(message_text, 
                    (SCREEN_WIDTH//2 - message_text.get_width()//2, 
                     SCREEN_HEIGHT//2))
        surface.blit(restart_text, 
                    (SCREEN_WIDTH//2 - restart_text.get_width()//2, 
                     SCREEN_HEIGHT//2 + 60))

    def _restart_game(self) -> None:
        """Reset the game state for a new game"""
        self.__init__()  # Reinitialize everything 
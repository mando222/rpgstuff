from typing import Dict, List
import pygame
from ..entities.player import Player

class StatusEffectsUI:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.icon_size = 32
        self.padding = 5
        
        # Define effect icons and colors
        self.effect_properties = {
            "bleeding": {
                "color": (255, 0, 0),
                "symbol": "🩸",
                "description": "Taking bleeding damage"
            },
            "radiation": {
                "color": (0, 255, 0),
                "symbol": "☢",
                "description": "Radiation poisoning"
            },
            "poisoned": {
                "color": (0, 255, 0),
                "symbol": "☠",
                "description": "Taking poison damage"
            },
            "exhausted": {
                "color": (255, 255, 0),
                "symbol": "😫",
                "description": "Reduced stamina regeneration"
            }
        }
        
    def render(self, surface: pygame.Surface, player: Player) -> None:
        active_effects = self._get_active_effects(player)
        if not active_effects:
            return
            
        start_x = 10
        start_y = surface.get_height() - self.icon_size - 10
        
        for i, (effect, duration) in enumerate(active_effects):
            self._render_effect(surface, 
                              effect, 
                              duration, 
                              start_x + (self.icon_size + self.padding) * i,
                              start_y)
                              
    def _render_effect(self, surface: pygame.Surface, effect: str, 
                      duration: int, x: int, y: int) -> None:
        # Draw effect background
        properties = self.effect_properties[effect]
        bg_color = (*properties["color"], 128)  # Semi-transparent
        pygame.draw.rect(surface, bg_color, 
                        (x, y, self.icon_size, self.icon_size))
        
        # Draw effect symbol
        symbol = self.font.render(properties["symbol"], True, properties["color"])
        symbol_rect = symbol.get_rect(center=(x + self.icon_size//2, 
                                            y + self.icon_size//2))
        surface.blit(symbol, symbol_rect)
        
        # Draw duration
        if duration > 0:
            duration_text = self.font.render(str(duration), True, (255, 255, 255))
            surface.blit(duration_text, (x + 2, y + 2))
            
    def _get_active_effects(self, player: Player) -> List[tuple[str, int]]:
        effects = []
        
        # Check combat effects
        if player.combat.bleeding_rate > 0:
            effects.append(("bleeding", int(player.combat.bleeding_rate)))
            
        if player.combat.radiation_level > 0:
            effects.append(("radiation", int(player.combat.radiation_level)))
            
        # Check status effects
        for effect, duration in player.combat.status_effects.items():
            if duration > 0:
                effects.append((effect, duration))
                
        return effects 
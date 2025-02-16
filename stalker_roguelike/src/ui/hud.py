from typing import List, Dict
import pygame
from ..entities.player import Player

class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.message_font = pygame.font.Font(None, 20)
        self.padding = 10
        
    def render(self, surface: pygame.Surface, player: Player, messages: List[Dict]) -> None:
        # Render health bar
        self._render_bar(surface, 
                        self.padding, 
                        self.padding,
                        200, 
                        20,
                        player.stats.current_health,
                        player.stats.max_health,
                        (255, 0, 0),
                        "Health")
                        
        # Render stamina bar
        self._render_bar(surface,
                        self.padding,
                        self.padding * 2 + 20,
                        200,
                        20,
                        player.stats.current_stamina,
                        player.stats.max_stamina,
                        (0, 255, 0),
                        "Stamina")
                        
        # Render radiation level
        rad_text = f"RAD: {player.combat.radiation_level:.1f}"
        rad_surface = self.font.render(rad_text, True, (0, 255, 0))
        surface.blit(rad_surface, (self.padding, self.padding * 3 + 40))
        
        # Render messages
        message_y = surface.get_height() - (len(messages) * 20 + self.padding)
        for message in messages:
            text_surface = self.message_font.render(message["text"], True, message["color"])
            surface.blit(text_surface, (self.padding, message_y))
            message_y += 20
            
    def _render_bar(self, surface: pygame.Surface, x: int, y: int, width: int, height: int,
                   value: float, maximum: float, color: tuple[int, int, int], text: str) -> None:
        # Background
        pygame.draw.rect(surface, (70, 70, 70), (x, y, width, height))
        
        # Bar
        if maximum > 0:
            fill_width = int(width * (value / maximum))
            pygame.draw.rect(surface, color, (x, y, fill_width, height))
            
        # Text
        bar_text = f"{text}: {value}/{maximum}"
        text_surface = self.font.render(bar_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (x + width//2, y + height//2)
        surface.blit(text_surface, text_rect) 
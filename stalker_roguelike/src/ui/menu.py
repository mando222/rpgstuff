from typing import List, Tuple, Optional, Callable, Dict, Any
import pygame
import json
import os
from datetime import datetime

class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.selected_index = 0
        self.padding = 40
        
        self.main_menu_items = [
            ("Continue", self._continue_game),
            ("Save Game", self._save_game),
            ("Load Game", self._load_game),
            ("Options", self._show_options),
            ("Quit", self._quit_game)
        ]
        
        self.current_menu = self.main_menu_items
        self.menu_stack: List[List[Tuple[str, Callable]]] = []
        
    def render(self, surface: pygame.Surface) -> None:
        # Draw semi-transparent background
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title = self.title_font.render("STALKER Roguelike", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=surface.get_width()//2, 
                                  y=self.padding)
        surface.blit(title, title_rect)
        
        # Draw menu items
        start_y = title_rect.bottom + self.padding
        for i, (text, _) in enumerate(self.current_menu):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            item_text = self.font.render(text, True, color)
            item_rect = item_text.get_rect(centerx=surface.get_width()//2,
                                         y=start_y + i * 40)
            surface.blit(item_text, item_rect)
            
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.menu_stack:
                    self.current_menu = self.menu_stack.pop()
                else:
                    return "game"
                    
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.current_menu)
                
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.current_menu)
                
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                _, action = self.current_menu[self.selected_index]
                return action()
                
        return None
        
    def _continue_game(self) -> str:
        return "game"
        
    def _save_game(self) -> None:
        if self.game_state:  # Add game_state as instance variable
            save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if self.save_manager.save_game(self.game_state, save_name):
                self.show_message("Game saved successfully!")
            else:
                self.show_message("Failed to save game!", color=(255, 0, 0))
                
    def _load_game(self) -> None:
        saves = self.save_manager.get_save_list()
        if not saves:
            self.show_message("No saves found!", color=(255, 0, 0))
            return
            
        self.menu_stack.append(self.current_menu)
        self.current_menu = [(save["save_name"], lambda s=save: self._load_save(s))
                            for save in saves]
        self.current_menu.append(("Back", lambda: None))
        self.selected_index = 0
        
    def _load_save(self, save_metadata: Dict[str, Any]) -> Optional[str]:
        save_data = self.save_manager.load_game(save_metadata["save_name"])
        if save_data:
            self.game_state.load_save_data(save_data)
            self.show_message("Game loaded successfully!")
            return "game"
        else:
            self.show_message("Failed to load game!", color=(255, 0, 0))
            return None
        
    def _show_options(self) -> None:
        self.menu_stack.append(self.current_menu)
        self.current_menu = [
            ("Video Settings", self._video_settings),
            ("Audio Settings", self._audio_settings),
            ("Controls", self._control_settings),
            ("Back", lambda: None)
        ]
        self.selected_index = 0
        
    def _quit_game(self) -> str:
        return "quit"
        
    def _video_settings(self) -> None:
        # TODO: Implement video settings
        pass
        
    def _audio_settings(self) -> None:
        # TODO: Implement audio settings
        pass
        
    def _control_settings(self) -> None:
        # TODO: Implement control settings
        pass 
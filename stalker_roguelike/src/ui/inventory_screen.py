from typing import Optional, List, Tuple
import pygame
from ..entities.player import Player
from ..items.item import Item

class InventoryScreen:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 15
        self.padding = 20
        self.item_height = 30
        
    def render(self, surface: pygame.Surface, player: Player) -> None:
        # Draw semi-transparent background
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Draw inventory title
        title = self.font.render(f"Inventory ({len(player.inventory.items)}/{player.inventory.capacity})", 
                               True, (255, 255, 255))
        surface.blit(title, (self.padding, self.padding))
        
        # Draw equipped items
        self._render_equipment(surface, player, self.padding, self.padding + 40)
        
        # Draw inventory items
        self._render_items(surface, player, self.padding, self.padding + 200)
        
        # Draw item details if an item is selected
        if player.inventory.items:
            self._render_item_details(surface, 
                                    player.inventory.items[self.selected_index],
                                    surface.get_width() - 300,
                                    self.padding)
                                    
    def _render_equipment(self, surface: pygame.Surface, player: Player, x: int, y: int) -> None:
        equipment_slots = [
            ("Head", "head"),
            ("Torso", "torso"),
            ("Legs", "legs"),
            ("Primary Weapon", "weapon_primary"),
            ("Secondary Weapon", "weapon_secondary")
        ]
        
        for i, (slot_name, slot_id) in enumerate(equipment_slots):
            equipped_item = player.inventory.equipped[slot_id]
            color = (255, 255, 255) if equipped_item else (128, 128, 128)
            text = f"{slot_name}: {equipped_item.name if equipped_item else 'Empty'}"
            slot_text = self.font.render(text, True, color)
            surface.blit(slot_text, (x, y + i * 30))
            
    def _render_items(self, surface: pygame.Surface, player: Player, x: int, y: int) -> None:
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.items_per_page, len(player.inventory.items))
        
        for i, item in enumerate(player.inventory.items[start_idx:end_idx]):
            color = (255, 255, 0) if i + start_idx == self.selected_index else (255, 255, 255)
            item_text = self.font.render(f"{item.name} ({item.weight}kg)", True, color)
            surface.blit(item_text, (x, y + i * self.item_height))
            
    def _render_item_details(self, surface: pygame.Surface, item: Item, x: int, y: int) -> None:
        # Draw item name
        name_text = self.font.render(item.name, True, (255, 255, 0))
        surface.blit(name_text, (x, y))
        
        # Draw item description
        desc_lines = self._wrap_text(item.description, 40)
        for i, line in enumerate(desc_lines):
            desc_text = self.font.render(line, True, (255, 255, 255))
            surface.blit(desc_text, (x, y + 30 + i * 20))
            
        # Draw item stats
        y_offset = y + 30 + len(desc_lines) * 20 + 20
        
        if hasattr(item, "damage"):
            damage_text = self.font.render(f"Damage: {item.damage}", True, (255, 255, 255))
            surface.blit(damage_text, (x, y_offset))
            y_offset += 20
            
        if hasattr(item, "protection"):
            for prot_type, value in item.protection.items():
                prot_text = self.font.render(f"{prot_type.title()}: {value*100:.0f}%", 
                                           True, (255, 255, 255))
                surface.blit(prot_text, (x, y_offset))
                y_offset += 20
                
        # Draw item condition
        condition_text = self.font.render(f"Condition: {item.stats.condition}%", 
                                        True, (255, 255, 255))
        surface.blit(condition_text, (x, y_offset))
        
    def _wrap_text(self, text: str, width: int) -> List[str]:
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > width:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(" ".join(current_line))
        return lines
        
    def handle_input(self, event: pygame.event.Event, player: Player) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                return "game"
                
            elif event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
                    
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(player.inventory.items) - 1, self.selected_index + 1)
                if self.selected_index >= self.scroll_offset + self.items_per_page:
                    self.scroll_offset = self.selected_index - self.items_per_page + 1
                    
            elif event.key == pygame.K_e and player.inventory.items:
                # Try to equip/use selected item
                item = player.inventory.items[self.selected_index]
                if item.can_equip("weapon_primary"):
                    player.inventory.equip_item(item, "weapon_primary")
                elif item.can_equip("torso"):
                    player.inventory.equip_item(item, "torso")
                elif hasattr(item, "use"):
                    item.use(player)
                    
            elif event.key == pygame.K_d and player.inventory.items:
                # Drop selected item
                item = player.inventory.items[self.selected_index]
                player.inventory.remove_item(item)
                self.selected_index = min(self.selected_index, len(player.inventory.items) - 1)
                
        return None 
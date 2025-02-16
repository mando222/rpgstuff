import json
import os
import pickle
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

class SaveManager:
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
    def save_game(self, game_state, save_name: Optional[str] = None) -> bool:
        try:
            if save_name is None:
                save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
            save_data = self._create_save_data(game_state)
            
            # Save metadata as JSON
            metadata = {
                "save_name": save_name,
                "timestamp": datetime.now().isoformat(),
                "player_level": game_state.player.level,
                "zone_coords": self._get_current_zone_coords(game_state)
            }
            
            with open(os.path.join(self.save_dir, f"{save_name}.json"), "w") as f:
                json.dump(metadata, f)
                
            # Save game state as pickle
            with open(os.path.join(self.save_dir, f"{save_name}.dat"), "wb") as f:
                pickle.dump(save_data, f)
                
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        try:
            # Load game state
            with open(os.path.join(self.save_dir, f"{save_name}.dat"), "rb") as f:
                save_data = pickle.load(f)
            return save_data
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
            
    def get_save_list(self) -> List[Dict[str, Any]]:
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.save_dir, filename), "r") as f:
                    metadata = json.load(f)
                    saves.append(metadata)
        return sorted(saves, key=lambda x: x["timestamp"], reverse=True)
        
    def _create_save_data(self, game_state) -> Dict[str, Any]:
        return {
            "player": {
                "stats": game_state.player.stats.__dict__,
                "inventory": {
                    "items": [self._serialize_item(item) for item in game_state.player.inventory.items],
                    "equipped": {slot: self._serialize_item(item) 
                               for slot, item in game_state.player.inventory.equipped.items() if item}
                },
                "position": (game_state.player.x, game_state.player.y),
                "level": game_state.player.level,
                "experience": game_state.player.experience,
                "reputation": game_state.player.reputation
            },
            "world": {
                "current_zone": self._get_current_zone_coords(game_state),
                "explored_zones": list(game_state.map_generator.zones.keys()),
                "game_time": game_state.game_time
            },
            "quests": {
                "active": game_state.quest_manager.active_quests,
                "completed": game_state.quest_manager.completed_quests,
                "failed": game_state.quest_manager.failed_quests
            }
        }
        
    def _serialize_item(self, item) -> Dict[str, Any]:
        if item is None:
            return None
        return {
            "type": item.__class__.__name__,
            "name": item.name,
            "description": item.description,
            "weight": item.weight,
            "stats": item.stats.__dict__,
            **{k: v for k, v in item.__dict__.items() 
               if k not in ["name", "description", "weight", "stats"]}
        }
        
    def _get_current_zone_coords(self, game_state) -> Tuple[int, int]:
        return next(coords for coords, zone in game_state.map_generator.zones.items()
                   if zone == game_state.current_zone) 
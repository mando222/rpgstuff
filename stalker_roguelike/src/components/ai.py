from typing import Optional, List, Tuple
import math
from ..entities.actor import Actor

class AI:
    def __init__(self, owner: Actor):
        self.owner = owner
        self.target: Optional[Actor] = None
        self.path: List[Tuple[int, int]] = []
        self.state = "idle"
        self.alert_level = 0  # 0: unaware, 50: suspicious, 100: alert
        self.last_known_target_pos: Optional[Tuple[int, int]] = None
        self.patrol_points: List[Tuple[int, int]] = []
        self.current_patrol_index = 0
        
    def update(self, game_map, actors) -> None:
        if self.state == "idle":
            self._update_idle(game_map, actors)
        elif self.state == "suspicious":
            self._update_suspicious(game_map, actors)
        elif self.state == "combat":
            self._update_combat(game_map, actors)
        elif self.state == "fleeing":
            self._update_fleeing(game_map, actors)
            
    def _update_idle(self, game_map, actors) -> None:
        # Check for visible threats
        visible_threats = self._scan_for_threats(actors)
        if visible_threats:
            self.alert_level = 50
            self.state = "suspicious"
            return
            
        # Continue patrol if we have patrol points
        if self.patrol_points:
            target = self.patrol_points[self.current_patrol_index]
            if self._move_towards(target, game_map):
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
                
    def _update_suspicious(self, game_map, actors) -> None:
        visible_threats = self._scan_for_threats(actors)
        if visible_threats:
            self.target = visible_threats[0]
            self.alert_level = 100
            self.state = "combat"
            self.last_known_target_pos = (self.target.x, self.target.y)
        else:
            # Investigate last known position
            if self.last_known_target_pos:
                if self._move_towards(self.last_known_target_pos, game_map):
                    self.alert_level = max(0, self.alert_level - 10)
                    if self.alert_level == 0:
                        self.state = "idle"
                        self.last_known_target_pos = None
                        
    def _update_combat(self, game_map, actors) -> None:
        if not self.target or not self._can_see_actor(self.target):
            self.state = "suspicious"
            return
            
        distance = self.owner.distance_to(self.target)
        weapon = self.owner.inventory.equipped.get("weapon_primary")
        
        if weapon:
            optimal_range = weapon.range * 0.7
            # Try to maintain optimal range
            if abs(distance - optimal_range) > 2:
                if distance < optimal_range:
                    self._move_away_from(self.target, game_map)
                else:
                    self._move_towards((self.target.x, self.target.y), game_map)
            
            # Attack if possible
            if distance <= weapon.range:
                self.owner.attack(self.target)
                
        # Check if should flee
        if self.owner.stats.current_health < self.owner.stats.max_health * 0.2:
            self.state = "fleeing"
            
    def _update_fleeing(self, game_map, actors) -> None:
        if self.target:
            self._move_away_from(self.target, game_map)
        
        # Return to combat if health recovered
        if self.owner.stats.current_health > self.owner.stats.max_health * 0.5:
            self.state = "combat"
            
    def _scan_for_threats(self, actors) -> List[Actor]:
        threats = []
        for actor in actors:
            if (actor != self.owner and 
                actor.faction != self.owner.faction and 
                self._can_see_actor(actor)):
                threats.append(actor)
        return threats
        
    def _can_see_actor(self, actor: Actor) -> bool:
        # TODO: Implement proper FOV check
        distance = self.owner.distance_to(actor)
        return distance < 10  # Simple distance check for now
        
    def _move_towards(self, target: Tuple[int, int], game_map) -> bool:
        # TODO: Implement proper pathfinding
        dx = target[0] - self.owner.x
        dy = target[1] - self.owner.y
        if abs(dx) > abs(dy):
            self.owner.move(1 if dx > 0 else -1, 0)
        else:
            self.owner.move(0, 1 if dy > 0 else -1)
        return (self.owner.x, self.owner.y) == target
        
    def _move_away_from(self, target: Actor, game_map) -> None:
        dx = self.owner.x - target.x
        dy = self.owner.y - target.y
        if abs(dx) > abs(dy):
            self.owner.move(1 if dx > 0 else -1, 0)
        else:
            self.owner.move(0, 1 if dy > 0 else -1)

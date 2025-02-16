from typing import Dict, Any, List, Tuple, Optional
import random
import math
from .behavior_tree import *
from ..environment.weather import WeatherType
from ..entities.actor import Actor
from .squad import Squad

class StalkerAI:
    def __init__(self, actor: Actor):
        self.actor = actor
        self.behavior_tree = self._create_behavior_tree()
        self.memory: Dict[str, Any] = {
            "last_known_enemy_pos": None,
            "patrol_points": [],
            "current_patrol_index": 0,
            "shelter_position": None,
            "search_time": 0
        }
        self.squad: Optional[Squad] = None
        
    def _create_behavior_tree(self) -> Node:
        return Selector([
            # Take shelter in bad weather
            Sequence([
                Condition(self._check_dangerous_weather),
                Selector([
                    Sequence([
                        Condition(self._has_shelter),
                        Action(self._move_to_shelter)
                    ]),
                    Action(self._find_shelter)
                ])
            ]),
            
            # Combat behavior
            Sequence([
                Condition(self._can_see_enemy),
                Selector([
                    # Retreat if low health
                    Sequence([
                        Condition(self._is_low_health),
                        Action(self._retreat)
                    ]),
                    # Attack if good conditions
                    Sequence([
                        Condition(self._has_good_shot),
                        Action(self._attack)
                    ]),
                    # Take cover and wait for better conditions
                    Action(self._take_cover)
                ])
            ]),
            
            # Search behavior
            Sequence([
                Condition(self._has_last_known_enemy_pos),
                Action(self._search_area)
            ]),
            
            # Patrol behavior
            Sequence([
                Condition(self._should_patrol),
                Action(self._patrol)
            ])
        ])
        
    def update(self) -> None:
        context = self._build_context()
        self.behavior_tree.tick(context)
        
    def _build_context(self) -> Dict[str, Any]:
        context = {
            "actor": self.actor,
            "game_state": self.actor.game_state,
            "weather": self.actor.game_state.weather_system.current_weather,
            "weather_effects": self.actor.game_state.weather_system.get_current_effects(),
            "light_level": self.actor.game_state.time_system.get_light_level(),
            "memory": self.memory
        }
        
        # Add squad context if in squad
        if self.squad:
            context.update(self.squad.get_member_context(self.actor))
            
        return context
        
    def _check_dangerous_weather(self, context: Dict[str, Any]) -> bool:
        weather = context["weather"]
        return weather in [WeatherType.RADIATION_STORM, WeatherType.ANOMALY_SURGE, 
                         WeatherType.STORM]
                         
    def _has_shelter(self, context: Dict[str, Any]) -> bool:
        return self.memory["shelter_position"] is not None
        
    def _move_to_shelter(self, context: Dict[str, Any]) -> NodeStatus:
        if not self.memory["shelter_position"]:
            return NodeStatus.FAILURE
            
        shelter_x, shelter_y = self.memory["shelter_position"]
        if self._move_towards(shelter_x, shelter_y):
            return NodeStatus.SUCCESS
        return NodeStatus.RUNNING
        
    def _find_shelter(self, context: Dict[str, Any]) -> NodeStatus:
        # Look for buildings or covered areas nearby
        game_state = context["game_state"]
        current_zone = game_state.current_zone
        
        # Search in increasing radius
        for radius in range(1, 10):
            for x in range(self.actor.x - radius, self.actor.x + radius + 1):
                for y in range(self.actor.y - radius, self.actor.y + radius + 1):
                    if (0 <= x < current_zone.width and 0 <= y < current_zone.height and
                        current_zone.tiles[x][y].tile_type in ["building", "cave"]):
                        self.memory["shelter_position"] = (x, y)
                        return NodeStatus.SUCCESS
                        
        return NodeStatus.FAILURE
        
    def _can_see_enemy(self, context: Dict[str, Any]) -> bool:
        game_state = context["game_state"]
        weather_effects = context["weather_effects"]
        light_level = context["light_level"]
        
        # Calculate view distance based on conditions
        base_view_distance = 10
        view_distance = (base_view_distance * 
                        weather_effects.visibility * 
                        max(0.3, light_level))
        
        # Check for visible enemies
        for entity in game_state.current_zone.entities:
            if (isinstance(entity, Actor) and 
                entity.faction != self.actor.faction and
                self.actor.distance_to(entity) <= view_distance):
                self.memory["last_known_enemy_pos"] = (entity.x, entity.y)
                return True
                
        return False
        
    def _has_good_shot(self, context: Dict[str, Any]) -> bool:
        weather_effects = context["weather_effects"]
        light_level = context["light_level"]
        
        # Consider weather and lighting conditions
        if weather_effects.accuracy < 0.5 or light_level < 0.3:
            return False
            
        # Check if we have ammo
        weapon = self.actor.inventory.equipped.get("weapon_primary")
        return weapon and weapon.current_ammo > 0
        
    def _attack(self, context: Dict[str, Any]) -> NodeStatus:
        # Update to consider squad tactics
        if self.squad and context.get("squad_state") == "combat":
            # Check if we should move to a better position
            if random.random() < 0.3:  # 30% chance to reposition
                if context["role"].name == "support":
                    positions = context["support_positions"]
                else:
                    positions = context["flanking_positions"]
                    
                if positions:
                    target_pos = min(positions, 
                                   key=lambda p: self.actor.distance_to_point(*p))
                    if self._move_towards(*target_pos):
                        return NodeStatus.RUNNING
                        
        # Proceed with normal attack
        game_state = context["game_state"]
        target_pos = self.memory["last_known_enemy_pos"]
        
        # Find target at position
        for entity in game_state.current_zone.entities:
            if (isinstance(entity, Actor) and 
                entity.faction != self.actor.faction and
                entity.x == target_pos[0] and 
                entity.y == target_pos[1]):
                # Attack the target
                attack_result = self.actor.attack(entity)
                return (NodeStatus.SUCCESS if attack_result["hit"] 
                       else NodeStatus.FAILURE)
                
        return NodeStatus.FAILURE 

    def _is_low_health(self, context: Dict[str, Any]) -> bool:
        actor = context["actor"]
        return actor.stats.current_health < actor.stats.max_health * 0.3

    def _retreat(self, context: Dict[str, Any]) -> NodeStatus:
        # Update to consider squad retreat
        if self.squad and context.get("squad_state") == "retreat":
            # Retreat towards squad leader
            leader_pos = context["leader_pos"]
            if self._move_towards(*leader_pos):
                return NodeStatus.SUCCESS
                
        # Proceed with normal retreat
        if not self.memory["last_known_enemy_pos"]:
            return NodeStatus.FAILURE
        
        enemy_x, enemy_y = self.memory["last_known_enemy_pos"]
        
        # Calculate direction away from enemy
        dx = self.actor.x - enemy_x
        dy = self.actor.y - enemy_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        else:
            dx, dy = dx/distance, dy/distance
        
        # Try to move diagonally away while seeking cover
        best_cover = 0
        best_move = None
        
        for move_x, move_y in [
            (int(dx), int(dy)),
            (int(dx+0.5), int(dy+0.5)),
            (int(dx+0.5), int(dy-0.5)),
            (int(dx-0.5), int(dy+0.5)),
            (int(dx-0.5), int(dy-0.5))
        ]:
            new_x = self.actor.x + move_x
            new_y = self.actor.y + move_y
            
            if not self._is_valid_move(new_x, new_y, context):
                continue
            
            cover = self._evaluate_cover(new_x, new_y, enemy_x, enemy_y, context)
            if cover > best_cover:
                best_cover = cover
                best_move = (move_x, move_y)
            
        if best_move:
            self.actor.move(*best_move)
            return NodeStatus.RUNNING
        
        return NodeStatus.FAILURE

    def _take_cover(self, context: Dict[str, Any]) -> NodeStatus:
        """Find and move to nearby cover"""
        if not self.memory["last_known_enemy_pos"]:
            return NodeStatus.FAILURE
        
        enemy_x, enemy_y = self.memory["last_known_enemy_pos"]
        best_cover = self._evaluate_cover(self.actor.x, self.actor.y, 
                                        enemy_x, enemy_y, context)
        best_pos = None
        
        # Search nearby positions for better cover
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                new_x = self.actor.x + dx
                new_y = self.actor.y + dy
                
                if not self._is_valid_move(new_x, new_y, context):
                    continue
                
                cover = self._evaluate_cover(new_x, new_y, enemy_x, enemy_y, context)
                if cover > best_cover:
                    best_cover = cover
                    best_pos = (new_x, new_y)
                
        if best_pos:
            if self._move_towards(*best_pos):
                return NodeStatus.SUCCESS
            return NodeStatus.RUNNING
        
        return NodeStatus.FAILURE

    def _search_area(self, context: Dict[str, Any]) -> NodeStatus:
        """Search around last known enemy position"""
        if not self.memory["last_known_enemy_pos"]:
            return NodeStatus.FAILURE
        
        target_x, target_y = self.memory["last_known_enemy_pos"]
        
        # Generate search points in a spiral pattern
        if not self.memory.get("search_points"):
            self.memory["search_points"] = self._generate_search_points(target_x, target_y)
            self.memory["current_search_point"] = 0
        
        # Move to next search point
        if self.memory["current_search_point"] < len(self.memory["search_points"]):
            point = self.memory["search_points"][self.memory["current_search_point"]]
            
            if self._move_towards(*point):
                self.memory["current_search_point"] += 1
            
            return NodeStatus.RUNNING
        
        # Clear search when complete
        self.memory["search_points"] = None
        self.memory["last_known_enemy_pos"] = None
        return NodeStatus.SUCCESS

    def _should_patrol(self, context: Dict[str, Any]) -> bool:
        """Check if we should be patrolling"""
        return (not self.memory["last_known_enemy_pos"] and 
                len(self.memory["patrol_points"]) > 0)

    def _patrol(self, context: Dict[str, Any]) -> NodeStatus:
        """Move between patrol points"""
        if not self.memory["patrol_points"]:
            self._generate_patrol_points(context)
        
        current_point = self.memory["patrol_points"][self.memory["current_patrol_index"]]
        
        if self._move_towards(*current_point):
            # Move to next patrol point
            self.memory["current_patrol_index"] = (
                (self.memory["current_patrol_index"] + 1) % 
                len(self.memory["patrol_points"])
            )
        
        return NodeStatus.RUNNING

    # Helper methods
    def _move_towards(self, target_x: int, target_y: int) -> bool:
        """Move one step towards target position. Returns True if at target."""
        if self.actor.x == target_x and self.actor.y == target_y:
            return True
        
        dx = max(-1, min(1, target_x - self.actor.x))
        dy = max(-1, min(1, target_y - self.actor.y))
        
        if self.actor.move(dx, dy):
            return False
        return False

    def _is_valid_move(self, x: int, y: int, context: Dict[str, Any]) -> bool:
        """Check if position is valid to move to"""
        game_state = context["game_state"]
        current_zone = game_state.current_zone
        
        return (0 <= x < current_zone.width and 
                0 <= y < current_zone.height and
                current_zone.is_walkable(x, y))

    def _evaluate_cover(self, x: int, y: int, enemy_x: int, enemy_y: int,
                       context: Dict[str, Any]) -> float:
        """Rate how good a position is for cover from 0 to 1"""
        game_state = context["game_state"]
        current_zone = game_state.current_zone
        
        # Check if position blocks line of sight
        cover_value = 0.0
        if current_zone.tiles[x][y].properties.blocks_sight:
            cover_value += 0.8
        
        # Add value for distance from enemy
        distance = math.sqrt((x - enemy_x)**2 + (y - enemy_y)**2)
        cover_value += min(0.2, distance / 20.0)
        
        return cover_value

    def _generate_search_points(self, center_x: int, center_y: int) -> List[Tuple[int, int]]:
        """Generate spiral pattern of points to search around a center"""
        points = []
        radius = 1
        max_radius = 5
        angle = 0
        
        while radius <= max_radius:
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            points.append((x, y))
            
            angle += math.pi / 4
            if angle >= 2 * math.pi:
                angle = 0
                radius += 1
            
        return points

    def _generate_patrol_points(self, context: Dict[str, Any]) -> None:
        """Generate patrol points around current position"""
        game_state = context["game_state"]
        current_zone = game_state.current_zone
        
        points = []
        radius = random.randint(5, 10)
        
        for _ in range(4):  # Generate 4 patrol points
            angle = random.uniform(0, 2 * math.pi)
            x = self.actor.x + int(radius * math.cos(angle))
            y = self.actor.y + int(radius * math.sin(angle))
            
            # Ensure point is within bounds and walkable
            x = max(0, min(current_zone.width - 1, x))
            y = max(0, min(current_zone.height - 1, y))
            
            if current_zone.is_walkable(x, y):
                points.append((x, y))
            
        self.memory["patrol_points"] = points
        self.memory["current_patrol_index"] = 0 
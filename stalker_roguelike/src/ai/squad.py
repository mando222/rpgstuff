from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import math
from ..entities.actor import Actor
from .behavior_tree import NodeStatus

@dataclass
class SquadRole:
    name: str
    min_distance: float  # Minimum distance to maintain from target
    max_distance: float  # Maximum distance to maintain from target
    priority_targets: List[str]  # Types of enemies to prioritize

class Squad:
    def __init__(self, leader: Actor):
        self.leader = leader
        self.members: List[Actor] = [leader]
        self.roles: Dict[Actor, SquadRole] = {leader: self._get_leader_role()}
        self.formation_center = (leader.x, leader.y)
        self.squad_state = "patrol"  # patrol, combat, retreat
        self.shared_memory: Dict[str, Any] = {
            "known_enemies": set(),
            "last_known_positions": {},
            "danger_zones": set(),  # Areas to avoid
            "strategic_points": []   # Points of interest
        }
        
    def add_member(self, member: Actor, role: str) -> None:
        self.members.append(member)
        self.roles[member] = self._get_role(role)
        member.squad = self
        
    def update(self, context: Dict[str, Any]) -> None:
        self._update_squad_state(context)
        self._update_formation_center()
        self._share_information()
        
    def get_member_context(self, member: Actor) -> Dict[str, Any]:
        """Get squad-specific context for member's decision making"""
        base_context = {
            "squad_state": self.squad_state,
            "formation_center": self.formation_center,
            "role": self.roles[member],
            "leader_pos": (self.leader.x, self.leader.y),
            "shared_memory": self.shared_memory
        }
        
        # Add squad-specific tactical information
        if self.squad_state == "combat":
            base_context.update({
                "support_positions": self._get_support_positions(member),
                "flanking_positions": self._get_flanking_positions(member),
                "nearest_allies": self._get_nearest_allies(member)
            })
            
        return base_context
        
    def _update_squad_state(self, context: Dict[str, Any]) -> None:
        """Update squad's overall state based on situation"""
        if self._is_squad_in_danger():
            self.squad_state = "retreat"
        elif len(self.shared_memory["known_enemies"]) > 0:
            self.squad_state = "combat"
        else:
            self.squad_state = "patrol"
            
    def _update_formation_center(self) -> None:
        """Update the center point of the squad's formation"""
        if self.squad_state == "patrol":
            # Formation centers on leader
            self.formation_center = (self.leader.x, self.leader.y)
        else:
            # Formation centers on average position
            avg_x = sum(m.x for m in self.members) / len(self.members)
            avg_y = sum(m.y for m in self.members) / len(self.members)
            self.formation_center = (avg_x, avg_y)
            
    def _share_information(self) -> None:
        """Share information between squad members"""
        # Combine all members' known enemy positions
        for member in self.members:
            if hasattr(member.ai, "memory"):
                if member.ai.memory.get("last_known_enemy_pos"):
                    pos = member.ai.memory["last_known_enemy_pos"]
                    self.shared_memory["last_known_positions"][id(member)] = pos
                    
        # Clean up old positions
        current_time = self.leader.game_state.game_time
        self.shared_memory["last_known_positions"] = {
            k: v for k, v in self.shared_memory["last_known_positions"].items()
            if current_time - k < 100  # Remove positions older than 100 ticks
        }
        
    def _get_support_positions(self, member: Actor) -> List[tuple[int, int]]:
        """Get good positions for supporting other squad members"""
        positions = []
        role = self.roles[member]
        
        for ally in self.members:
            if ally != member:
                # Find positions at appropriate range that provide cover
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    x = ally.x + int(role.min_distance * math.cos(rad))
                    y = ally.y + int(role.min_distance * math.sin(rad))
                    
                    if self._is_valid_position(x, y):
                        positions.append((x, y))
                        
        return positions
        
    def _get_flanking_positions(self, member: Actor) -> List[tuple[int, int]]:
        """Get good positions for flanking known enemies"""
        positions = []
        
        for enemy_pos in self.shared_memory["last_known_positions"].values():
            # Get positions perpendicular to the line between squad center and enemy
            dx = enemy_pos[0] - self.formation_center[0]
            dy = enemy_pos[1] - self.formation_center[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # Calculate perpendicular vectors
                perp_x, perp_y = -dy/distance, dx/distance
                flank_distance = 5  # Distance to flank
                
                # Check both sides
                for mult in [-1, 1]:
                    x = int(enemy_pos[0] + perp_x * flank_distance * mult)
                    y = int(enemy_pos[1] + perp_y * flank_distance * mult)
                    
                    if self._is_valid_position(x, y):
                        positions.append((x, y))
                        
        return positions
        
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is valid for squad movement"""
        zone = self.leader.game_state.current_zone
        return (0 <= x < zone.width and 
                0 <= y < zone.height and 
                zone.is_walkable(x, y) and
                (x, y) not in self.shared_memory["danger_zones"])
                
    def _is_squad_in_danger(self) -> bool:
        """Determine if squad should retreat"""
        # Check overall squad health
        avg_health = sum(m.stats.current_health / m.stats.max_health 
                        for m in self.members) / len(self.members)
        if avg_health < 0.3:
            return True
            
        # Check if outnumbered significantly
        if len(self.shared_memory["known_enemies"]) > len(self.members) * 2:
            return True
            
        return False
        
    @staticmethod
    def _get_leader_role() -> SquadRole:
        return SquadRole(
            name="leader",
            min_distance=3,
            max_distance=8,
            priority_targets=["player"]
        )
        
    @staticmethod
    def _get_role(role_name: str) -> SquadRole:
        roles = {
            "assault": SquadRole(
                name="assault",
                min_distance=2,
                max_distance=5,
                priority_targets=["player", "heavy"]
            ),
            "support": SquadRole(
                name="support",
                min_distance=6,
                max_distance=12,
                priority_targets=["sniper", "support"]
            ),
            "sniper": SquadRole(
                name="sniper",
                min_distance=10,
                max_distance=20,
                priority_targets=["sniper", "player"]
            )
        }
        return roles.get(role_name, roles["assault"]) 
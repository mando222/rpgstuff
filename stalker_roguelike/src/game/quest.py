from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class QuestStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QuestObjective:
    description: str
    target_amount: int = 1
    current_amount: int = 0
    completed: bool = False
    
    def update(self, amount: int = 1) -> bool:
        if self.completed:
            return False
        self.current_amount = min(self.target_amount, self.current_amount + amount)
        if self.current_amount >= self.target_amount:
            self.completed = True
            return True
        return False

class Quest:
    def __init__(self, quest_id: str, title: str, description: str):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.status = QuestStatus.NOT_STARTED
        self.objectives: Dict[str, QuestObjective] = {}
        self.rewards: Dict[str, int] = {}  # type: money, exp, items, etc.
        self.on_complete: Optional[Callable] = None
        self.on_fail: Optional[Callable] = None
        self.prerequisites: List[str] = []  # List of quest IDs that must be completed
        
    def add_objective(self, obj_id: str, description: str, target_amount: int = 1) -> None:
        self.objectives[obj_id] = QuestObjective(description, target_amount)
        
    def update_objective(self, obj_id: str, amount: int = 1) -> bool:
        if obj_id in self.objectives:
            if self.objectives[obj_id].update(amount):
                self._check_completion()
                return True
        return False
        
    def _check_completion(self) -> None:
        if self.status != QuestStatus.IN_PROGRESS:
            return
            
        if all(obj.completed for obj in self.objectives.values()):
            self.complete()
            
    def start(self) -> bool:
        if self.status == QuestStatus.NOT_STARTED:
            self.status = QuestStatus.IN_PROGRESS
            return True
        return False
        
    def complete(self) -> None:
        if self.status == QuestStatus.IN_PROGRESS:
            self.status = QuestStatus.COMPLETED
            if self.on_complete:
                self.on_complete()
                
    def fail(self) -> None:
        if self.status == QuestStatus.IN_PROGRESS:
            self.status = QuestStatus.FAILED
            if self.on_fail:
                self.on_fail()

class QuestManager:
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []
        self.completed_quests: List[str] = []
        self.failed_quests: List[str] = []
        
    def add_quest(self, quest: Quest) -> None:
        self.quests[quest.quest_id] = quest
        
    def start_quest(self, quest_id: str) -> bool:
        if quest_id in self.quests and self._can_start_quest(quest_id):
            quest = self.quests[quest_id]
            if quest.start():
                self.active_quests.append(quest_id)
                return True
        return False
        
    def _can_start_quest(self, quest_id: str) -> bool:
        quest = self.quests[quest_id]
        return all(prereq in self.completed_quests for prereq in quest.prerequisites)
        
    def update_objective(self, quest_id: str, objective_id: str, amount: int = 1) -> None:
        if quest_id in self.quests:
            self.quests[quest_id].update_objective(objective_id, amount)
            
    def get_active_quests(self) -> List[Quest]:
        return [self.quests[qid] for qid in self.active_quests]
        
    def get_completed_quests(self) -> List[Quest]:
        return [self.quests[qid] for qid in self.completed_quests] 
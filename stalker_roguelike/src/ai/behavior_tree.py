from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from ..environment.weather import WeatherType, WeatherEffects

class NodeStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"

class Node:
    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        raise NotImplementedError

class Sequence(Node):
    def __init__(self, children: List[Node]):
        self.children = children
        self.current_child = 0
        
    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].tick(context)
            
            if status == NodeStatus.FAILURE:
                self.current_child = 0
                return NodeStatus.FAILURE
            elif status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            
            self.current_child += 1
            
        self.current_child = 0
        return NodeStatus.SUCCESS

class Selector(Node):
    def __init__(self, children: List[Node]):
        self.children = children
        self.current_child = 0
        
    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].tick(context)
            
            if status == NodeStatus.SUCCESS:
                self.current_child = 0
                return NodeStatus.SUCCESS
            elif status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            
            self.current_child += 1
            
        self.current_child = 0
        return NodeStatus.FAILURE

class Condition(Node):
    def __init__(self, check_func: Callable[[Dict[str, Any]], bool]):
        self.check_func = check_func
        
    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        return NodeStatus.SUCCESS if self.check_func(context) else NodeStatus.FAILURE

class Action(Node):
    def __init__(self, action_func: Callable[[Dict[str, Any]], NodeStatus]):
        self.action_func = action_func
        
    def tick(self, context: Dict[str, Any]) -> NodeStatus:
        return self.action_func(context) 
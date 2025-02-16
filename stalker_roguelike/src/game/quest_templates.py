from typing import Dict, Any
from .quest import Quest, QuestManager

class QuestTemplates:
    @staticmethod
    def create_quest(template_id: str, **kwargs) -> Quest:
        if template_id in QUEST_TEMPLATES:
            template = QUEST_TEMPLATES[template_id]
            quest = Quest(template_id, 
                        template["title"].format(**kwargs),
                        template["description"].format(**kwargs))
            
            # Add objectives
            for obj_id, obj_data in template["objectives"].items():
                quest.add_objective(obj_id,
                                  obj_data["description"].format(**kwargs),
                                  obj_data.get("target_amount", 1))
                
            # Add rewards
            quest.rewards = template["rewards"].copy()
            
            # Add prerequisites
            quest.prerequisites = template.get("prerequisites", [])
            
            return quest
        raise ValueError(f"Unknown quest template: {template_id}")

QUEST_TEMPLATES = {
    "artifact_hunt": {
        "title": "Hunt for {artifact_name}",
        "description": "Find a rare artifact in the {zone_name} anomaly field.",
        "objectives": {
            "find_artifact": {
                "description": "Find {artifact_name}",
                "target_amount": 1
            },
            "survive_radiation": {
                "description": "Return to safety",
                "target_amount": 1
            }
        },
        "rewards": {
            "money": 5000,
            "exp": 1000
        }
    },
    "bandit_cleanup": {
        "title": "Clear {location_name}",
        "description": "Clear out the bandit camp at {location_name}.",
        "objectives": {
            "kill_bandits": {
                "description": "Eliminate bandits",
                "target_amount": 5
            },
            "collect_intel": {
                "description": "Find bandit documents",
                "target_amount": 1
            }
        },
        "rewards": {
            "money": 3000,
            "exp": 800,
            "reputation": {
                "military": 10,
                "bandits": -20
            }
        }
    },
    "anomaly_research": {
        "title": "Study {anomaly_type} Anomaly",
        "description": "Collect data from {anomaly_type} anomalies for the scientists.",
        "objectives": {
            "collect_readings": {
                "description": "Collect anomaly readings",
                "target_amount": 3
            },
            "gather_samples": {
                "description": "Gather anomaly samples",
                "target_amount": 2
            }
        },
        "rewards": {
            "money": 2000,
            "exp": 500,
            "reputation": {
                "scientists": 15
            }
        },
        "prerequisites": ["basic_training"]
    }
} 
class Stats:
    def __init__(self, max_health: int = 100, max_stamina: int = 100):
        # Base stats
        self.max_health = max_health
        self.current_health = max_health
        self.max_stamina = max_stamina
        self.current_stamina = max_stamina
        
        # Limb health
        self.limb_health = {
            "head": 100,
            "torso": 100,
            "left_arm": 100,
            "right_arm": 100,
            "left_leg": 100,
            "right_leg": 100
        }
        
        # Combat stats
        self.strength = 10
        self.agility = 10
        self.endurance = 10
        
        # Resistance stats
        self.radiation_resistance = 0
        self.anomaly_resistance = 0
        self.bleeding_resistance = 0

    def modify_health(self, amount: int) -> None:
        self.current_health = max(0, min(self.max_health, self.current_health + amount))

    def modify_stamina(self, amount: int) -> None:
        self.current_stamina = max(0, min(self.max_stamina, self.current_stamina + amount))

    def damage_limb(self, limb: str, amount: int) -> None:
        if limb in self.limb_health:
            self.limb_health[limb] = max(0, self.limb_health[limb] - amount) 
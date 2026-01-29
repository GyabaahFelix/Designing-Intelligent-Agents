import random
import time

class DisasterEnvironment:
    def __init__(self):
        self.disasters = ["Flood", "Fire", "Earthquake", "Storm"]
        self.severity_levels = ["Low", "Moderate", "High", "Critical"]

    def sense_environment(self):
        event = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "disaster_type": random.choice(self.disasters),
            "severity": random.choice(self.severity_levels),
            "risk_level": random.randint(1, 10)
        }
        return event

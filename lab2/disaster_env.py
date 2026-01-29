import random
import time

class DisasterEnvironment:
    def __init__(self):  # FIXED __init__ method
        self.locations = ["North", "South", "East", "West"]
        self.severity_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def generate_event(self):
        return {
            "location": random.choice(self.locations),
            "severity": random.choice(self.severity_levels),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

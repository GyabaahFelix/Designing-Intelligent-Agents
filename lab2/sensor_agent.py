import asyncio
from disaster_env import DisasterEnvironment

class SensorAgent:
    def __init__(self):  # FIXED __init__ method
        self.env = DisasterEnvironment()

    async def run(self):
        print("SensorAgent started (simulation mode)...")
        while True:
            event = self.env.generate_event()
            log = f"[{event['timestamp']}] Location: {event['location']} | Severity: {event['severity']}"
            print(log)

            # Log to file
            with open("lab2/event_log.txt", "a") as f:  # ensure folder exists
                f.write(log + "\n")

            await asyncio.sleep(5)

# FIXED __name__ check
if __name__ == "__main__":
    # Make sure the log folder exists
    import os
    os.makedirs("lab2", exist_ok=True)

    asyncio.run(SensorAgent().run())

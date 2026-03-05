import asyncio
import random


############################################
# SIMPLE FSM IMPLEMENTATION
############################################

class RescueAgentFSM:

    def __init__(self):
        self.state = "IDLE"

    async def idle_state(self):
        print("State: IDLE - Waiting for disaster event...")
        await asyncio.sleep(2)

        event = random.choice(["NO", "LOW", "MEDIUM", "HIGH"])
        print(f"Event detected: {event}")

        if event == "LOW":
            self.state = "MONITOR"
        elif event == "MEDIUM":
            self.state = "RESCUE"
        elif event == "HIGH":
            self.state = "EMERGENCY"
        else:
            self.state = "IDLE"

    async def monitor_state(self):
        print("State: MONITOR - Monitoring minor disaster...")
        await asyncio.sleep(3)
        self.state = "IDLE"

    async def rescue_state(self):
        print("State: RESCUE - Performing rescue operation...")
        await asyncio.sleep(4)
        print("Rescue completed.")
        self.state = "IDLE"

    async def emergency_state(self):
        print("State: EMERGENCY - Critical response activated!")
        await asyncio.sleep(5)
        print("Emergency handled.")
        self.state = "IDLE"

    async def run(self):
        print("RescueAgent started\n")

        # Run 5 cycles for demonstration
        for _ in range(5):
            if self.state == "IDLE":
                await self.idle_state()

            elif self.state == "MONITOR":
                await self.monitor_state()

            elif self.state == "RESCUE":
                await self.rescue_state()

            elif self.state == "EMERGENCY":
                await self.emergency_state()

            print("----------------------------------------")

        print("FSM Execution Completed.")


############################################
# MAIN
############################################

async def main():
    agent = RescueAgentFSM()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

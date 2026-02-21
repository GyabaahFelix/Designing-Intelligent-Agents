import asyncio
import random
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State

############################################
# STATES
############################################

class IdleState(State):
    async def run(self):
        print("State: IDLE - Waiting for disaster event...")
        await asyncio.sleep(2)

        event = random.choice(["NO", "LOW", "MEDIUM", "HIGH"])
        print(f"Event detected: {event}")

        if event == "LOW":
            self.set_next_state("MONITOR")
        elif event == "MEDIUM":
            self.set_next_state("RESCUE")
        elif event == "HIGH":
            self.set_next_state("EMERGENCY")
        else:
            self.set_next_state("IDLE")


class MonitorState(State):
    async def run(self):
        print("State: MONITOR - Monitoring minor disaster...")
        await asyncio.sleep(3)
        self.set_next_state("IDLE")


class RescueState(State):
    async def run(self):
        print("State: RESCUE - Performing rescue operation...")
        await asyncio.sleep(4)
        print("Rescue completed.")
        self.set_next_state("IDLE")


class EmergencyState(State):
    async def run(self):
        print("State: EMERGENCY - Critical response activated!")
        await asyncio.sleep(5)
        print("Emergency handled.")
        self.set_next_state("IDLE")


############################################
# AGENT
############################################

class RescueAgent(Agent):
    async def setup(self):
        print("RescueAgent started")

        fsm = FSMBehaviour()

        # Add states
        fsm.add_state(name="IDLE", state=IdleState(), initial=True)
        fsm.add_state(name="MONITOR", state=MonitorState())
        fsm.add_state(name="RESCUE", state=RescueState())
        fsm.add_state(name="EMERGENCY", state=EmergencyState())

        # Transitions
        fsm.add_transition(source="IDLE", dest="IDLE")
        fsm.add_transition(source="IDLE", dest="MONITOR")
        fsm.add_transition(source="IDLE", dest="RESCUE")
        fsm.add_transition(source="IDLE", dest="EMERGENCY")

        fsm.add_transition(source="MONITOR", dest="IDLE")
        fsm.add_transition(source="RESCUE", dest="IDLE")
        fsm.add_transition(source="EMERGENCY", dest="IDLE")

        self.add_behaviour(fsm)


############################################
# RUN AGENT
############################################

async def main():
    agent = RescueAgent(
    "rescueagent@localhost",
    "password"
)

    await agent.start(auto_register=True)

    print("Agent running... Press CTRL+C to stop.")
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

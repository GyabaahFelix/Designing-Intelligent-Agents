from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import asyncio

class BasicAgent(Agent):
    class StartBehaviour(OneShotBehaviour):
        async def run(self):
            print("BasicAgent behaviour executed successfully.")

async def main():
    agent = BasicAgent("basicagent@localhost", "password")

    print("Initializing BasicAgent...")

    # Manually create and run behaviour (NO XMPP)
    behaviour = agent.StartBehaviour()
    behaviour.agent = agent  # attach agent manually
    await behaviour.run()

if __name__ == "__main__":
    asyncio.run(main())

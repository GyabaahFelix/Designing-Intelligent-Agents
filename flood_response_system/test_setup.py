import spade
import asyncio  # Add this import

class DummyAgent(spade.agent.Agent):
    async def setup(self):
        print(f"✅ Agent {self.jid} is running! SPADE is working.")

async def main():
    dummy = DummyAgent("test@localhost", "password")
    await dummy.start(auto_register=True)
    await asyncio.sleep(3)  # Changed from spade.sleep to asyncio.sleep
    await dummy.stop()
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    spade.run(main())
import asyncio


# ===============================
# SIMPLE FIPA-ACL MESSAGE CLASS
# ===============================
class ACLMessage:
    def __init__(self, performative, sender, receiver, content):
        self.performative = performative
        self.sender = sender
        self.receiver = receiver
        self.content = content


# ===============================
# SENSOR AGENT
# ===============================
class SensorAgent:

    async def detect_disaster(self):
        print("SensorAgent: Detecting disaster...\n")

        msg = ACLMessage(
            performative="INFORM",
            sender="sensoragent",
            receiver="rescueagent",
            content="Disaster severity: HIGH"
        )

        print("SensorAgent: INFORM message created")
        print("Performative:", msg.performative)
        print("Content:", msg.content)
        print("Sending to RescueAgent...\n")

        await asyncio.sleep(1)
        return msg


# ===============================
# RESCUE AGENT
# ===============================
class RescueAgent:

    async def receive_message(self, msg):
        print("RescueAgent: Message received")
        print("Performative:", msg.performative)
        print("Content:", msg.content, "\n")

        await asyncio.sleep(1)

        reply = ACLMessage(
            performative="REQUEST",
            sender="rescueagent",
            receiver="sensoragent",
            content="Requesting location details."
        )

        print("RescueAgent: REQUEST message created")
        print("Performative:", reply.performative)
        print("Content:", reply.content)
        print("Sending back to SensorAgent...\n")

        return reply


# ===============================
# MAIN EXECUTION
# ===============================
async def main():

    sensor = SensorAgent()
    rescue = RescueAgent()

    # Sensor sends INFORM
    inform_msg = await sensor.detect_disaster()

    # Rescue receives INFORM and replies with REQUEST
    request_msg = await rescue.receive_message(inform_msg)

    print("Communication cycle completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())

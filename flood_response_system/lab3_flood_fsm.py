import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, CyclicBehaviour
from spade.message import Message
import asyncio
import random
import json
from datetime import datetime

# ============================================
# LAB 3: URBAN FLASH FLOOD RESPONSE SYSTEM
# Location: Accra, Ghana (Coastal City)
# Disaster: Flash Flooding from Heavy Rainfall
# ============================================

# FSM States for RescueBoat Agent
class StateIdle(State):
    """Waiting for rescue assignments"""
    async def run(self):
        print("\n🛥️  [IDLE] Rescue boat waiting at base...")
        print("     Status: READY | Fuel: 100% | Crew: Available")
        
        # Wait for mission assignment
        msg = await self.receive(timeout=10)
        
        if msg:
            content = json.loads(msg.body)
            mission_type = content.get("mission_type")
            
            if mission_type == "FLOOD_RESCUE":
                self.agent.current_mission = content
                zone = content.get("zone")
                severity = content.get("severity")
                print(f"🚨 [EVENT] Emergency received: {severity} flooding in {zone}")
                self.set_next_state("ASSESSING")
            else:
                self.set_next_state("IDLE")
        else:
            self.set_next_state("IDLE")

class StateAssessing(State):
    """Assessing flood conditions and planning route"""
    async def run(self):
        mission = self.agent.current_mission
        zone = mission.get("zone")
        water_level = mission.get("water_level")
        
        print(f"\n🛥️  [ASSESSING] Analyzing conditions in {zone}...")
        print(f"     Water Level: {water_level}m")
        
        # Simulate assessment time
        await asyncio.sleep(2)
        
        # Determine approach based on severity
        if water_level > 3.0:
            self.agent.approach = "boat_only"
            print("     ⚠️  Roads impassable - Water approach required")
        elif water_level > 1.5:
            self.agent.approach = "mixed"
            print("     ⚠️  Partial flooding - Mixed approach")
        else:
            self.agent.approach = "standard"
            print("     ℹ️  Standard rescue approach")
        
        print(f"     ✅ Assessment complete - Proceeding to {zone}")
        self.set_next_state("NAVIGATING")

class StateNavigating(State):
    """Navigating to flood zone"""
    async def run(self):
        mission = self.agent.current_mission
        zone = mission.get("zone")
        priority = mission.get("priority", 1)
        
        print(f"\n🛥️  [NAVIGATING] En route to {zone}...")
        
        # Travel time depends on priority (higher = faster response)
        travel_time = 5 - priority  # Priority 3 = 2 seconds, Priority 1 = 4 seconds
        await asyncio.sleep(travel_time)
        
        print(f"     ✅ Arrived at {zone} - Starting rescue operations")
        self.set_next_state("RESCUING")

class StateRescuing(State):
    """Performing water rescue operations"""
    async def run(self):
        mission = self.agent.current_mission
        zone = mission.get("zone")
        severity = mission.get("severity")
        
        print(f"\n🛥️  [RESCUING] Active rescue in {zone}...")
        print(f"     Approach: {self.agent.approach.upper()}")
        
        # Simulate rescue operation
        rescue_time = random.randint(3, 6)
        await asyncio.sleep(rescue_time)
        
        # Calculate rescued civilians based on conditions
        if severity == "CRITICAL":
            rescued = random.randint(8, 15)
        elif severity == "HIGH":
            rescued = random.randint(4, 8)
        else:
            rescued = random.randint(1, 4)
        
        self.agent.rescued_count += rescued
        
        print(f"     ✅ RESCUED {rescued} civilians from flood zone!")
        print(f"     Total rescued this mission: {rescued}")
        
        # Report completion to coordinator
        report = Message(to="coordinator@localhost")
        report.set_metadata("performative", "inform")
        report.body = json.dumps({
            "report_type": "RESCUE_COMPLETE",
            "zone": zone,
            "rescued": rescued,
            "unit": str(self.agent.jid),
            "timestamp": datetime.now().isoformat()
        })
        await self.send(report)
        
        self.set_next_state("RETURNING")

class StateReturning(State):
    """Returning to base for refuel and medical handoff"""
    async def run(self):
        print(f"\n🛥️  [RETURNING] Heading back to base...")
        print(f"     Mission complete - Transporting rescued civilians")
        
        await asyncio.sleep(3)
        
        print(f"     ✅ Back at base - Civilians transferred to medical team")
        print(f"     🏆 Total rescues by this unit: {self.agent.rescued_count}")
        
        # Reset mission data
        self.agent.current_mission = None
        self.agent.approach = None
        
        self.set_next_state("IDLE")

class RescueBoatAgent(Agent):
    """
    SPADE Agent with FSM for flood rescue operations
    States: IDLE → ASSESSING → NAVIGATING → RESCUING → RETURNING → IDLE
    """
    
    async def setup(self):
        print("=" * 60)
        print(f"🚢 RESCUE BOAT AGENT: {self.jid}")
        print("Type: Water Rescue Unit | Location: Accra Coastal Zone")
        print("Capabilities: Flood rescue, Evacuation, Medical transport")
        print("=" * 60)
        
        # Agent attributes
        self.current_mission = None
        self.approach = None
        self.rescued_count = 0
        
        # Create FSM
        fsm = FSMBehaviour()
        
        # Add states
        fsm.add_state(name="IDLE", state=StateIdle(), initial=True)
        fsm.add_state(name="ASSESSING", state=StateAssessing())
        fsm.add_state(name="NAVIGATING", state=StateNavigating())
        fsm.add_state(name="RESCUING", state=StateRescuing())
        fsm.add_state(name="RETURNING", state=StateReturning())
        
        # Add transitions
        fsm.add_transition(source="IDLE", dest="ASSESSING")
        fsm.add_transition(source="IDLE", dest="IDLE")
        fsm.add_transition(source="ASSESSING", dest="NAVIGATING")
        fsm.add_transition(source="NAVIGATING", dest="RESCUING")
        fsm.add_transition(source="RESCUING", dest="RETURNING")
        fsm.add_transition(source="RETURNING", dest="IDLE")
        
        self.add_behaviour(fsm)
        print("🔄 FSM initialized - States: IDLE → ASSESSING → NAVIGATING → RESCUING → RETURNING\n")

class WaterLevelSensorAgent(Agent):
    """
    Simulates flood sensors in different zones of Accra
    Generates realistic water level data and emergency alerts
    """
    
    class SensorBehaviour(CyclicBehaviour):
        async def run(self):
            # Specific zones in Accra coastal area
            zones = [
                {"name": "Zone-A-Jamestown", "base_level": 2.8, "risk": "extreme"},
                {"name": "Zone-B-UsherTown", "base_level": 1.9, "risk": "high"},
                {"name": "Zone-C-IndependenceSquare", "base_level": 1.2, "risk": "medium"}
            ]
            
            for zone in zones:
                # Simulate rising water levels during storm
                storm_surge = random.uniform(0, 1.5)
                water_level = round(zone["base_level"] + storm_surge, 2)
                
                # Determine status
                if water_level > 3.5:
                    status = "CRITICAL"
                    priority = 3
                elif water_level > 2.5:
                    status = "HIGH"
                    priority = 2
                elif water_level > 1.5:
                    status = "WARNING"
                    priority = 1
                else:
                    status = "NORMAL"
                    priority = 0
                
                # Display sensor reading
                icon = "🔴" if status == "CRITICAL" else "🟠" if status == "HIGH" else "🟡" if status == "WARNING" else "🟢"
                print(f"{icon} SENSOR [{zone['name']}]: Water level {water_level}m - {status}")
                
                # Send alert if severe flooding
                if status in ["CRITICAL", "HIGH"]:
                    alert = Message(to="coordinator@localhost")
                    alert.set_metadata("performative", "inform")
                    alert.body = json.dumps({
                        "alert_type": "FLOOD_EMERGENCY",
                        "zone": zone["name"],
                        "water_level": water_level,
                        "severity": status,
                        "priority": priority,
                        "timestamp": datetime.now().isoformat()
                    })
                    await self.send(alert)
                    print(f"   🚨 EMERGENCY ALERT SENT to coordinator!")
                
                await asyncio.sleep(1)
            
            # Wait before next sensor sweep
            await asyncio.sleep(5)
    
    async def setup(self):
        print(f"📡 WATER LEVEL SENSOR: {self.jid}")
        print("Coverage: Accra Coastal Zones (Jamestown, UsherTown, Independence Square)")
        print("Monitoring: Real-time flood detection\n")
        self.add_behaviour(self.SensorBehaviour())

class FloodCoordinatorAgent(Agent):
    """
    Central coordinator for flood response
    Receives sensor alerts and dispatches rescue units
    """
    
    class CoordinationBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            
            if msg:
                try:
                    content = json.loads(msg.body)
                    sender = str(msg.sender).split('/')[0]
                    
                    # Handle emergency alerts from sensors
                    if content.get("alert_type") == "FLOOD_EMERGENCY":
                        zone = content.get("zone")
                        severity = content.get("severity")
                        water_level = content.get("water_level")
                        priority = content.get("priority")
                        
                        print(f"\n🎯 COORDINATOR: Received {severity} alert from {zone}")
                        print(f"   Water level: {water_level}m | Priority: {priority}")
                        
                        # Dispatch rescue unit
                        dispatch = Message(to="rescue1@localhost")
                        dispatch.set_metadata("performative", "request")
                        dispatch.body = json.dumps({
                            "mission_type": "FLOOD_RESCUE",
                            "zone": zone,
                            "severity": severity,
                            "water_level": water_level,
                            "priority": priority,
                            "timestamp": datetime.now().isoformat()
                        })
                        await self.send(dispatch)
                        print(f"   📤 DISPATCHED rescue unit to {zone}")
                    
                    # Handle rescue completion reports
                    elif content.get("report_type") == "RESCUE_COMPLETE":
                        zone = content.get("zone")
                        rescued = content.get("rescued")
                        unit = content.get("unit")
                        print(f"\n✅ COORDINATOR: Mission complete in {zone}")
                        print(f"   Unit: {unit} | Civilians rescued: {rescued}")
                        
                except json.JSONDecodeError:
                    print(f"⚠️  Could not parse message from {sender}")
    
    async def setup(self):
        print(f"🎯 FLOOD COORDINATOR: {self.jid}")
        print("Location: Emergency Operations Center, Accra")
        print("Function: Sensor monitoring, Task allocation, Resource coordination\n")
        self.add_behaviour(self.CoordinationBehaviour())

async def main():
    print("\n" + "=" * 70)
    print("🌊 URBAN FLASH FLOOD RESPONSE SYSTEM - LAB 3")
    print("Location: Accra, Ghana (Coastal Metropolitan Area)")
    print("Scenario: Monsoon Season Flash Flooding")
    print("=" * 70)
    print("\nSystem Components:")
    print("  📡 Water Level Sensors (3 zones)")
    print("  🎯 Flood Coordinator (Central command)")
    print("  🚢 Rescue Boat (FSM-based response unit)")
    print("=" * 70 + "\n")
    
    # Create agents
    sensor = WaterLevelSensorAgent("sensor@localhost", "password")
    coordinator = FloodCoordinatorAgent("coordinator@localhost", "password")
    rescue1 = RescueBoatAgent("rescue1@localhost", "password")
    
    # Start all agents
    await sensor.start(auto_register=True)
    await coordinator.start(auto_register=True)
    await rescue1.start(auto_register=True)
    
    print("\n" + "=" * 70)
    print("🔄 SYSTEM ACTIVE - Monitoring flood conditions...")
    print("   (Press Ctrl+C to stop)")
    print("=" * 70 + "\n")
    
    # Run for demonstration (60 seconds)
    await asyncio.sleep(60)
    
    # Stop all agents
    print("\n" + "=" * 70)
    print("🛑 Shutting down system...")
    print("=" * 70)
    
    await sensor.stop()
    await coordinator.stop()
    await rescue1.stop()
    
    print("\n✅ LAB 3 DEMONSTRATION COMPLETED")
    print("FSM Implementation: 5 states with full transitions")
    print("Rescue missions completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    spade.run(main())
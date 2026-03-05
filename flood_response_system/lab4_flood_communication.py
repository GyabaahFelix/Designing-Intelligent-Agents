import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
import asyncio
import json
import random
from datetime import datetime
from enum import Enum

# ============================================
# LAB 4: FIPA-ACL COMMUNICATION PROTOCOL
# Urban Flash Flood Response System
# Location: Accra, Ghana
# ============================================

class Performative(Enum):
    """FIPA-ACL Standard Performatives"""
    INFORM = "inform"
    REQUEST = "request"
    CONFIRM = "confirm"
    REFUSE = "refuse"
    PROPOSE = "propose"
    ACCEPT_PROPOSAL = "accept-proposal"
    REJECT_PROPOSAL = "reject-proposal"
    FAILURE = "failure"
    NOT_UNDERSTOOD = "not-understood"

class FloodSensorAgent(Agent):
    """
    Lab 4: Enhanced Sensor with proper FIPA-ACL INFORM messages
    """
    
    class SensorBehaviour(CyclicBehaviour):
        async def run(self):
            # Accra coastal zones with specific coordinates
            zones = [
                {
                    "id": "Zone-A-Jamestown",
                    "coords": {"lat": 5.6037, "lon": -0.1870},
                    "population": 15000,
                    "risk_level": "extreme"
                },
                {
                    "id": "Zone-B-UsherTown", 
                    "coords": {"lat": 5.5600, "lon": -0.2050},
                    "population": 8000,
                    "risk_level": "high"
                },
                {
                    "id": "Zone-C-IndependenceSquare",
                    "coords": {"lat": 5.5800, "lon": -0.1800},
                    "population": 5000,
                    "risk_level": "medium"
                }
            ]
            
            for zone in zones:
                # Generate realistic water level based on risk
                base = {"extreme": 2.8, "high": 1.9, "medium": 1.2}
                surge = random.uniform(0, 1.8)
                water_level = round(base[zone["risk_level"]] + surge, 2)
                
                # Determine flood status
                if water_level > 3.5:
                    status = "CRITICAL"
                    urgency = "immediate"
                elif water_level > 2.5:
                    status = "HIGH"
                    urgency = "urgent"
                elif water_level > 1.5:
                    status = "WARNING"
                    urgency = "planned"
                else:
                    status = "NORMAL"
                    urgency = "monitoring"
                
                # Create FIPA-ACL INFORM message
                msg = Message(to="coordinator@localhost")
                msg.set_metadata("performative", Performative.INFORM.value)
                msg.set_metadata("ontology", "flood-monitoring")
                msg.set_metadata("language", "JSON")
                msg.set_metadata("conversation-id", f"sensor-{zone['id']}-{datetime.now().timestamp()}")
                msg.set_metadata("sender-id", str(self.agent.jid))
                
                # Structured content (ontology-based)
                content = {
                    "message_type": "sensor_reading",
                    "sensor_id": str(self.agent.jid),
                    "timestamp": datetime.now().isoformat(),
                    "location": {
                        "zone_id": zone["id"],
                        "coordinates": zone["coords"],
                        "population_at_risk": zone["population"]
                    },
                    "measurement": {
                        "water_level_m": water_level,
                        "flood_status": status,
                        "urgency": urgency,
                        "trend": "rising" if random.random() > 0.3 else "stable"
                    }
                }
                msg.body = json.dumps(content, indent=2)
                
                await self.send(msg)
                
                # Visual output
                icon = "🔴" if status == "CRITICAL" else "🟠" if status == "HIGH" else "🟡" if status == "WARNING" else "🟢"
                print(f"\n{icon} SENSOR: {zone['id']}")
                print(f"   Water Level: {water_level}m | Status: {status}")
                print(f"   📤 SENT: INFORM to coordinator@localhost")
                
                # Send emergency alert if critical
                if status in ["CRITICAL", "HIGH"]:
                    await self.send_emergency_alert(zone, water_level, status)
                
                await asyncio.sleep(1)
            
            await asyncio.sleep(4)
        
        async def send_emergency_alert(self, zone, water_level, status):
            """Send high-priority emergency alert"""
            alert = Message(to="coordinator@localhost")
            alert.set_metadata("performative", Performative.INFORM.value)
            alert.set_metadata("ontology", "emergency-alert")
            alert.set_metadata("priority", "critical")
            alert.set_metadata("conversation-id", f"emergency-{zone['id']}-{datetime.now().timestamp()}")
            
            alert.body = json.dumps({
                "message_type": "emergency_alert",
                "alert_code": "FLOOD-001",
                "zone": zone["id"],
                "severity": status,
                "water_level": water_level,
                "estimated_casualties": random.randint(10, 100) if status == "CRITICAL" else random.randint(1, 20),
                "required_resources": ["water_rescue", "medical", "evacuation"],
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(alert)
            print(f"   🚨 EMERGENCY ALERT SENT: {status} priority")
    
    async def setup(self):
        print("=" * 70)
        print(f"📡 FLOOD SENSOR AGENT: {self.jid}")
        print("FIPA-ACL Role: Information Provider")
        print("Performatives Used: INFORM")
        print("Ontology: flood-monitoring, emergency-alert")
        print("=" * 70)
        self.add_behaviour(self.SensorBehaviour())

class FloodRescueAgent(Agent):
    """
    Lab 4: Rescue Agent with FIPA-ACL REQUEST handling
    Responds with CONFIRM, REFUSE, or FAILURE
    """
    
    class RescueHandler(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            
            if msg:
                performative = msg.get_metadata("performative")
                sender = str(msg.sender).split('/')[0]
                
                # Skip if not a REQUEST
                if performative != Performative.REQUEST.value:
                    return
                
                print(f"\n🛥️  RESCUE UNIT received {performative.upper()}")
                print(f"   From: {sender}")
                
                try:
                    content = json.dumps(json.loads(msg.body), indent=2)
                    print(f"   Content Preview: {content[:80]}...")
                except:
                    print(f"   Content: {msg.body[:80]}...")
                
                # Process the request
                await self.process_request(msg)
        
        async def process_request(self, msg):
            """Decide whether to CONFIRM, REFUSE, or FAILURE"""
            try:
                content = json.loads(msg.body)
                mission = content.get("mission", {})
                mission_type = mission.get("type")
                zone = mission.get("zone")
                priority = mission.get("priority", 1)
                
                print(f"\n   📋 Mission: {mission_type} in {zone} (Priority {priority})")
                
                # Decision logic
                boat_capacity = 8
                current_load = self.agent.current_load
                fuel_level = self.agent.fuel_level
                available = boat_capacity - current_load
                
                print(f"   Status Check: Fuel {fuel_level}% | Capacity {available}/{boat_capacity}")
                
                # Determine response
                if fuel_level < 20:
                    await self.send_refuse(msg, "INSUFFICIENT_FUEL")
                elif available < 2:
                    await self.send_refuse(msg, "CAPACITY_FULL")
                elif self.agent.status == "BUSY":
                    await self.send_refuse(msg, "AGENT_BUSY")
                else:
                    await self.send_confirm(msg, mission, available)
                    
            except Exception as e:
                await self.send_failure(msg, str(e))
        
        async def send_confirm(self, original_msg, mission, capacity):
            """Send FIPA-ACL CONFIRM"""
            reply = Message(to=str(original_msg.sender).split('/')[0])
            reply.set_metadata("performative", Performative.CONFIRM.value)
            reply.set_metadata("ontology", "rescue-coordination")
            
            eta = random.randint(5, 15)
            mission_id = f"RSC-{random.randint(10000,99999)}"
            
            reply.body = json.dumps({
                "message_type": "mission_accepted",
                "mission_id": mission_id,
                "rescue_unit": str(self.agent.jid),
                "status": "CONFIRMED",
                "eta_minutes": eta,
                "capacity_available": capacity,
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(reply)
            print(f"   ✅ SENT: CONFIRM (ETA {eta}min, Mission {mission_id})")
            
            # Execute mission
            self.agent.status = "BUSY"
            await self.execute_mission(mission, mission_id)
        
        async def send_refuse(self, original_msg, reason):
            """Send FIPA-ACL REFUSE"""
            reply = Message(to=str(original_msg.sender).split('/')[0])
            reply.set_metadata("performative", Performative.REFUSE.value)
            reply.set_metadata("ontology", "rescue-coordination")
            
            reply.body = json.dumps({
                "message_type": "mission_refused",
                "rescue_unit": str(self.agent.jid),
                "status": "REFUSED",
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(reply)
            print(f"   ❌ SENT: REFUSE (Reason: {reason})")
        
        async def send_failure(self, original_msg, error):
            """Send FIPA-ACL FAILURE"""
            reply = Message(to=str(original_msg.sender).split('/')[0])
            reply.set_metadata("performative", Performative.FAILURE.value)
            reply.set_metadata("ontology", "rescue-coordination")
            
            reply.body = json.dumps({
                "message_type": "mission_failed",
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(reply)
            print(f"   💥 SENT: FAILURE (Error: {error})")
        
        async def execute_mission(self, mission, mission_id):
            """Execute rescue and report completion"""
            zone = mission.get("zone")
            print(f"\n   🛥️  EXECUTING: Mission {mission_id} in {zone}")
            
            # Simulate rescue
            duration = 8
            await asyncio.sleep(duration)
            
            rescued = random.randint(3, 8)
            self.agent.rescued_total += rescued
            self.agent.current_load = 0
            self.agent.fuel_level -= random.randint(15, 30)
            
            print(f"   ✅ COMPLETED: Rescued {rescued} civilians")
            print(f"   🏆 Total rescues: {self.agent.rescued_total}")
            
            # Report completion
            report = Message(to="coordinator@localhost")
            report.set_metadata("performative", Performative.INFORM.value)
            report.set_metadata("ontology", "mission-report")
            report.body = json.dumps({
                "message_type": "mission_complete",
                "mission_id": mission_id,
                "zone": zone,
                "rescued": rescued,
                "unit": str(self.agent.jid),
                "timestamp": datetime.now().isoformat()
            })
            await self.send(report)
            
            self.agent.status = "READY"
            print(f"   📤 SENT: INFORM (Mission complete)")
    
    async def setup(self):
        print("=" * 70)
        print(f"🚢 FLOOD RESCUE AGENT: {self.jid}")
        print("FIPA-ACL Role: Service Provider")
        print("Performatives Used: CONFIRM, REFUSE, FAILURE, INFORM")
        print("Ontology: rescue-coordination, mission-report")
        print("=" * 70)
        
        self.status = "READY"
        self.fuel_level = 100
        self.current_load = 0
        self.rescued_total = 0
        
        self.add_behaviour(self.RescueHandler())

class FloodCoordinatorAgent(Agent):
    """
    Lab 4: Coordinator with full FIPA-ACL protocol management
    """
    
    class CoordinationEngine(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            
            if msg:
                performative = msg.get_metadata("performative")
                sender = str(msg.sender).split('/')[0]
                
                # Handle different performatives
                if performative == Performative.INFORM.value:
                    await self.handle_inform(msg, sender)
                elif performative == Performative.CONFIRM.value:
                    await self.handle_confirm(msg, sender)
                elif performative == Performative.REFUSE.value:
                    await self.handle_refuse(msg, sender)
                elif performative == Performative.FAILURE.value:
                    await self.handle_failure(msg, sender)
        
        async def handle_inform(self, msg, sender):
            """Handle INFORM messages from sensors and rescue units"""
            try:
                content = json.loads(msg.body)
                msg_type = content.get("message_type")
                
                if msg_type == "sensor_reading":
                    zone = content["location"]["zone_id"]
                    level = content["measurement"]["water_level_m"]
                    status = content["measurement"]["flood_status"]
                    
                    print(f"\n🎯 COORDINATOR received INFORM from sensor")
                    print(f"   Zone: {zone} | Water: {level}m | Status: {status}")
                    
                    # Trigger rescue if critical
                    if status in ["CRITICAL", "HIGH"]:
                        await self.dispatch_rescue(content)
                
                elif msg_type == "emergency_alert":
                    zone = content["zone"]
                    severity = content["severity"]
                    print(f"\n🚨 COORDINATOR received EMERGENCY ALERT")
                    print(f"   Zone: {zone} | Severity: {severity}")
                
                elif msg_type == "mission_complete":
                    print(f"\n✅ COORDINATOR received MISSION COMPLETE")
                    print(f"   Zone: {content['zone']} | Rescued: {content['rescued']}")
                    
            except Exception as e:
                print(f"   ⚠️  Error processing INFORM: {e}")
        
        async def dispatch_rescue(self, sensor_data):
            """Send FIPA-ACL REQUEST to rescue unit"""
            zone = sensor_data["location"]["zone_id"]
            level = sensor_data["measurement"]["water_level_m"]
            status = sensor_data["measurement"]["flood_status"]
            priority = 3 if status == "CRITICAL" else 2
            
            print(f"\n   🎯 DISPATCHING rescue to {zone}")
            
            request = Message(to="rescue1@localhost")
            request.set_metadata("performative", Performative.REQUEST.value)
            request.set_metadata("ontology", "rescue-coordination")
            
            request.body = json.dumps({
                "message_type": "rescue_request",
                "mission": {
                    "type": "water_rescue",
                    "zone": zone,
                    "water_level": level,
                    "severity": status,
                    "priority": priority
                },
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(request)
            print(f"   📤 SENT: REQUEST to rescue1@localhost")
        
        async def handle_confirm(self, msg, sender):
            """Handle CONFIRM from rescue unit"""
            content = json.loads(msg.body)
            print(f"\n🎯 COORDINATOR received CONFIRM from {sender}")
            print(f"   Mission: {content['mission_id']}")
            print(f"   ETA: {content['eta_minutes']} minutes")
        
        async def handle_refuse(self, msg, sender):
            """Handle REFUSE from rescue unit"""
            content = json.loads(msg.body)
            print(f"\n🎯 COORDINATOR received REFUSE from {sender}")
            print(f"   Reason: {content['reason']}")
        
        async def handle_failure(self, msg, sender):
            """Handle FAILURE from rescue unit"""
            content = json.loads(msg.body)
            print(f"\n🎯 COORDINATOR received FAILURE from {sender}")
            print(f"   Error: {content.get('error', 'Unknown')}")
    
    async def setup(self):
        print("=" * 70)
        print(f"🎯 FLOOD COORDINATOR: {self.jid}")
        print("FIPA-ACL Role: Coordinator")
        print("Performatives Handled: INFORM, CONFIRM, REFUSE, FAILURE")
        print("Performatives Sent: REQUEST, INFORM")
        print("=" * 70)
        self.add_behaviour(self.CoordinationEngine())

async def main():
    print("\n" + "=" * 70)
    print("🌊 LAB 4: FIPA-ACL COMMUNICATION PROTOCOL")
    print("Urban Flash Flood Response System - Accra, Ghana")
    print("=" * 70)
    print("\nFIPA-ACL Performatives Implemented:")
    print("  📤 SENT: INFORM, REQUEST")
    print("  📥 RECEIVED: INFORM, CONFIRM, REFUSE, FAILURE")
    print("\nOntologies:")
    print("  • flood-monitoring")
    print("  • emergency-alert") 
    print("  • rescue-coordination")
    print("  • mission-report")
    print("=" * 70 + "\n")
    
    # Create agents
    sensor = FloodSensorAgent("sensor@localhost", "password")
    coordinator = FloodCoordinatorAgent("coordinator@localhost", "password")
    rescue1 = FloodRescueAgent("rescue1@localhost", "password")
    
    # Start agents
    await sensor.start(auto_register=True)
    await coordinator.start(auto_register=True)
    await rescue1.start(auto_register=True)
    
    print("\n" + "=" * 70)
    print("🔄 FIPA-ACL PROTOCOL ACTIVE")
    print("   (Press Ctrl+C to stop)")
    print("=" * 70 + "\n")
    
    # Run demonstration
    await asyncio.sleep(60)
    
    # Shutdown
    print("\n" + "=" * 70)
    print("🛑 Shutting down FIPA-ACL system...")
    print("=" * 70)
    
    await sensor.stop()
    await coordinator.stop()
    await rescue1.stop()
    
    print("\n✅ LAB 4 DEMONSTRATION COMPLETED")
    print("FIPA-ACL Protocol successfully implemented!")
    print("=" * 70)

if __name__ == "__main__":
    spade.run(main())
"""
Flood Rescue Agent - Lab 4
Role: Water rescue operations
FIPA-ACL: Handles REQUEST; Sends CONFIRM, REFUSE, FAILURE, INFORM
"""

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import json
import random
from datetime import datetime


class Performative:
    """FIPA-ACL Standard Performatives"""
    INFORM = "inform"
    REQUEST = "request"
    CONFIRM = "confirm"
    REFUSE = "refuse"
    FAILURE = "failure"


class FloodRescueAgent(Agent):
    """
    Lab 4: Rescue Agent with FIPA-ACL REQUEST handling
    Responds with CONFIRM, REFUSE, or FAILURE based on availability
    """
    
    class RescueHandler(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            
            if msg:
                performative = msg.get_metadata("performative")
                sender = str(msg.sender).split('/')[0]
                
                # Only process REQUEST performatives
                if performative == Performative.REQUEST:
                    print(f"\n🛥️  RESCUE UNIT received {performative.upper()}")
                    print(f"   From: {sender}")
                    
                    try:
                        content = json.dumps(json.loads(msg.body), indent=2)
                        print(f"   Content: {content[:100]}...")
                    except:
                        print(f"   Content: {msg.body[:100]}...")
                    
                    await self.process_request(msg)
        
        async def process_request(self, msg):
            """Decide whether to CONFIRM, REFUSE, or FAILURE"""
            try:
                content = json.loads(msg.body)
                mission = content.get("mission", {})
                mission_type = mission.get("type")
                zone = mission.get("zone")
                priority = mission.get("priority", 1)
                
                print(f"\n   📋 Mission Details:")
                print(f"      Type: {mission_type}")
                print(f"      Zone: {zone}")
                print(f"      Priority: {priority}")
                
                # Decision logic based on agent state
                boat_capacity = 8
                current_load = self.agent.current_load
                fuel_level = self.agent.fuel_level
                available = boat_capacity - current_load
                
                print(f"   Status Check:")
                print(f"      Fuel: {fuel_level}%")
                print(f"      Capacity: {available}/{boat_capacity}")
                print(f"      Status: {self.agent.status}")
                
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
            reply.set_metadata("performative", Performative.CONFIRM)
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
                "approach": "water_rescue",
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(reply)
            print(f"   ✅ SENT: CONFIRM")
            print(f"      Mission ID: {mission_id}")
            print(f"      ETA: {eta} minutes")
            
            # Execute mission
            self.agent.status = "BUSY"
            await self.execute_mission(mission, mission_id)
        
        async def send_refuse(self, original_msg, reason):
            """Send FIPA-ACL REFUSE"""
            reply = Message(to=str(original_msg.sender).split('/')[0])
            reply.set_metadata("performative", Performative.REFUSE)
            reply.set_metadata("ontology", "rescue-coordination")
            
            reply.body = json.dumps({
                "message_type": "mission_refused",
                "rescue_unit": str(self.agent.jid),
                "status": "REFUSED",
                "reason": reason,
                "suggestion": "Request backup unit or air support",
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(reply)
            print(f"   ❌ SENT: REFUSE")
            print(f"      Reason: {reason}")
        
        async def send_failure(self, original_msg, error):
            """Send FIPA-ACL FAILURE"""
            reply = Message(to=str(original_msg.sender).split('/')[0])
            reply.set_metadata("performative", Performative.FAILURE)
            reply.set_metadata("ontology", "rescue-coordination")
            
            reply.body = json.dumps({
                "message_type": "mission_failed",
                "rescue_unit": str(self.agent.jid),
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(reply)
            print(f"   💥 SENT: FAILURE")
            print(f"      Error: {error}")
        
        async def execute_mission(self, mission, mission_id):
            """Execute rescue operation and report completion"""
            zone = mission.get("zone")
            print(f"\n   🛥️  EXECUTING MISSION {mission_id}")
            print(f"      Location: {zone}")
            print(f"      Operation: Water rescue")
            
            # Simulate rescue duration
            duration = 8
            await asyncio.sleep(duration)
            
            # Mission results
            rescued = random.randint(3, 8)
            self.agent.rescued_total += rescued
            self.agent.current_load = 0  # Disembarked at base
            self.agent.fuel_level -= random.randint(15, 30)
            
            print(f"   ✅ MISSION COMPLETE")
            print(f"      Rescued: {rescued} civilians")
            print(f"      Total rescues: {self.agent.rescued_total}")
            
            # Report completion to coordinator
            report = Message(to="coordinator@localhost")
            report.set_metadata("performative", Performative.INFORM)
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
            print(f"   📤 SENT: INFORM (Mission complete report)")
    
    async def setup(self):
        print("=" * 70)
        print(f"🚢 FLOOD RESCUE AGENT: {self.jid}")
        print("Type: Water Rescue Unit | Boat Capacity: 8 persons")
        print("FIPA-ACL Role: Service Provider")
        print("Performatives Used: CONFIRM, REFUSE, FAILURE, INFORM")
        print("Ontology: rescue-coordination, mission-report")
        print("=" * 70)
        
        # Agent state
        self.status = "READY"
        self.fuel_level = 100
        self.current_load = 0
        self.rescued_total = 0
        
        self.add_behaviour(self.RescueHandler())
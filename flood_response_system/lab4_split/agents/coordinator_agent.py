"""
Flood Coordinator Agent - Lab 4
Location: Emergency Operations Center, Accra
Role: Receive alerts, dispatch rescue units
FIPA-ACL: Handles INFORM, CONFIRM, REFUSE, FAILURE; Sends REQUEST, INFORM
"""

import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
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


class FloodCoordinatorAgent(Agent):
    """
    Lab 4: Coordinator with full FIPA-ACL protocol management
    Central command for flood response operations
    """
    
    class CoordinationEngine(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            
            if msg:
                performative = msg.get_metadata("performative")
                sender = str(msg.sender).split('/')[0]
                
                # Route to appropriate handler based on performative
                if performative == Performative.INFORM:
                    await self.handle_inform(msg, sender)
                elif performative == Performative.CONFIRM:
                    await self.handle_confirm(msg, sender)
                elif performative == Performative.REFUSE:
                    await self.handle_refuse(msg, sender)
                elif performative == Performative.FAILURE:
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
                    resources = content["required_resources"]
                    print(f"\n🚨 COORDINATOR received EMERGENCY ALERT")
                    print(f"   Zone: {zone} | Severity: {severity}")
                    print(f"   Requires: {', '.join(resources)}")
                
                elif msg_type == "mission_complete":
                    print(f"\n✅ COORDINATOR received MISSION COMPLETE")
                    print(f"   Zone: {content['zone']}")
                    print(f"   Rescued: {content['rescued']} civilians")
                    print(f"   By Unit: {content['unit']}")
                    
            except Exception as e:
                print(f"   ⚠️ Error processing INFORM: {e}")
        
        async def dispatch_rescue(self, sensor_data):
            """Send FIPA-ACL REQUEST to rescue unit"""
            zone = sensor_data["location"]["zone_id"]
            level = sensor_data["measurement"]["water_level_m"]
            status = sensor_data["measurement"]["flood_status"]
            priority = 3 if status == "CRITICAL" else 2
            
            print(f"\n   🎯 DISPATCHING rescue to {zone}")
            
            request = Message(to="rescue1@localhost")
            request.set_metadata("performative", Performative.REQUEST)
            request.set_metadata("ontology", "rescue-coordination")
            
            request.body = json.dumps({
                "message_type": "rescue_request",
                "mission": {
                    "type": "water_rescue",
                    "zone": zone,
                    "water_level": level,
                    "severity": status,
                    "priority": priority,
                    "estimated_civilians": random.randint(5, 30)
                },
                "requested_by": str(self.agent.jid),
                "timestamp": datetime.now().isoformat()
            })
            
            await self.send(request)
            print(f"   📤 SENT: REQUEST to rescue1@localhost")
        
        async def handle_confirm(self, msg, sender):
            """Handle CONFIRM from rescue unit"""
            content = json.loads(msg.body)
            print(f"\n🎯 COORDINATOR received CONFIRM from {sender}")
            print(f"   Mission ID: {content['mission_id']}")
            print(f"   ETA: {content['eta_minutes']} minutes")
            print(f"   Status: {content['status']}")
        
        async def handle_refuse(self, msg, sender):
            """Handle REFUSE from rescue unit"""
            content = json.loads(msg.body)
            print(f"\n🎯 COORDINATOR received REFUSE from {sender}")
            print(f"   Reason: {content['reason']}")
            print(f"   Suggestion: {content.get('suggestion', 'None')}")
        
        async def handle_failure(self, msg, sender):
            """Handle FAILURE from rescue unit"""
            content = json.loads(msg.body)
            print(f"\n🎯 COORDINATOR received FAILURE from {sender}")
            print(f"   Error: {content.get('error', 'Unknown error')}")
    
    async def setup(self):
        print("=" * 70)
        print(f"🎯 FLOOD COORDINATOR: {self.jid}")
        print("Location: Emergency Operations Center, Accra")
        print("FIPA-ACL Role: Coordinator")
        print("Performatives Handled: INFORM, CONFIRM, REFUSE, FAILURE")
        print("Performatives Sent: REQUEST, INFORM")
        print("Ontology: flood-monitoring, rescue-coordination, emergency-alert")
        print("=" * 70)
        self.add_behaviour(self.CoordinationEngine())
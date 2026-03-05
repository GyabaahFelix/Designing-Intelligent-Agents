"""
Flood Sensor Agent - Lab 4
Location: Accra, Ghana (Coastal Zones)
Role: Monitor water levels, send INFORM messages
FIPA-ACL: INFORM performative
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


class FloodSensorAgent(Agent):
    """
    Lab 4: Enhanced Sensor with proper FIPA-ACL INFORM messages
    Monitors 3 zones: Jamestown, UsherTown, Independence Square
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
                # Generate realistic water level based on risk profile
                base = {"extreme": 2.8, "high": 1.9, "medium": 1.2}
                storm_surge = random.uniform(0, 1.8)
                water_level = round(base[zone["risk_level"]] + storm_surge, 2)
                
                # Determine flood status and urgency
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
                msg.set_metadata("performative", Performative.INFORM)
                msg.set_metadata("ontology", "flood-monitoring")
                msg.set_metadata("language", "JSON")
                msg.set_metadata("conversation-id", f"sensor-{zone['id']}-{datetime.now().timestamp()}")
                msg.set_metadata("sender-id", str(self.agent.jid))
                
                # Structured content following flood-monitoring ontology
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
            """Send high-priority emergency alert using FIPA-ACL INFORM"""
            alert = Message(to="coordinator@localhost")
            alert.set_metadata("performative", Performative.INFORM)
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
        print("Location: Accra Coastal Zone")
        print("FIPA-ACL Role: Information Provider")
        print("Performatives Used: INFORM")
        print("Ontology: flood-monitoring, emergency-alert")
        print("=" * 70)
        self.add_behaviour(self.SensorBehaviour())
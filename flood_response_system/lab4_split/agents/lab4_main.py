"""
Lab 4 Main Runner - FIPA-ACL Communication Protocol
Urban Flash Flood Response System
Location: Accra, Ghana
"""

import spade
import asyncio
import sys
import os

# Add agents folder to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'agents')
sys.path.insert(0, agents_dir)

# Import agent classes
from sensor_agent import FloodSensorAgent
from coordinator_agent import FloodCoordinatorAgent
from rescue_agent import FloodRescueAgent


async def main():
    """Main execution function"""
    print("\n" + "=" * 70)
    print("🌊 LAB 4: FIPA-ACL COMMUNICATION PROTOCOL")
    print("Urban Flash Flood Response System - Accra, Ghana")
    print("=" * 70)
    print("\nSystem Architecture:")
    print("  📡 FloodSensorAgent (3 zones)")
    print("  🎯 FloodCoordinatorAgent (Central command)")
    print("  🚢 FloodRescueAgent (Water rescue unit)")
    print("\nFIPA-ACL Performatives:")
    print("  📤 SENT: INFORM, REQUEST")
    print("  📥 RECEIVED: INFORM, CONFIRM, REFUSE, FAILURE")
    print("\nOntologies:")
    print("  • flood-monitoring")
    print("  • emergency-alert")
    print("  • rescue-coordination")
    print("  • mission-report")
    print("=" * 70 + "\n")
    
    # Create agent instances
    print("Initializing agents...")
    sensor = FloodSensorAgent("sensor@localhost", "password")
    coordinator = FloodCoordinatorAgent("coordinator@localhost", "password")
    rescue1 = FloodRescueAgent("rescue1@localhost", "password")
    
    # Start all agents
    print("Starting agents...")
    await sensor.start(auto_register=True)
    await coordinator.start(auto_register=True)
    await rescue1.start(auto_register=True)
    
    print("\n" + "=" * 70)
    print("🔄 FIPA-ACL PROTOCOL ACTIVE")
    print("   Monitoring flood conditions in Accra coastal zones")
    print("   (Press Ctrl+C to stop)")
    print("=" * 70 + "\n")
    
    # Run for demonstration period
    try:
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    
    # Graceful shutdown
    print("\n" + "=" * 70)
    print("🛑 Shutting down FIPA-ACL system...")
    print("=" * 70)
    
    await sensor.stop()
    await coordinator.stop()
    await rescue1.stop()
    
    print("\n" + "=" * 70)
    print("✅ LAB 4 DEMONSTRATION COMPLETED")
    print("FIPA-ACL Protocol successfully implemented!")
    print("All agents stopped gracefully")
    print("=" * 70)


if __name__ == "__main__":
    spade.run(main())
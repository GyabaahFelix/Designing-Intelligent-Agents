# Lab 3: FSM Diagram - Flood Rescue Boat Agent

## System: Urban Flash Flood Response System
**Location:** Accra, Ghana (Coastal Metropolitan Area)  
**Specific Disaster:** Flash flooding in Jamestown, UsherTown, and Independence Square  
**Agent:** RescueBoatAgent (Water Rescue Unit)

---

## Finite State Machine (FSM) Diagram
┌─────────┐         ┌─────────────┐         ┌─────────────┐
│  IDLE   │ ──────► │  ASSESSING  │ ──────► │  NAVIGATING │
│ (Start) │ REQUEST │  (Analyze   │  PLAN   │  (Travel to │
│  🛥️⚓   │◄───────│   flood     │◄───────│   zone)     │
└────┬────┘         │  severity)  │         └──────┬──────┘
│              └─────────────┘                │
│                     ▲                       │
│                     │                       ▼
│              ┌─────────────┐         ┌─────────────┐
│              │  RETURNING  │◄────────│  RESCUING   │
└─────────────►│ (Back to   │ COMPLETE│ (Execute    │
│   base)     │         │  rescue)    │
└─────────────┘         └─────────────┘
│
▼
(Loop to IDLE)


---

## State Descriptions

| State | Description | Triggers | Actions |
|-------|-------------|----------|---------|
| **IDLE** | Boat waiting at base | Initial state; Return from mission | Monitor for requests; Display status |
| **ASSESSING** | Analyzing flood conditions | REQUEST received from Coordinator | Evaluate water level; Determine approach (boat_only/mixed/standard) |
| **NAVIGATING** | Traveling to flood zone | Assessment complete | Travel to zone; ETA based on priority |
| **RESCUING** | Active rescue operations | Arrival at zone | Rescue civilians; Update count; Send completion report |
| **RETURNING** | Heading back to base | Rescue complete | Transport civilians; Refuel; Reset mission data |

---

## Transitions (Events)

| From | To | Trigger Event | Condition |
|------|-----|---------------|-----------|
| IDLE | ASSESSING | `REQUEST` message received | `mission_type == "FLOOD_RESCUE"` |
| IDLE | IDLE | Timeout/no message | No emergency |
| ASSESSING | NAVIGATING | Assessment complete | Always |
| NAVIGATING | RESCUING | Arrival at zone | Travel time elapsed |
| RESCUING | RETURNING | Rescue complete | `rescued_count > 0` |
| RETURNING | IDLE | Back at base | Medical handoff complete |
 
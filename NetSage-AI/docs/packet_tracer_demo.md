# Packet Tracer Demo Preparation - NetSage AI (Phase 9)

## Overview

This document provides a detailed blueprint for creating a Cisco Packet Tracer scenario that demonstrates the NetSage AI troubleshooting workflow.

**Status**: Template for manual creation in Packet Tracer GUI (no automatic .pkt generation in Phase 9)

---

## Recommended Demo Scenario: Inter-VLAN Routing Issue

### Why This Scenario?

✅ Common networking problem (junior engineers encounter frequently)  
✅ Clearly demonstrable symptom (ping fails)  
✅ Obvious solution (enable VLAN on trunk)  
✅ Easy to verify (ping succeeds after fix)  
✅ Directly maps to Phase 5 VLAN cases (NET-001, NET-003, etc.)

---

## Network Topology

### Devices

```
┌─────────┐
│   R1    │  (Inter-VLAN Router)
│ 3850    │  IP: 192.168.1.1 (on router subinterface)
└────┬────┘
     │ (VLAN 1 - Management/Native)
     │ Gi0/0/1 (trunking)
     │
┌─────────────────────────────┐
│        SW1                  │
│   Catalyst 2960             │
│ Gi0/1 - Trunk to R1         │
│ Fa0/2 - VLAN 10 (PC1)       │
│ Fa0/3 - VLAN 30 (Access)    │
└─────────────────────────────┘
          │              │
          │              │
     ┌────┴───┐      ┌────┴───┐
     │  PC1   │      │  PC2   │
     │ VLAN 10│      │VLAN 30 │
     │192.168.│      │192.168.│
     │10.10   │      │30.10   │
     └────────┘      └────────┘
```

### VLAN Configuration

| VLAN | Name         | Description         | Devices     |
| ---- | ------------ | ------------------- | ----------- |
| 1    | Management   | Default native VLAN | R1, SW1     |
| 10   | DEPARTMENT_A | PC1 access VLAN     | PC1 (Fa0/2) |
| 30   | DEPARTMENT_B | PC2 access VLAN     | PC2 (Fa0/3) |

### IP Addressing Scheme

| Device | VLAN | Interface  | IP Address    | Gateway      |
| ------ | ---- | ---------- | ------------- | ------------ |
| PC1    | 10   | Fa0        | 192.168.10.10 | 192.168.10.1 |
| PC2    | 30   | Fa0        | 192.168.30.10 | 192.168.30.1 |
| R1     | 10   | Gi0/0/1.10 | 192.168.10.1  | N/A          |
| R1     | 30   | Gi0/0/1.30 | 192.168.30.1  | N/A          |
| SW1    | 1    | Vlan 1     | 192.168.1.1   | N/A          |

---

## Step-by-Step Creation in Packet Tracer

### Phase 1: Create Router

1. **Add Cisco 3850 Router**
   - Drag Router > Cisco 3850 to canvas
   - Label: "R1"

2. **Configure Router Interfaces**
   - Click Router (CLI mode)
   - Enter commands:

```cisco
enable
configure terminal

! Configure main interface
interface GigabitEthernet0/0/1
 no shutdown
 description Link to SW1

! Configure VLAN 10 subinterface
interface GigabitEthernet0/0/1.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0

! Configure VLAN 30 subinterface
interface GigabitEthernet0/0/1.30
 encapsulation dot1Q 30
 ip address 192.168.30.1 255.255.255.0

! Save config
end
write memory
```

---

### Phase 2: Create Switch

1. **Add Cisco 2960 Switch**
   - Drag Router > Cisco 2960 to canvas
   - Label: "SW1"

2. **Configure Trunk Port (Gi0/1)**
   - Right-click SW1 → CLI
   - Enter commands:

```cisco
enable
configure terminal

! Configure trunk to router
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 1
 ! ⚠️ **IMPORTANT - THE FAULT IS HERE**
 switchport trunk allowed vlan 1,10
 ! This EXCLUDES VLAN 30!
 ! The fix will ADD 30: switchport trunk allowed vlan 1,10,30
 no shutdown

! Configure access ports
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
 no shutdown

interface FastEthernet0/3
 switchport mode access
 switchport access vlan 30
 no shutdown

! Create VLANs
vlan 10
 name DEPARTMENT_A
vlan 30
 name DEPARTMENT_B

end
write memory
```

**CRITICAL**: Line `switchport trunk allowed vlan 1,10` is the **injected fault**. It prevents VLAN 30 traffic from crossing the trunk.

---

### Phase 3: Create PCs

1. **Add PC1**
   - Drag End Devices > PC to canvas
   - Label: "PC1"
   - Desktop tab → IP Configuration → Static
   - IP: `192.168.10.10`
   - Subnet: `255.255.255.0`
   - Default Gateway: `192.168.10.1`

2. **Add PC2**
   - Drag End Devices > PC to canvas
   - Label: "PC2"
   - Desktop tab → IP Configuration → Static
   - IP: `192.168.30.10`
   - Subnet: `255.255.255.0`
   - Default Gateway: `192.168.30.1`

---

### Phase 4: Create Cable Connections

1. **Connect PC1 to SW1**
   - Drag copper straight-through cable from PC1 Fa0 to SW1 Fa0/2

2. **Connect PC2 to SW1**
   - Drag copper straight-through cable from PC2 Fa0 to SW1 Fa0/3

3. **Connect SW1 to R1**
   - Drag copper straight-through cable from SW1 Gi0/1 to R1 Gi0/0/1

4. **Wait for Link Lights**
   - All ports should show green (active)
   - May take 30 seconds

---

### Phase 5: Verify Broken Network

1. **Test from PC1 to PC2**
   - Click PC1
   - Command Prompt tab
   - `ping 192.168.30.10`
   - **Expected Result**: Ping FAILS (all timeouts) ❌

```
C:\> ping 192.168.30.10
Pinging 192.168.30.10 with 32 bytes of data:
Request timed out.
Request timed out.
Request timed out.
Request timed out.

Ping statistics for 192.168.30.10:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
```

### Capture Evidence: Show Commands

From R1 or SW1, demonstrate the problem:

**Show VLAN Configuration**:

```cisco
SW1# show vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- ---
1    default                          active    Gi0/1(trunk)
10   DEPARTMENT_A                     active    Fa0/2
30   DEPARTMENT_B                     active    Fa0/3

```

**Show Trunk Configuration**:

```cisco
SW1# show interfaces trunk

Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1,10

Port        Vlans allowed and active in management domain
Gi0/1       1,10

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,10
```

**Notice**: VLAN 30 is NOT in the allowed list on the trunk! ⚠️

---

## Demonstration Workflow

### **Step 1: Show the Broken Network (1 min)**

```
"Network is down. PC1 cannot reach PC2."
```

- Show ping failure from PC1
- Show both PCs are in same network (visually on diagram)
- Show both connected to same switch

### **Step 2: Gather Evidence (2 min)**

```
"First, let's get show output to diagnose."
```

- Run `show vlan brief` on SW1
- Run `show interfaces trunk` on SW1
- Show evidence in terminal

### **Step 3: Launch NetSage AI Dashboard (2 min)**

```
"Now let's feed this into our AI system."
```

- Open NetSage AI Dashboard in browser
- Show a similar case (NET-003) in case explorer
- Show AI diagnosis: "VLAN 30 is not allowed on trunk"

### **Step 4: Review AI Recommendation (1 min)**

```
"AI says: Add VLAN 30 to the trunk allowed list."
```

- Show recommended fix in dashboard
- Emphasize: "We don't execute this automatically"

### **Step 5: Manual Fix (1 min)**

```
"Human approves. Let's apply the fix."
```

On SW1 CLI:

```cisco
enable
configure terminal
interface GigabitEthernet0/1
 switchport trunk allowed vlan 1,10,30
 end
write memory
```

### **Step 6: Verify Solution Works (1 min)**

```
"Testing connectivity again..."
```

From PC1 CLI:

```
C:\> ping 192.168.30.10
Pinging 192.168.30.10 with 32 bytes of data:
Reply from 192.168.30.10: bytes=32 time=15ms TTL=62
Reply from 192.168.30.10: bytes=32 time=12ms TTL=62
Reply from 192.168.30.10: bytes=32 time=13ms TTL=62
Reply from 192.168.30.10: bytes=32 time=14ms TTL=62

Ping statistics for 192.168.30.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% success)
    Approximate round trip times in milliseconds:
    Minimum = 12ms, Maximum = 15ms, Average = 13ms
```

**Success! Network restored.** ✅

---

## Optional: Alternative Scenarios

### Scenario 2: Native VLAN Mismatch

- Set native VLAN to 1 on router, 99 on switch
- Same symptoms, different root cause
- Fix: Match native VLAN on both sides

### Scenario 3: Missing VLAN in Database

- Create VLAN 30 on router but not on switch
- VLAN exists in subinterface but not in `vlan 30` database
- Symptom: Ping fails
- Fix: Add `vlan 30` on switch

### Scenario 4: IP Subnet Mismatch

- Set PC2 to wrong subnet (192.168.40.10)
- Same symptom (ping fails) but different root cause
- Good for showing how rule checker and AI disambiguate

---

## Saving the .pkt File

### In Packet Tracer GUI:

1. File → Save As
2. Filename: `NetSage_AI_Demo_VLAN_Routing.pkt`
3. Location: `docs/packet_tracer_scenarios/`
4. Format: Packet Tracer Document (.pkt)

### Recommended Backup Location:

```
NetSage-AI/
├── docs/
│   ├── packet_tracer_scenarios/
│   │   └── NetSage_AI_Demo_VLAN_Routing.pkt
│   └── packet_tracer_demo.md  (this file)
```

---

## Testing Checklist

Before final presentation, verify:

- [ ] All cables connected (green link lights)
- [ ] Ping from PC1 to PC2 fails (shows timeout)
- [ ] `show vlan` shows VLANs 1, 10, 30
- [ ] `show interfaces trunk` shows allowed VLANs 1,10 (missing 30)
- [ ] After fix: Ping succeeds
- [ ] After fix: `show interfaces trunk` shows 1,10,30

---

## Time Estimates

| Task              | Time       |
| ----------------- | ---------- |
| Create router     | 2 min      |
| Create switch     | 3 min      |
| Create PCs        | 2 min      |
| Create cables     | 1 min      |
| Configure IPs     | 3 min      |
| Test broken state | 1 min      |
| Total creation    | **12 min** |
| Demo presentation | **6 min**  |

**Total**: ~18 minutes

---

## Technical Notes

### Why Inter-VLAN Routing?

- Exercises Layers 2 & 3 simultaneously
- Tests both switch and router knowledge
- Common real-world issue
- Mapsto Phase 5 dataset (NET-001 through NET-005)

### Why This Exact Fault?

- VLAN not in trunk allowed list is subtle (not obviously broken)
- Requires understanding of 802.1Q trunking
- AI/rule checker can diagnose it clearly
- Junior engineers often miss this

### Why Not BGP/OSPF?

- Too complex for demo (takes 20+ minutes)
- Loss of focus on AI system
- Requires advanced Packet Tracer setup
- Stretches beyond scope of Phase 9

---

## Troubleshooting Common Issues

### Issue: Cables won't connect

**Solution**: Ensure you're using copper straight-through cables, not crossover

### Issue: No link lights

**Solution**: Wait 30 seconds. Packet Tracer simulates carrier detection. If still no lights, check interface config (no shutdown)

### Issue: PC can't get to switch

**Solution**: Verify access port VLAN. PC must be on correct VLAN to reach gateway

### Issue: Ping works when it shouldn't

**Solution**: Check that the fault is correctly applied. Review `show interfaces trunk allowed vlan`

### Issue: After fix, ping still fails

**Solution**: Wait 60 seconds for spanning tree recalculation. Try ping again. May need to restart R1 interface.

---

## Adaptation for Live Audience

### Large Screen/Projector

- Increase font size in terminal (if possible)
- Use Packet Tracer zoom to show full topology
- Consider screenshare if projector resolution is limited

### Time Pressure

- Pre-create the .pkt file
- Skip "creating devices" phase
- Go straight to "verify broken network"
- Reduce to 3-minute demo (show issue, fix, verify)

### No Projector (Personal Demo)

- Screen-share Packet Tracer + Dashboard side-by-side
- Annotate with arrows what to watch
- Have backup screenshots if connection fails

---

## Integration with Dashboard Demo

### Timing in Full Presentation:

1. Show NetSage AI Dashboard (7 minutes)
2. Show actual Packet Tracer scenario (8 minutes)
3. **Total: 15 minutes**

### Connection Points:

- Dashboard shows case NET-003 (similar VLAN trunk issue)
- Packet Tracer demonstrates the same problem
- Show how AI diagnoses both

---

**Version**: Phase 9  
**Last Updated**: 2026-08-29  
**Status**: Manual Creation Template (Ready for PT GUI implementation)

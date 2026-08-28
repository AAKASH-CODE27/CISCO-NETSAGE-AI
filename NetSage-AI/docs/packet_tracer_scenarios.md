# NetSage AI — Packet Tracer Troubleshooting Scenarios

This document provides full details for all **35 Packet Tracer lab scenarios** in the NetSage AI dataset.

## Ground-Truth Architecture Overview

Each scenario is divided into:
- **Public Evidence**: Case ID, Category, User-visible Symptom, Topology Note, Cisco Show Commands.
- **Ground Truth**: Expected Root Cause, OSI Layer, Severity, Recommended Fix, Verification Procedure.

---

## NET-001 — VLAN (Medium Severity)

- **Category Tag**: `VLAN`
- **OSI Layer**: `Layer 2`
- **Severity**: `Medium`
- **Network Topology**: PC1 -> SW1 -> SW2 -> PC2
- **Expected User Symptom**: PC1 cannot ping PC2. Both are in the same department but connected to different switches.
- **Observed Show Commands**:
```text
SW1# show interfaces trunk
Port   Mode   Encapsulation  Status  Native vlan
Gi0/1  on     802.1q         trunking 1

SW2# show interfaces trunk
Port   Mode   Encapsulation  Status  Native vlan
Gi0/1  on     802.1q         trunking 1

SW1# show vlan brief
10   Sales    active    Fa0/1

SW2# show vlan brief
20   IT       active    Fa0/1
```
- **Expected Root Cause**: PC1 and PC2 are assigned to different VLANs (10 and 20) on their respective access ports.
- **Recommended Fix**: Reassign switchport Fa0/1 on SW2 to VLAN 10 using switchport access vlan 10.
- **Verification Procedure**: show vlan brief on SW2 and ping PC2 from PC1

---

## NET-002 — VLAN (Medium Severity)

- **Category Tag**: `VLAN`
- **OSI Layer**: `Layer 2`
- **Severity**: `Medium`
- **Network Topology**: PC -> SW1 (Fa0/2)
- **Expected User Symptom**: New PC connected to SW1 Fa0/2 cannot reach the network.
- **Observed Show Commands**:
```text
SW1# show vlan brief
1    default  active    Fa0/1, Fa0/3

SW1# show interfaces Fa0/2 switchport
Name: Fa0/2
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Access Mode VLAN: 10 (Inactive)
```
- **Expected Root Cause**: VLAN 10 is configured on the access port but missing from the VLAN database.
- **Recommended Fix**: Create VLAN 10 in global configuration mode on SW1 (vlan 10).
- **Verification Procedure**: show vlan brief on SW1 to verify VLAN 10 is active

---

## NET-003 — VLAN (High Severity)

- **Category Tag**: `VLAN`
- **OSI Layer**: `Layer 2`
- **Severity**: `High`
- **Network Topology**: SW_A -> trunk -> SW_B
- **Expected User Symptom**: Traffic from VLAN 30 cannot cross between Switch A and Switch B. Other VLANs work fine.
- **Observed Show Commands**:
```text
SW_A# show interfaces trunk
Port        Vlans allowed on trunk
Gi0/1       10,20,30

SW_B# show interfaces trunk
Port        Vlans allowed on trunk
Gi0/1       10,20
```
- **Expected Root Cause**: VLAN 30 is not allowed on the trunk link on Switch B.
- **Recommended Fix**: Add VLAN 30 to the allowed trunk VLAN list on SW_B Gi0/1 (switchport trunk allowed vlan add 30).
- **Verification Procedure**: show interfaces trunk on SW_B

---

## NET-004 — VLAN (Low Severity)

- **Category Tag**: `VLAN`
- **OSI Layer**: `Layer 2`
- **Severity**: `Low`
- **Network Topology**: SW1 (Gi0/1) -> SW2 (Gi0/1)
- **Expected User Symptom**: CDP messages indicate a 'Native VLAN mismatch' on the trunk between SW1 and SW2.
- **Observed Show Commands**:
```text
SW1# show interfaces Gi0/1 switchport
Trunking Native Mode VLAN: 99 (Management)

SW2# show interfaces Gi0/1 switchport
Trunking Native Mode VLAN: 1 (default)
```
- **Expected Root Cause**: Native VLAN mismatch across the trunk link (99 vs 1).
- **Recommended Fix**: Set native VLAN on SW2 interface Gi0/1 to match SW1 (switchport trunk native vlan 99).
- **Verification Procedure**: show interfaces Gi0/1 switchport on SW2 and monitor CDP console logs

---

## NET-005 — Gateway (High Severity)

- **Category Tag**: `Gateway`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: PC1 (192.168.1.50) -> SW1 -> R1 (192.168.1.1)
- **Expected User Symptom**: PC1 can ping other PCs in its subnet but cannot reach the internet or other subnets.
- **Observed Show Commands**:
```text
C:\> ipconfig
IPv4 Address: 192.168.1.50
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.1.254

R1# show ip interface brief
GigabitEthernet0/0     192.168.1.1     YES manual up                    up
```
- **Expected Root Cause**: Incorrect default gateway configured on PC1 (192.168.1.254 instead of 192.168.1.1).
- **Recommended Fix**: Change PC1 default gateway address to 192.168.1.1 in network settings.
- **Verification Procedure**: ipconfig on PC1 and ping 192.168.1.1

---

## NET-006 — Gateway (Critical Severity)

- **Category Tag**: `Gateway`
- **OSI Layer**: `Layer 1`
- **Severity**: `Critical`
- **Network Topology**: Branch PCs -> SW -> R_Branch (Gi0/0)
- **Expected User Symptom**: Entire branch office cannot access the main headquarters network.
- **Observed Show Commands**:
```text
R_Branch# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.1.1.1        YES manual administratively down down
GigabitEthernet0/1     192.168.100.1   YES manual up                    up
```
- **Expected Root Cause**: The gateway interface (Gi0/0) on the branch router is administratively down.
- **Recommended Fix**: Enter interface GigabitEthernet0/0 configuration mode on R_Branch and execute no shutdown.
- **Verification Procedure**: show ip interface brief on R_Branch

---

## NET-007 — Gateway (High Severity)

- **Category Tag**: `Gateway`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: Server (10.0.0.10/24) -> Router (10.0.1.1/24)
- **Expected User Symptom**: Server cannot reach external networks despite seemingly correct IP settings.
- **Observed Show Commands**:
```text
Server# ipconfig
IPv4 Address: 10.0.0.10
Subnet Mask: 255.255.255.0
Default Gateway: 10.0.1.1

Router# show running-config interface Gi0/0
interface GigabitEthernet0/0
 ip address 10.0.1.1 255.255.255.0
```
- **Expected Root Cause**: Server's default gateway is on a different subnet (10.0.1.x) than the server's IP (10.0.0.x).
- **Recommended Fix**: Reconfigure server default gateway to an IP inside 10.0.0.0/24 (e.g. 10.0.0.1).
- **Verification Procedure**: ipconfig on server and ping 10.0.0.1

---

## NET-008 — DHCP (High Severity)

- **Category Tag**: `DHCP`
- **OSI Layer**: `Layer 7`
- **Severity**: `High`
- **Network Topology**: Clients -> SW1 -> R1 (DHCP Server)
- **Expected User Symptom**: New clients connecting to the network fail to get an IP address and receive APIPA addresses instead.
- **Observed Show Commands**:
```text
R1# show ip dhcp pool LAN
Pool LAN :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 50
 Leased addresses               : 50
 Pending event                  : none
```
- **Expected Root Cause**: DHCP pool is exhausted; 50/50 addresses are leased.
- **Recommended Fix**: Expand DHCP subnet address pool or clear expired bindings with clear ip dhcp binding *.
- **Verification Procedure**: show ip dhcp pool LAN on R1

---

## NET-009 — DHCP (High Severity)

- **Category Tag**: `DHCP`
- **OSI Layer**: `Layer 7`
- **Severity**: `High`
- **Network Topology**: PCs -> SW1 -> R1 (DHCP)
- **Expected User Symptom**: PCs receive DHCP IP addresses but cannot route traffic off the local subnet.
- **Observed Show Commands**:
```text
R1# show running-config | section dhcp
ip dhcp pool OFFICE
 network 192.168.10.0 255.255.255.0
 default-router 192.168.20.1
 dns-server 8.8.8.8

R1# show ip interface brief
Gi0/0    192.168.10.1    YES manual up    up
```
- **Expected Root Cause**: Incorrect default-router in DHCP pool (192.168.20.1 instead of 192.168.10.1).
- **Recommended Fix**: Update DHCP pool configuration on R1 with default-router 192.168.10.1.
- **Verification Procedure**: ipconfig /renew on client PC and verify gateway address

---

## NET-010 — DHCP (Medium Severity)

- **Category Tag**: `DHCP`
- **OSI Layer**: `Layer 3`
- **Severity**: `Medium`
- **Network Topology**: VLAN 20 Clients -> SW (L3) -> DHCP Server (VLAN 10)
- **Expected User Symptom**: Clients on VLAN 20 do not get an IP address. DHCP server is on VLAN 10.
- **Observed Show Commands**:
```text
SW# show running-config interface Vlan20
interface Vlan20
 ip address 10.0.20.1 255.255.255.0
 ! Missing helper-address

SW# show running-config interface Vlan10
interface Vlan10
 ip address 10.0.10.1 255.255.255.0
```
- **Expected Root Cause**: Missing ip helper-address on the VLAN 20 interface to forward DHCP broadcasts.
- **Recommended Fix**: Configure ip helper-address 10.0.10.2 under interface Vlan20 on SW.
- **Verification Procedure**: show running-config interface Vlan20 and ipconfig /renew on client

---

## NET-011 — DHCP (High Severity)

- **Category Tag**: `DHCP`
- **OSI Layer**: `Layer 7`
- **Severity**: `High`
- **Network Topology**: Router provides DHCP for its own attached subnet.
- **Expected User Symptom**: Occasional IP conflict warnings on the network. Router interfaces sometimes unreachable.
- **Observed Show Commands**:
```text
Router# show running-config | include dhcp
ip dhcp pool LOCAL
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1

Router# show ip dhcp conflict
IP address        Detection method   Detection time          VRF
192.168.1.1       Ping               Mar 01 2026 10:00 AM
```
- **Expected Root Cause**: Router IP (192.168.1.1) is not excluded from the DHCP pool, causing conflicts.
- **Recommended Fix**: Add ip dhcp excluded-address 192.168.1.1 to global router configuration.
- **Verification Procedure**: show running-config | include excluded-address and clear ip dhcp conflict *

---

## NET-012 — DNS (High Severity)

- **Category Tag**: `DNS`
- **OSI Layer**: `Layer 7`
- **Severity**: `High`
- **Network Topology**: Users -> Router -> ISP
- **Expected User Symptom**: Users can ping 8.8.8.8 but cannot browse websites by name.
- **Observed Show Commands**:
```text
C:\> ping 8.8.8.8
Reply from 8.8.8.8: bytes=32 time=20ms TTL=115

C:\> ipconfig /all
DNS Servers . . . . . . . . . . . : 127.0.0.1
```
- **Expected Root Cause**: Incorrect DNS server (127.0.0.1) configured via DHCP or statically.
- **Recommended Fix**: Update DNS server IP address to a reachable server (e.g. 8.8.8.8 or internal DNS IP).
- **Verification Procedure**: nslookup cisco.com on PC

---

## NET-013 — DNS (Medium Severity)

- **Category Tag**: `DNS`
- **OSI Layer**: `Layer 4`
- **Severity**: `Medium`
- **Network Topology**: PC -> Internal DNS Server -> Internet
- **Expected User Symptom**: Internal domain names resolve correctly, but external websites do not.
- **Observed Show Commands**:
```text
DNS_Server# show access-lists
Extended IP access list OUTBOUND
 10 permit tcp any any eq www
 20 permit tcp any any eq 443
 30 deny ip any any

DNS_Server# show run int Gi0/1
interface GigabitEthernet0/1
 ip access-group OUTBOUND out
```
- **Expected Root Cause**: ACL permits HTTP/HTTPS but denies other IP traffic, which blocks DNS UDP traffic on port 53.
- **Recommended Fix**: Add permit udp any any eq 53 to extended access-list OUTBOUND on DNS router.
- **Verification Procedure**: show access-lists OUTBOUND and nslookup google.com from client

---

## NET-014 — DNS (Medium Severity)

- **Category Tag**: `DNS`
- **OSI Layer**: `Layer 3`
- **Severity**: `Medium`
- **Network Topology**: Host -> Router -> DNS Server (10.0.0.53)
- **Expected User Symptom**: Host fails to resolve names. DNS server is on a different subnet, routing is fine.
- **Observed Show Commands**:
```text
Host> ipconfig /all
DNS Servers . . . . . . . . . . . : 10.0.0.99

Router# show ip route
C 192.168.1.0 is directly connected, Gi0/0
C 10.0.0.0 is directly connected, Gi0/1

Host> ping 10.0.0.99
Request timed out.
```
- **Expected Root Cause**: The host is configured with an incorrect DNS server IP (10.0.0.99) instead of the actual DNS server (10.0.0.53).
- **Recommended Fix**: Correct static DNS server address on Host to 10.0.0.53.
- **Verification Procedure**: ipconfig /all on host and nslookup lab.local

---

## NET-015 — Routing (Critical Severity)

- **Category Tag**: `Routing`
- **OSI Layer**: `Layer 3`
- **Severity**: `Critical`
- **Network Topology**: Branch (192.168.1.0/24) -> R1 (172.16.0.1) -> R2 (172.16.0.2) -> HQ (10.0.0.0/24)
- **Expected User Symptom**: PC at branch office cannot reach the head office server subnet (10.0.0.0/24).
- **Observed Show Commands**:
```text
R1# show ip route
C 192.168.1.0/24 is directly connected
C 172.16.0.0/30 is directly connected
! Note: 10.0.0.0/24 is missing

R2# show ip route
C 10.0.0.0/24 is directly connected, Gi0/1
C 172.16.0.0/30 is directly connected, Gi0/0

R1# ping 10.0.0.10
.....
Success rate is 0 percent (0/5)
```
- **Expected Root Cause**: Missing static route to 10.0.0.0/24 on R1.
- **Recommended Fix**: Configure static route on R1: ip route 10.0.0.0 255.255.255.0 172.16.0.2.
- **Verification Procedure**: show ip route on R1 and ping 10.0.0.10 from R1

---

## NET-016 — Routing (Critical Severity)

- **Category Tag**: `Routing`
- **OSI Layer**: `Layer 3`
- **Severity**: `Critical`
- **Network Topology**: R1 (Gi0/0: 10.1.1.2) -> ISP Router (Gi0/0: 10.1.1.1)
- **Expected User Symptom**: Internet access is down for all users on R1.
- **Observed Show Commands**:
```text
R1# show running-config | include ip route
ip route 0.0.0.0 0.0.0.0 10.1.1.254

R1# show ip interface brief
Gi0/0  10.1.1.2  YES manual up up
```
- **Expected Root Cause**: Incorrect static default route next-hop (10.1.1.254 instead of 10.1.1.1).
- **Recommended Fix**: Reconfigure static default route on R1: ip route 0.0.0.0 0.0.0.0 10.1.1.1.
- **Verification Procedure**: show ip route on R1 and ping 10.1.1.1

---

## NET-017 — Routing (High Severity)

- **Category Tag**: `Routing`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: R1 (192.168.12.1) <-> R2 (192.168.12.2)
- **Expected User Symptom**: OSPF neighbor relationship is not forming between R1 and R2.
- **Observed Show Commands**:
```text
R1# show running-config | section ospf
router ospf 1
 network 10.0.0.0 0.0.0.255 area 0

R1# show ip interface brief
Gi0/0   192.168.12.1   YES manual up up

R2# show ip ospf neighbor
(no output)
```
- **Expected Root Cause**: Missing OSPF network command for the 192.168.12.0 network on R1.
- **Recommended Fix**: Add network 192.168.12.0 0.0.0.255 area 0 under router ospf 1 on R1.
- **Verification Procedure**: show ip ospf neighbor on R1 and R2

---

## NET-018 — Routing (High Severity)

- **Category Tag**: `Routing`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: R1 <-> R2
- **Expected User Symptom**: EIGRP routing table on R1 does not contain routes from R2.
- **Observed Show Commands**:
```text
R1# show ip protocols
Routing Protocol is 'eigrp 100'

R2# show ip protocols
Routing Protocol is 'eigrp 200'
```
- **Expected Root Cause**: EIGRP Autonomous System (AS) number mismatch (100 vs 200).
- **Recommended Fix**: Change EIGRP AS number on R2 to match R1 (router eigrp 100).
- **Verification Procedure**: show ip eigrp neighbors on R1

---

## NET-019 — Routing (Medium Severity)

- **Category Tag**: `Routing`
- **OSI Layer**: `Layer 3`
- **Severity**: `Medium`
- **Network Topology**: R1 (Gi0/1) <-> R2 (Gi0/1)
- **Expected User Symptom**: R2 receives no RIP updates from R1 on their connecting link Gi0/1.
- **Observed Show Commands**:
```text
R1# show running-config | section router rip
router rip
 version 2
 passive-interface GigabitEthernet0/1
 network 10.0.0.0
 network 192.168.1.0
```
- **Expected Root Cause**: Passive-interface is incorrectly configured on the link connecting to R2 (Gi0/1).
- **Recommended Fix**: Remove passive-interface GigabitEthernet0/1 under router rip process on R1.
- **Verification Procedure**: show ip route rip on R2

---

## NET-020 — ACL (High Severity)

- **Category Tag**: `ACL`
- **OSI Layer**: `Layer 4`
- **Severity**: `High`
- **Network Topology**: Users -> R1 (Gi0/1) -> Web Server
- **Expected User Symptom**: Users on 192.168.1.0 cannot access the web server at 10.0.0.80 over HTTP.
- **Observed Show Commands**:
```text
R1# show access-lists
Extended IP access list 101
 10 deny tcp 192.168.1.0 0.0.0.255 host 10.0.0.80 eq www (15 matches)
 20 permit ip any any

R1# show ip interface Gi0/1
  Outgoing access list is 101
```
- **Expected Root Cause**: ACL 101 is applied outbound on Gi0/1 and explicitly denies HTTP traffic from the user subnet to the web server.
- **Recommended Fix**: Modify ACL 101 to permit TCP port 80 traffic to 10.0.0.80 or remove deny entry 10.
- **Verification Procedure**: show access-lists 101 and HTTP query to 10.0.0.80

---

## NET-021 — ACL (Medium Severity)

- **Category Tag**: `ACL`
- **OSI Layer**: `Layer 3`
- **Severity**: `Medium`
- **Network Topology**: PC1 -> R1 (Gi0/0) -> Internet. Printer is on R1 Gi0/0.
- **Expected User Symptom**: PC1 (10.1.1.10) cannot reach the Internet, but it CAN reach the local printer (10.1.1.20).
- **Observed Show Commands**:
```text
R1# show access-lists 1
Standard IP access list 1
 10 deny 10.1.1.10
 20 permit any

R1# show running-config interface Gi0/0
interface GigabitEthernet0/0
 ip access-group 1 in
```
- **Expected Root Cause**: Standard ACL 1 is applied closest to the source (Gi0/0 in), blocking PC1 from reaching all other networks instead of just a specific destination.
- **Recommended Fix**: Remove ip access-group 1 in from Gi0/0 and apply specific extended ACL closer to destination.
- **Verification Procedure**: show ip interface Gi0/0 and ping 8.8.8.8 from PC1

---

## NET-022 — ACL (High Severity)

- **Category Tag**: `ACL`
- **OSI Layer**: `Layer 4`
- **Severity**: `High`
- **Network Topology**: Internet -> R1 (Gi0/0) -> Jump Server
- **Expected User Symptom**: External SSH access to the admin jump server (192.168.50.5) is failing.
- **Observed Show Commands**:
```text
R1# show access-lists 110
Extended IP access list 110
 10 permit tcp host 192.168.50.5 any eq 22  ! Incorrect
 ! Intended: permit tcp any host 192.168.50.5 eq 22
 20 deny ip any any

R1# show ip interface Gi0/0
  Inbound access list is 110
```
- **Expected Root Cause**: Extended ACL 110 has the source and destination IP/ports reversed for inbound traffic.
- **Recommended Fix**: Update entry 10 in ACL 110 to permit tcp any host 192.168.50.5 eq 22.
- **Verification Procedure**: show access-lists 110 and test SSH connection

---

## NET-023 — ACL (Medium Severity)

- **Category Tag**: `ACL`
- **OSI Layer**: `Layer 3`
- **Severity**: `Medium`
- **Network Topology**: Internal -> R1 (Gi0/1) -> (Gi0/0) External
- **Expected User Symptom**: Ping from internal network to external server fails. ACL 100 is designed to block external pings inbound.
- **Observed Show Commands**:
```text
R1# show running-config interface Gi0/1
interface GigabitEthernet0/1
 ip access-group 100 in

R1# show access-lists 100
Extended IP access list 100
 10 deny icmp any any echo-request
 20 permit ip any any
```
- **Expected Root Cause**: ACL 100 is applied in the wrong direction or wrong interface (applied IN on the internal interface instead of IN on external).
- **Recommended Fix**: Remove access-group 100 from Gi0/1 and apply ip access-group 100 in on external interface Gi0/0.
- **Verification Procedure**: show ip interface Gi0/1 and ping external IP from internal PC

---

## NET-024 — NAT (High Severity)

- **Category Tag**: `NAT`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: Internal (Gi0/1) -> R1 -> External (Gi0/0)
- **Expected User Symptom**: Internal users cannot reach the internet. NAT overload is configured.
- **Observed Show Commands**:
```text
R1# show running-config | include ip nat
ip nat inside source list 1 interface GigabitEthernet0/0 overload

R1# show running-config interface Gi0/0
interface GigabitEthernet0/0
 ip nat outside

R1# show running-config interface Gi0/1
interface GigabitEthernet0/1
 ! Missing ip nat inside
```
- **Expected Root Cause**: Missing 'ip nat inside' command on the internal interface Gi0/1.
- **Recommended Fix**: Add ip nat inside to interface GigabitEthernet0/1 configuration on R1.
- **Verification Procedure**: show running-config interface Gi0/1 and show ip nat translations

---

## NET-025 — NAT (High Severity)

- **Category Tag**: `NAT`
- **OSI Layer**: `Layer 4`
- **Severity**: `High`
- **Network Topology**: Internal -> R1 -> Internet
- **Expected User Symptom**: Only one internal user can access the internet at a time.
- **Observed Show Commands**:
```text
R1# show running-config | include ip nat inside source
ip nat inside source list 1 interface GigabitEthernet0/0

R1# show ip nat translations
Pro Inside global      Inside local       Outside local      Outside global
tcp 203.0.113.1:80     192.168.1.10:80    198.51.100.1:80    198.51.100.1:80
```
- **Expected Root Cause**: The 'overload' keyword is missing from the NAT configuration, preventing PAT.
- **Recommended Fix**: Reconfigure NAT rule to include overload: ip nat inside source list 1 interface Gi0/0 overload.
- **Verification Procedure**: show ip nat translations with multiple internal users

---

## NET-026 — NAT (Medium Severity)

- **Category Tag**: `NAT`
- **OSI Layer**: `Layer 3`
- **Severity**: `Medium`
- **Network Topology**: VLAN 10/20 -> R1 -> Internet
- **Expected User Symptom**: Users on the new VLAN 20 (192.168.20.0/24) cannot reach the internet, while VLAN 10 users can.
- **Observed Show Commands**:
```text
R1# show access-lists 1
Standard IP access list 1
 10 permit 192.168.10.0, wildcard bits 0.0.0.255

R1# show running-config | include nat
ip nat inside source list 1 interface Gi0/0 overload
```
- **Expected Root Cause**: The NAT ACL (list 1) does not permit the new VLAN 20 subnet.
- **Recommended Fix**: Add access-list 1 permit 192.168.20.0 0.0.0.255 to NAT ACL on R1.
- **Verification Procedure**: show access-lists 1 and ping external IP from VLAN 20 PC

---

## NET-027 — Wireless (High Severity)

- **Category Tag**: `Wireless`
- **OSI Layer**: `Layer 2`
- **Severity**: `High`
- **Network Topology**: WLC -> SW1. Guest WLAN should be VLAN 50.
- **Expected User Symptom**: Wireless clients connect to the 'Guest' SSID but receive IPs from the Corporate VLAN (VLAN 10).
- **Observed Show Commands**:
```text
WLC> show wlan 2
WLAN Identifier.................................. 2
Profile Name..................................... Guest
Network Name (SSID).............................. Guest
Interface........................................ management (VLAN 10)
```
- **Expected Root Cause**: Guest WLAN is incorrectly mapped to the management interface/VLAN 10 instead of the Guest dynamic interface/VLAN 50.
- **Recommended Fix**: Update WLAN 2 interface mapping on WLC to dynamic interface Guest-VLAN50.
- **Verification Procedure**: show wlan 2 on WLC and ipconfig on guest client

---

## NET-028 — Wireless (Medium Severity)

- **Category Tag**: `Wireless`
- **OSI Layer**: `Layer 2`
- **Severity**: `Medium`
- **Network Topology**: Laptop -> AP -> WLC
- **Expected User Symptom**: Clients cannot join the 'CorpWiFi' SSID. They are prompted for a username/password but expect a PSK.
- **Observed Show Commands**:
```text
WLC> show wlan 1
WLAN Identifier.................................. 1
Profile Name..................................... CorpWiFi
Security Policies:
 WPA2 Encryption.............................. AES
 Auth Key Management.......................... 802.1x

Laptop (User Report):
'I am typing the pre-shared key but it fails.'
```
- **Expected Root Cause**: WLAN is configured for 802.1x (Enterprise) authentication, but the user is expecting a WPA2 PSK.
- **Recommended Fix**: Change WLAN 1 Layer 2 security Auth Key Management to PSK and enter pre-shared key.
- **Verification Procedure**: show wlan 1 on WLC

---

## NET-029 — Wireless (Medium Severity)

- **Category Tag**: `Wireless`
- **OSI Layer**: `Layer 7`
- **Severity**: `Medium`
- **Network Topology**: Guest Laptop -> Lightweight AP -> WLC (DHCP Server)
- **Expected User Symptom**: Wireless clients connecting to 'Guest-Net' fail to obtain IP address from DHCP server on WLC.
- **Observed Show Commands**:
```text
WLC> show dhcp summary
Scope Name: GuestPool
Network: 172.16.50.0/24
Default Router: 172.16.50.254
Status: Disabled
```
- **Expected Root Cause**: Internal DHCP scope for Guest wireless clients is administratively disabled on Wireless LAN Controller.
- **Recommended Fix**: Enable DHCP scope GuestPool on WLC with config dhcp scope enable GuestPool.
- **Verification Procedure**: show dhcp summary on WLC and ipconfig /renew on guest client

---

## NET-030 — Wireless (High Severity)

- **Category Tag**: `Wireless`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: Guest Laptop -> AP -> WLC -> Core Switch -> Corporate Server (10.0.0.10)
- **Expected User Symptom**: Guest Wi-Fi users connected to 'Guest-WiFi' can reach sensitive internal corporate server (10.0.0.10).
- **Observed Show Commands**:
```text
WLC> show wlan 3
SSID: Guest-WiFi
Interface: guest-vlan50
Client ACL: None

Core Switch# show access-lists GUEST_BLOCK
Extended IP access list GUEST_BLOCK
 10 deny ip 172.16.50.0 0.0.0.255 10.0.0.0 0.255.255.255
 20 permit ip any any

Core Switch# show ip interface Vlan50
 Inbound access list is Not set
```
- **Expected Root Cause**: Guest isolation ACL GUEST_BLOCK is created on Core Switch but not applied inbound on interface Vlan50.
- **Recommended Fix**: Apply ACL inbound on Vlan50 interface (interface Vlan50, ip access-group GUEST_BLOCK in).
- **Verification Procedure**: show ip interface Vlan50 and ping 10.0.0.10 from guest host

---

## NET-031 — VLAN (Medium Severity)

- **Category Tag**: `VLAN`
- **OSI Layer**: `Layer 2`
- **Severity**: `Medium`
- **Network Topology**: Host_C -> SW1 (Fa0/5) -> Trunk -> Core Router
- **Expected User Symptom**: Host connected to SW1 Fa0/5 cannot communicate with other devices in VLAN 20.
- **Observed Show Commands**:
```text
SW1# show vlan brief
1    default          active    Fa0/1, Fa0/5
20   SERVERS          active    Fa0/2, Fa0/3

SW1# show interfaces Fa0/5 switchport
Name: Fa0/5
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Access Mode VLAN: 1 (default)
```
- **Expected Root Cause**: Interface Fa0/5 on SW1 is assigned to default VLAN 1 instead of VLAN 20.
- **Recommended Fix**: Configure switchport access vlan 20 on interface Fa0/5 on SW1.
- **Verification Procedure**: show interfaces Fa0/5 switchport on SW1

---

## NET-032 — Gateway (High Severity)

- **Category Tag**: `Gateway`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: VLAN 20 Hosts -> Switch -> Router (Gi0/0.20 subinterface)
- **Expected User Symptom**: Hosts on VLAN 20 cannot reach remote subnets via Router-on-a-Stick subinterface.
- **Observed Show Commands**:
```text
Router# show running-config interface Gi0/0.20
interface GigabitEthernet0/0.20
 ip address 192.168.20.1 255.255.255.0
 ! Missing encapsulation dot1Q 20

Router# show ip interface brief
Gi0/0.20      192.168.20.1    YES manual up                    down
```
- **Expected Root Cause**: Subinterface Gi0/0.20 is missing encapsulation dot1Q 20, causing line protocol to remain down.
- **Recommended Fix**: Configure encapsulation dot1Q 20 under subinterface Gi0/0.20 on Router.
- **Verification Procedure**: show ip interface brief on Router

---

## NET-033 — DHCP (Medium Severity)

- **Category Tag**: `DHCP`
- **OSI Layer**: `Layer 7`
- **Severity**: `Medium`
- **Network Topology**: Branch PC -> Switch -> Branch Router (DHCP Server)
- **Expected User Symptom**: DHCP clients receive IP addresses in the 192.168.2.0/24 subnet instead of local 192.168.1.0/24 subnet.
- **Observed Show Commands**:
```text
Branch_Router# show running-config | section dhcp
ip dhcp pool BRANCH
 network 192.168.2.0 255.255.255.0
 default-router 192.168.1.1
 dns-server 8.8.8.8

Branch_Router# show ip interface brief
Gi0/0         192.168.1.1     YES manual up                    up
```
- **Expected Root Cause**: Network statement in DHCP pool is configured for the wrong subnet (192.168.2.0/24 instead of 192.168.1.0/24).
- **Recommended Fix**: Update DHCP pool network statement to network 192.168.1.0 255.255.255.0.
- **Verification Procedure**: ipconfig /renew on client PC

---

## NET-034 — DNS (Low Severity)

- **Category Tag**: `DNS`
- **OSI Layer**: `Layer 7`
- **Severity**: `Low`
- **Network Topology**: Router R1 -> ISP Router (8.8.8.8 reachable)
- **Expected User Symptom**: Cisco IOS Router fails to resolve domain names when using diagnostic commands like ping host.domain.com.
- **Observed Show Commands**:
```text
R1# show running-config | include ip domain
! No ip domain-name or ip name-server configured

R1# ping google.com
Translating "google.com"...domain server (255.255.255.255)
% Unrecognized host or address, or protocol not running.
```
- **Expected Root Cause**: DNS domain lookup and name-server IP (8.8.8.8) are not configured on router R1.
- **Recommended Fix**: Configure ip domain-lookup and ip name-server 8.8.8.8 on router R1.
- **Verification Procedure**: ping google.com from R1

---

## NET-035 — NAT (High Severity)

- **Category Tag**: `NAT`
- **OSI Layer**: `Layer 3`
- **Severity**: `High`
- **Network Topology**: External Client -> Router R1 (Public IP 203.0.113.10) -> Web Server (192.168.1.100)
- **Expected User Symptom**: External web clients cannot access internal web server at 192.168.1.100 via public IP 203.0.113.10.
- **Observed Show Commands**:
```text
R1# show running-config | include ip nat inside source static
ip nat inside source static 192.168.1.50 203.0.113.10

R1# show ip interface brief
Gi0/0         203.0.113.10    YES manual up                    up
Gi0/1         192.168.1.1     YES manual up                    up

Server# ipconfig
IPv4 Address: 192.168.1.100
```
- **Expected Root Cause**: Static NAT rule maps public IP 203.0.113.10 to incorrect internal IP address (192.168.1.50 instead of 192.168.1.100).
- **Recommended Fix**: Update static NAT rule: ip nat inside source static 192.168.1.100 203.0.113.10.
- **Verification Procedure**: show ip nat translations and HTTP query to 203.0.113.10

---


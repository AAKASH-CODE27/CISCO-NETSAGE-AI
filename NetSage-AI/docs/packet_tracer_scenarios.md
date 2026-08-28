# Packet Tracer Scenarios

## NET-001 - VLAN
- **Category:** VLAN
- **Network Topology:** PC1 -> SW1 -> SW2 -> PC2
- **Intentional Fault:** PC1 and PC2 are assigned to different VLANs (10 and 20) on their respective access ports.
- **Expected User Symptom:** PC1 cannot ping PC2. Both are in the same department but connected to different switches.
- **Expected Evidence:** 
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
- **Expected Correct Diagnosis:** The issue is a VLAN problem at Layer 2. Specifically, PC1 and PC2 are assigned to different VLANs (10 and 20) on their respective access ports.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-002 - VLAN
- **Category:** VLAN
- **Network Topology:** PC -> SW1 (Fa0/2)
- **Intentional Fault:** VLAN 10 is configured on the access port but missing from the VLAN database.
- **Expected User Symptom:** New PC connected to SW1 Fa0/2 cannot reach the network.
- **Expected Evidence:** 
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
- **Expected Correct Diagnosis:** The issue is a VLAN problem at Layer 2. Specifically, VLAN 10 is configured on the access port but missing from the VLAN database.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-003 - VLAN
- **Category:** VLAN
- **Network Topology:** SW_A -> trunk -> SW_B
- **Intentional Fault:** VLAN 30 is not allowed on the trunk link on Switch B.
- **Expected User Symptom:** Traffic from VLAN 30 cannot cross between Switch A and Switch B. Other VLANs work fine.
- **Expected Evidence:** 
```text
SW_A# show interfaces trunk
Port        Vlans allowed on trunk
Gi0/1       10,20,30

SW_B# show interfaces trunk
Port        Vlans allowed on trunk
Gi0/1       10,20
```
- **Expected Correct Diagnosis:** The issue is a VLAN problem at Layer 2. Specifically, VLAN 30 is not allowed on the trunk link on Switch B.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-004 - VLAN
- **Category:** VLAN
- **Network Topology:** SW1 (Gi0/1) -> SW2 (Gi0/1)
- **Intentional Fault:** Native VLAN mismatch across the trunk link (99 vs 1).
- **Expected User Symptom:** CDP messages indicate a 'Native VLAN mismatch' on the trunk between SW1 and SW2.
- **Expected Evidence:** 
```text
SW1# show interfaces Gi0/1 switchport
Trunking Native Mode VLAN: 99 (Management)

SW2# show interfaces Gi0/1 switchport
Trunking Native Mode VLAN: 1 (default)
```
- **Expected Correct Diagnosis:** The issue is a VLAN problem at Layer 2. Specifically, Native VLAN mismatch across the trunk link (99 vs 1).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-005 - Gateway
- **Category:** Gateway
- **Network Topology:** PC1 (192.168.1.50) -> SW1 -> R1 (192.168.1.1)
- **Intentional Fault:** Incorrect default gateway configured on PC1 (192.168.1.254 instead of 192.168.1.1).
- **Expected User Symptom:** PC1 can ping other PCs in its subnet but cannot reach the internet or other subnets.
- **Expected Evidence:** 
```text
C:\> ipconfig
IPv4 Address: 192.168.1.50
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.1.254

R1# show ip interface brief
GigabitEthernet0/0     192.168.1.1     YES manual up                    up
```
- **Expected Correct Diagnosis:** The issue is a Gateway problem at Layer 3. Specifically, Incorrect default gateway configured on PC1 (192.168.1.254 instead of 192.168.1.1).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-006 - Interface/connectivity
- **Category:** Interface/connectivity
- **Network Topology:** Branch PCs -> SW -> R_Branch (Gi0/0)
- **Intentional Fault:** The gateway interface (Gi0/0) on the branch router is administratively down.
- **Expected User Symptom:** Entire branch office cannot access the main headquarters network.
- **Expected Evidence:** 
```text
R_Branch# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.1.1.1        YES manual administratively down down
GigabitEthernet0/1     192.168.100.1   YES manual up                    up
```
- **Expected Correct Diagnosis:** The issue is a Interface/connectivity problem at Layer 1. Specifically, The gateway interface (Gi0/0) on the branch router is administratively down.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-007 - Gateway
- **Category:** Gateway
- **Network Topology:** Server (10.0.0.10/24) -> Router (10.0.1.1/24)
- **Intentional Fault:** Server's default gateway is on a different subnet (10.0.1.x) than the server's IP (10.0.0.x).
- **Expected User Symptom:** Server cannot reach external networks despite seemingly correct IP settings.
- **Expected Evidence:** 
```text
Server# ipconfig
IPv4 Address: 10.0.0.10
Subnet Mask: 255.255.255.0
Default Gateway: 10.0.1.1

Router# show running-config interface Gi0/0
interface GigabitEthernet0/0
 ip address 10.0.1.1 255.255.255.0
```
- **Expected Correct Diagnosis:** The issue is a Gateway problem at Layer 3. Specifically, Server's default gateway is on a different subnet (10.0.1.x) than the server's IP (10.0.0.x).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-008 - DHCP
- **Category:** DHCP
- **Network Topology:** Clients -> SW1 -> R1 (DHCP Server)
- **Intentional Fault:** DHCP pool is exhausted; 50/50 addresses are leased.
- **Expected User Symptom:** New clients connecting to the network fail to get an IP address and receive APIPA addresses instead.
- **Expected Evidence:** 
```text
R1# show ip dhcp pool LAN
Pool LAN :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0
 Total addresses                : 50
 Leased addresses               : 50
 Pending event                  : none
```
- **Expected Correct Diagnosis:** The issue is a DHCP problem at Layer 7. Specifically, DHCP pool is exhausted; 50/50 addresses are leased.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-009 - DHCP
- **Category:** DHCP
- **Network Topology:** PCs -> SW1 -> R1 (DHCP)
- **Intentional Fault:** Incorrect default-router in DHCP pool (192.168.20.1 instead of 192.168.10.1).
- **Expected User Symptom:** PCs receive DHCP IP addresses but cannot route traffic off the local subnet.
- **Expected Evidence:** 
```text
R1# show running-config | section dhcp
ip dhcp pool OFFICE
 network 192.168.10.0 255.255.255.0
 default-router 192.168.20.1
 dns-server 8.8.8.8

R1# show ip interface brief
Gi0/0    192.168.10.1    YES manual up    up
```
- **Expected Correct Diagnosis:** The issue is a DHCP problem at Layer 7. Specifically, Incorrect default-router in DHCP pool (192.168.20.1 instead of 192.168.10.1).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-010 - DHCP
- **Category:** DHCP
- **Network Topology:** VLAN 20 Clients -> SW (L3) -> DHCP Server (VLAN 10)
- **Intentional Fault:** Missing ip helper-address on the VLAN 20 interface to forward DHCP broadcasts.
- **Expected User Symptom:** Clients on VLAN 20 do not get an IP address. DHCP server is on VLAN 10.
- **Expected Evidence:** 
```text
SW# show running-config interface Vlan20
interface Vlan20
 ip address 10.0.20.1 255.255.255.0
 ! Missing helper-address

SW# show running-config interface Vlan10
interface Vlan10
 ip address 10.0.10.1 255.255.255.0
```
- **Expected Correct Diagnosis:** The issue is a DHCP problem at Layer 3. Specifically, Missing ip helper-address on the VLAN 20 interface to forward DHCP broadcasts.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-011 - DHCP
- **Category:** DHCP
- **Network Topology:** Router provides DHCP for its own attached subnet.
- **Intentional Fault:** Router IP (192.168.1.1) is not excluded from the DHCP pool, causing conflicts.
- **Expected User Symptom:** Occasional IP conflict warnings on the network. Router interfaces sometimes unreachable.
- **Expected Evidence:** 
```text
Router# show running-config | include dhcp
ip dhcp pool LOCAL
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1

Router# show ip dhcp conflict
IP address        Detection method   Detection time          VRF
192.168.1.1       Ping               Mar 01 2026 10:00 AM
```
- **Expected Correct Diagnosis:** The issue is a DHCP problem at Layer 7. Specifically, Router IP (192.168.1.1) is not excluded from the DHCP pool, causing conflicts.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-012 - DNS
- **Category:** DNS
- **Network Topology:** Users -> Router -> ISP
- **Intentional Fault:** Incorrect DNS server (127.0.0.1) configured via DHCP or statically.
- **Expected User Symptom:** Users can ping 8.8.8.8 but cannot browse websites by name.
- **Expected Evidence:** 
```text
C:\> ping 8.8.8.8
Reply from 8.8.8.8: bytes=32 time=20ms TTL=115

C:\> ipconfig /all
DNS Servers . . . . . . . . . . . : 127.0.0.1
```
- **Expected Correct Diagnosis:** The issue is a DNS problem at Layer 7. Specifically, Incorrect DNS server (127.0.0.1) configured via DHCP or statically.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-013 - DNS
- **Category:** DNS
- **Network Topology:** PC -> Internal DNS Server -> Internet
- **Intentional Fault:** ACL permits HTTP/HTTPS but denies other IP traffic, which blocks DNS UDP traffic on port 53.
- **Expected User Symptom:** Internal domain names resolve correctly, but external websites do not.
- **Expected Evidence:** 
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
- **Expected Correct Diagnosis:** The issue is a DNS problem at Layer 4. Specifically, ACL permits HTTP/HTTPS but denies other IP traffic, which blocks DNS UDP traffic on port 53.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-014 - DNS
- **Category:** DNS
- **Network Topology:** Host -> Router -> DNS Server (10.0.0.53)
- **Intentional Fault:** The host is configured with an incorrect DNS server IP (10.0.0.99) instead of the actual DNS server (10.0.0.53).
- **Expected User Symptom:** Host fails to resolve names. DNS server is on a different subnet, routing is fine.
- **Expected Evidence:** 
```text
Host> ipconfig /all
DNS Servers . . . . . . . . . . . : 10.0.0.99

Router# show ip route
C 192.168.1.0 is directly connected, Gi0/0
C 10.0.0.0 is directly connected, Gi0/1

Host> ping 10.0.0.99
Request timed out.
```
- **Expected Correct Diagnosis:** The issue is a DNS problem at Layer 3. Specifically, The host is configured with an incorrect DNS server IP (10.0.0.99) instead of the actual DNS server (10.0.0.53).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-015 - Routing
- **Category:** Routing
- **Network Topology:** Branch (192.168.1.0/24) -> R1 (172.16.0.1) -> R2 (172.16.0.2) -> HQ (10.0.0.0/24)
- **Intentional Fault:** Missing static route to 10.0.0.0/24 on R1.
- **Expected User Symptom:** PC at branch office cannot reach the head office server subnet (10.0.0.0/24).
- **Expected Evidence:** 
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
- **Expected Correct Diagnosis:** The issue is a Routing problem at Layer 3. Specifically, Missing static route to 10.0.0.0/24 on R1.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-016 - Routing
- **Category:** Routing
- **Network Topology:** R1 (Gi0/0: 10.1.1.2) -> ISP Router (Gi0/0: 10.1.1.1)
- **Intentional Fault:** Incorrect static default route next-hop (10.1.1.254 instead of 10.1.1.1).
- **Expected User Symptom:** Internet access is down for all users on R1.
- **Expected Evidence:** 
```text
R1# show running-config | include ip route
ip route 0.0.0.0 0.0.0.0 10.1.1.254

R1# show ip interface brief
Gi0/0  10.1.1.2  YES manual up up
```
- **Expected Correct Diagnosis:** The issue is a Routing problem at Layer 3. Specifically, Incorrect static default route next-hop (10.1.1.254 instead of 10.1.1.1).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-017 - Routing
- **Category:** Routing
- **Network Topology:** R1 (192.168.12.1) <-> R2 (192.168.12.2)
- **Intentional Fault:** Missing OSPF network command for the 192.168.12.0 network on R1.
- **Expected User Symptom:** OSPF neighbor relationship is not forming between R1 and R2.
- **Expected Evidence:** 
```text
R1# show running-config | section ospf
router ospf 1
 network 10.0.0.0 0.0.0.255 area 0

R1# show ip interface brief
Gi0/0   192.168.12.1   YES manual up up

R2# show ip ospf neighbor
(no output)
```
- **Expected Correct Diagnosis:** The issue is a Routing problem at Layer 3. Specifically, Missing OSPF network command for the 192.168.12.0 network on R1.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-018 - Routing
- **Category:** Routing
- **Network Topology:** R1 <-> R2
- **Intentional Fault:** EIGRP Autonomous System (AS) number mismatch (100 vs 200).
- **Expected User Symptom:** EIGRP routing table on R1 does not contain routes from R2.
- **Expected Evidence:** 
```text
R1# show ip protocols
Routing Protocol is 'eigrp 100'

R2# show ip protocols
Routing Protocol is 'eigrp 200'
```
- **Expected Correct Diagnosis:** The issue is a Routing problem at Layer 3. Specifically, EIGRP Autonomous System (AS) number mismatch (100 vs 200).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-019 - Routing
- **Category:** Routing
- **Network Topology:** R1 (Gi0/1) <-> R2 (Gi0/1)
- **Intentional Fault:** Passive-interface is incorrectly configured on the link connecting to R2 (Gi0/1).
- **Expected User Symptom:** R2 receives no RIP updates from R1 on their connecting link Gi0/1.
- **Expected Evidence:** 
```text
R1# show running-config | section router rip
router rip
 version 2
 passive-interface GigabitEthernet0/1
 network 10.0.0.0
 network 192.168.1.0
```
- **Expected Correct Diagnosis:** The issue is a Routing problem at Layer 3. Specifically, Passive-interface is incorrectly configured on the link connecting to R2 (Gi0/1).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-020 - ACL
- **Category:** ACL
- **Network Topology:** Users -> R1 (Gi0/1) -> Web Server
- **Intentional Fault:** ACL 101 is applied outbound on Gi0/1 and explicitly denies HTTP traffic from the user subnet to the web server.
- **Expected User Symptom:** Users on 192.168.1.0 cannot access the web server at 10.0.0.80 over HTTP.
- **Expected Evidence:** 
```text
R1# show access-lists
Extended IP access list 101
 10 deny tcp 192.168.1.0 0.0.0.255 host 10.0.0.80 eq www (15 matches)
 20 permit ip any any

R1# show ip interface Gi0/1
  Outgoing access list is 101
```
- **Expected Correct Diagnosis:** The issue is a ACL problem at Layer 4. Specifically, ACL 101 is applied outbound on Gi0/1 and explicitly denies HTTP traffic from the user subnet to the web server.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-021 - ACL
- **Category:** ACL
- **Network Topology:** PC1 -> R1 (Gi0/0) -> Internet. Printer is on R1 Gi0/0.
- **Intentional Fault:** Standard ACL 1 is applied closest to the source (Gi0/0 in), blocking PC1 from reaching all other networks instead of just a specific destination.
- **Expected User Symptom:** PC1 (10.1.1.10) cannot reach the Internet, but it CAN reach the local printer (10.1.1.20).
- **Expected Evidence:** 
```text
R1# show access-lists 1
Standard IP access list 1
 10 deny 10.1.1.10
 20 permit any

R1# show running-config interface Gi0/0
interface GigabitEthernet0/0
 ip access-group 1 in
```
- **Expected Correct Diagnosis:** The issue is a ACL problem at Layer 3. Specifically, Standard ACL 1 is applied closest to the source (Gi0/0 in), blocking PC1 from reaching all other networks instead of just a specific destination.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-022 - ACL
- **Category:** ACL
- **Network Topology:** Internet -> R1 (Gi0/0) -> Jump Server
- **Intentional Fault:** Extended ACL 110 has the source and destination IP/ports reversed for inbound traffic.
- **Expected User Symptom:** External SSH access to the admin jump server (192.168.50.5) is failing.
- **Expected Evidence:** 
```text
R1# show access-lists 110
Extended IP access list 110
 10 permit tcp host 192.168.50.5 any eq 22  ! Incorrect
 ! Intended: permit tcp any host 192.168.50.5 eq 22
 20 deny ip any any

R1# show ip interface Gi0/0
  Inbound access list is 110
```
- **Expected Correct Diagnosis:** The issue is a ACL problem at Layer 4. Specifically, Extended ACL 110 has the source and destination IP/ports reversed for inbound traffic.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-023 - ACL
- **Category:** ACL
- **Network Topology:** Internal -> R1 (Gi0/1) -> (Gi0/0) External
- **Intentional Fault:** ACL 100 is applied in the wrong direction or wrong interface (applied IN on the internal interface instead of IN on external).
- **Expected User Symptom:** Ping from internal network to external server fails. ACL 100 is designed to block external pings inbound.
- **Expected Evidence:** 
```text
R1# show running-config interface Gi0/1
interface GigabitEthernet0/1
 ip access-group 100 in

R1# show access-lists 100
Extended IP access list 100
 10 deny icmp any any echo-request
 20 permit ip any any
```
- **Expected Correct Diagnosis:** The issue is a ACL problem at Layer 3. Specifically, ACL 100 is applied in the wrong direction or wrong interface (applied IN on the internal interface instead of IN on external).
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-024 - NAT
- **Category:** NAT
- **Network Topology:** Internal (Gi0/1) -> R1 -> External (Gi0/0)
- **Intentional Fault:** Missing 'ip nat inside' command on the internal interface Gi0/1.
- **Expected User Symptom:** Internal users cannot reach the internet. NAT overload is configured.
- **Expected Evidence:** 
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
- **Expected Correct Diagnosis:** The issue is a NAT problem at Layer 3. Specifically, Missing 'ip nat inside' command on the internal interface Gi0/1.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-025 - NAT
- **Category:** NAT
- **Network Topology:** Internal -> R1 -> Internet
- **Intentional Fault:** The 'overload' keyword is missing from the NAT configuration, preventing PAT.
- **Expected User Symptom:** Only one internal user can access the internet at a time.
- **Expected Evidence:** 
```text
R1# show running-config | include ip nat inside source
ip nat inside source list 1 interface GigabitEthernet0/0

R1# show ip nat translations
Pro Inside global      Inside local       Outside local      Outside global
tcp 203.0.113.1:80     192.168.1.10:80    198.51.100.1:80    198.51.100.1:80
```
- **Expected Correct Diagnosis:** The issue is a NAT problem at Layer 4. Specifically, The 'overload' keyword is missing from the NAT configuration, preventing PAT.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-026 - NAT
- **Category:** NAT
- **Network Topology:** VLAN 10/20 -> R1 -> Internet
- **Intentional Fault:** The NAT ACL (list 1) does not permit the new VLAN 20 subnet.
- **Expected User Symptom:** Users on the new VLAN 20 (192.168.20.0/24) cannot reach the internet, while VLAN 10 users can.
- **Expected Evidence:** 
```text
R1# show access-lists 1
Standard IP access list 1
 10 permit 192.168.10.0, wildcard bits 0.0.0.255

R1# show running-config | include nat
ip nat inside source list 1 interface Gi0/0 overload
```
- **Expected Correct Diagnosis:** The issue is a NAT problem at Layer 3. Specifically, The NAT ACL (list 1) does not permit the new VLAN 20 subnet.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-027 - Wireless
- **Category:** Wireless
- **Network Topology:** WLC -> SW1. Guest WLAN should be VLAN 50.
- **Intentional Fault:** Guest WLAN is incorrectly mapped to the management interface/VLAN 10 instead of the Guest dynamic interface/VLAN 50.
- **Expected User Symptom:** Wireless clients connect to the 'Guest' SSID but receive IPs from the Corporate VLAN (VLAN 10).
- **Expected Evidence:** 
```text
WLC> show wlan 2
WLAN Identifier.................................. 2
Profile Name..................................... Guest
Network Name (SSID).............................. Guest
Interface........................................ management (VLAN 10)
```
- **Expected Correct Diagnosis:** The issue is a Wireless problem at Layer 2. Specifically, Guest WLAN is incorrectly mapped to the management interface/VLAN 10 instead of the Guest dynamic interface/VLAN 50.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-028 - Wireless
- **Category:** Wireless
- **Network Topology:** Laptop -> AP -> WLC
- **Intentional Fault:** WLAN is configured for 802.1x (Enterprise) authentication, but the user is expecting a WPA2 PSK.
- **Expected User Symptom:** Clients cannot join the 'CorpWiFi' SSID. They are prompted for a username/password but expect a PSK.
- **Expected Evidence:** 
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
- **Expected Correct Diagnosis:** The issue is a Wireless problem at Layer 2. Specifically, WLAN is configured for 802.1x (Enterprise) authentication, but the user is expecting a WPA2 PSK.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-029 - Interface/connectivity
- **Category:** Interface/connectivity
- **Network Topology:** SW1 (Gi0/24) -> R1 (Gi0/0)
- **Intentional Fault:** Port security violation triggered an err-disable state on the switchport.
- **Expected User Symptom:** Switch uplink to the router is physically connected but the link protocol shows down.
- **Expected Evidence:** 
```text
SW1# show interfaces Gi0/24
GigabitEthernet0/24 is up, line protocol is down (err-disabled)

SW1# show port-security interface Gi0/24
Port Security              : Enabled
Port Status                : Secure-down
Violation Mode             : Shutdown
```
- **Expected Correct Diagnosis:** The issue is a Interface/connectivity problem at Layer 2. Specifically, Port security violation triggered an err-disable state on the switchport.
- **Note:** Port security on the router uplink is an intentional lab scenario.
- **Verification Method:** Correct the configuration and verify connectivity.

## NET-030 - Interface/connectivity
- **Category:** Interface/connectivity
- **Network Topology:** SW1 (Fa0/1) -> R1 (Gi0/0)
- **Intentional Fault:** Speed/duplex mismatch between the switch (Half-duplex) and router (Full-duplex).
- **Expected User Symptom:** Performance between the switch and router is extremely slow, and there are many late collisions.
- **Expected Evidence:** 
```text
SW1# show interfaces Fa0/1
FastEthernet0/1 is up, line protocol is up
  Half-duplex, 100Mb/s
  0 runts, 0 giants, 0 throttles
  4560 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored

R1# show interfaces Gi0/0
GigabitEthernet0/0 is up, line protocol is up
  Full-duplex, 100Mb/s
```
- **Expected Correct Diagnosis:** The issue is a Interface/connectivity problem at Layer 1. Specifically, Speed/duplex mismatch between the switch (Half-duplex) and router (Full-duplex).
- **Verification Method:** Correct the configuration and verify connectivity.


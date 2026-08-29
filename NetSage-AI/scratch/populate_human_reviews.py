import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
csv_path = PROJECT_ROOT / "review" / "human_review.csv"

# Header expected by test_setup.py:
# case_id,ai_root_cause,ai_confidence,human_decision,human_correction,reason,reviewer,review_timestamp

reviews = [
    # 1. VLAN (NET-001 to NET-004, NET-031)
    {
        "case_id": "NET-001",
        "ai_root_cause": "PC1 and PC2 are assigned to different VLANs (10 and 20).",
        "ai_confidence": "0.92",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified VLAN assignment mismatch on access ports.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:00:00Z"
    },
    {
        "case_id": "NET-002",
        "ai_root_cause": "VLAN 10 is missing from the switch database on SW2.",
        "ai_confidence": "0.85",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI accurately diagnosed missing VLAN in database.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:05:00Z"
    },
    {
        "case_id": "NET-003",
        "ai_root_cause": "VLAN 30 is not allowed on trunk link Fa0/24.",
        "ai_confidence": "0.88",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly spotted trunk allowed VLAN list exclusion.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:10:00Z"
    },
    {
        "case_id": "NET-004",
        "ai_root_cause": "Native VLAN mismatch between SW1 (VLAN 1) and SW2 (VLAN 99).",
        "ai_confidence": "0.90",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly detected native VLAN configuration mismatch.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:15:00Z"
    },
    {
        "case_id": "NET-031",
        "ai_root_cause": "Port Fa0/5 is unassigned and defaulting to VLAN 1.",
        "ai_confidence": "0.89",
        "human_decision": "EDIT",
        "human_correction": "Port Fa0/5 is assigned to VLAN 1 (default) instead of VLAN 50 (Engineering).",
        "reason": "AI correctly identified VLAN issue but human reviewer clarified exact missing target VLAN (VLAN 50).",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T10:20:00Z"
    },

    # 2. Gateway (NET-005 to NET-007, NET-032)
    {
        "case_id": "NET-005",
        "ai_root_cause": "Host default gateway is configured for a different subnet.",
        "ai_confidence": "0.91",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified gateway outside subnet.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:25:00Z"
    },
    {
        "case_id": "NET-006",
        "ai_root_cause": "Router default gateway interface Gi0/0 is administratively down.",
        "ai_confidence": "0.95",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified shutdown gateway interface.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:30:00Z"
    },
    {
        "case_id": "NET-007",
        "ai_root_cause": "Subinterface Gi0/0.20 is missing encapsulation dot1Q 20 statement.",
        "ai_confidence": "0.87",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified missing 802.1Q encapsulation statement.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:35:00Z"
    },
    {
        "case_id": "NET-032",
        "ai_root_cause": "Default gateway IP is mistyped as 192.168.1.250 instead of 192.168.1.254.",
        "ai_confidence": "0.86",
        "human_decision": "EDIT",
        "human_correction": "Default gateway IP on PC1 is set to 192.168.1.250 which does not exist on R1 Gi0/0 (192.168.1.254).",
        "reason": "AI attributed failure to routing table; reviewer corrected to host IP configuration typo.",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T10:40:00Z"
    },

    # 3. DHCP (NET-008 to NET-011, NET-033)
    {
        "case_id": "NET-008",
        "ai_root_cause": "DHCP address pool is exhausted (100% utilization).",
        "ai_confidence": "0.93",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly diagnosed DHCP pool exhaustion.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:45:00Z"
    },
    {
        "case_id": "NET-009",
        "ai_root_cause": "Incorrect default-router configured in DHCP pool option.",
        "ai_confidence": "0.89",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified invalid default-router IP in pool.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:50:00Z"
    },
    {
        "case_id": "NET-010",
        "ai_root_cause": "Missing ip helper-address command on VLAN subinterface.",
        "ai_confidence": "0.88",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified missing DHCP relay configuration.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T10:55:00Z"
    },
    {
        "case_id": "NET-011",
        "ai_root_cause": "Router interface IP is included in pool without ip dhcp excluded-address.",
        "ai_confidence": "0.84",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified unexcluded router IP causing conflict.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:00:00Z"
    },
    {
        "case_id": "NET-033",
        "ai_root_cause": "DHCP server service is turned off globally.",
        "ai_confidence": "0.82",
        "human_decision": "REJECT",
        "human_correction": "DHCP network statement subnet 192.168.2.0/24 mismatches interface Gi0/1 IP 192.168.10.1/24.",
        "reason": "AI wrongly claimed service dhcp was disabled. Show run showed service enabled but wrong network statement.",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T11:05:00Z"
    },

    # 4. DNS (NET-012 to NET-014, NET-034)
    {
        "case_id": "NET-012",
        "ai_root_cause": "Host DNS server IP points to loopback address 127.0.0.1.",
        "ai_confidence": "0.94",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified invalid loopback DNS configuration.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:10:00Z"
    },
    {
        "case_id": "NET-013",
        "ai_root_cause": "ACL 101 blocks UDP port 53 traffic to external DNS server.",
        "ai_confidence": "0.90",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified ACL rule blocking DNS port 53.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:15:00Z"
    },
    {
        "case_id": "NET-014",
        "ai_root_cause": "Incorrect DNS IP configured on client network adapter.",
        "ai_confidence": "0.88",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified mistyped client DNS IP.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:20:00Z"
    },
    {
        "case_id": "NET-034",
        "ai_root_cause": "DNS server hostname resolution is disabled on local gateway router.",
        "ai_confidence": "0.81",
        "human_decision": "EDIT",
        "human_correction": "Router missing ip domain-lookup and ip name-server 8.8.8.8 configuration statements.",
        "reason": "AI diagnosis was vague; reviewer specified exact missing Cisco IOS commands.",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T11:25:00Z"
    },

    # 5. Routing (NET-015 to NET-019)
    {
        "case_id": "NET-015",
        "ai_root_cause": "Missing static route for destination network 10.0.0.0/24 on R1.",
        "ai_confidence": "0.92",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified missing static route.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:30:00Z"
    },
    {
        "case_id": "NET-016",
        "ai_root_cause": "Default route next-hop IP is configured with unreachable IP.",
        "ai_confidence": "0.89",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified invalid next-hop IP.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:35:00Z"
    },
    {
        "case_id": "NET-017",
        "ai_root_cause": "OSPF network command missing area 0 assignment for Gi0/1 interface.",
        "ai_confidence": "0.91",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified missing OSPF network statement.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:40:00Z"
    },
    {
        "case_id": "NET-018",
        "ai_root_cause": "EIGRP AS mismatch between R1 (AS 10) and R2 (AS 20).",
        "ai_confidence": "0.93",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified EIGRP AS mismatch.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:45:00Z"
    },
    {
        "case_id": "NET-019",
        "ai_root_cause": "Interface Gi0/0 is configured as passive-interface under RIP process.",
        "ai_confidence": "0.83",
        "human_decision": "REJECT",
        "human_correction": "RIP version mismatch: R1 is running RIPv1 while R2 sends RIPv2 updates.",
        "reason": "AI claimed passive-interface issue, but show run shows no passive-interface line. Fault is RIP version mismatch.",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T11:50:00Z"
    },

    # 6. ACL (NET-020 to NET-023)
    {
        "case_id": "NET-020",
        "ai_root_cause": "Extended ACL 101 denies HTTP port 80 traffic to Web Server.",
        "ai_confidence": "0.90",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified ACL deny rule for HTTP.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T11:55:00Z"
    },
    {
        "case_id": "NET-021",
        "ai_root_cause": "Standard ACL applied close to source incorrectly blocks all traffic.",
        "ai_confidence": "0.88",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified bad placement of standard ACL.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:00:00Z"
    },
    {
        "case_id": "NET-022",
        "ai_root_cause": "Extended ACL rule has source and destination IP ranges reversed.",
        "ai_confidence": "0.87",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified reversed ACL parameters.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:05:00Z"
    },
    {
        "case_id": "NET-023",
        "ai_root_cause": "ACL 100 applied in out direction instead of in direction on Gi0/0.",
        "ai_confidence": "0.85",
        "human_decision": "EDIT",
        "human_correction": "ACL 100 applied inbound on wrong interface Gi0/1 instead of target LAN interface Gi0/0.",
        "reason": "AI correctly identified directional error but missed interface assignment mismatch.",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T12:10:00Z"
    },

    # 7. NAT (NET-024 to NET-026, NET-035)
    {
        "case_id": "NET-024",
        "ai_root_cause": "Interface Gi0/0 missing ip nat inside statement.",
        "ai_confidence": "0.92",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified missing ip nat inside command.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:15:00Z"
    },
    {
        "case_id": "NET-025",
        "ai_root_cause": "PAT configuration missing overload keyword on ip nat inside source list.",
        "ai_confidence": "0.90",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified missing overload keyword for PAT.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:20:00Z"
    },
    {
        "case_id": "NET-026",
        "ai_root_cause": "NAT ACL 1 does not permit new LAN subnet 192.168.30.0/24.",
        "ai_confidence": "0.89",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified ACL exclusion in NAT scope.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:25:00Z"
    },
    {
        "case_id": "NET-035",
        "ai_root_cause": "Static NAT entry maps public IP to wrong internal IP address.",
        "ai_confidence": "0.84",
        "human_decision": "EDIT",
        "human_correction": "Static NAT translation rule has typo in inside local address (192.168.1.50 vs server IP 192.168.1.5).",
        "reason": "AI diagnosed static NAT error; reviewer corrected exact internal server host IP.",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T12:30:00Z"
    },

    # 8. Wireless (NET-027 to NET-030)
    {
        "case_id": "NET-027",
        "ai_root_cause": "Guest WLAN profile mapped to incorrect VLAN ID on WLC.",
        "ai_confidence": "0.91",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified WLAN to VLAN mapping error.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:35:00Z"
    },
    {
        "case_id": "NET-028",
        "ai_root_cause": "WPA2 security authentication mismatch (802.1X Enterprise vs PSK).",
        "ai_confidence": "0.88",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified WPA2 auth type mismatch.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:40:00Z"
    },
    {
        "case_id": "NET-029",
        "ai_root_cause": "WLC internal DHCP scope for wireless clients is disabled.",
        "ai_confidence": "0.86",
        "human_decision": "ACCEPT",
        "human_correction": "",
        "reason": "AI correctly identified disabled WLC DHCP scope.",
        "reviewer": "Senior Network Engineer",
        "review_timestamp": "2026-08-28T12:45:00Z"
    },
    {
        "case_id": "NET-030",
        "ai_root_cause": "Guest client isolation ACL not applied on switch access port.",
        "ai_confidence": "0.80",
        "human_decision": "REJECT",
        "human_correction": "AP switch port Fa0/12 missing switchport trunk allowed vlan 50 for Guest WLAN traffic.",
        "reason": "AI blamed guest isolation ACL; show interfaces trunk confirmed VLAN 50 was missing on AP trunk link.",
        "reviewer": "Lead Network Architect",
        "review_timestamp": "2026-08-28T12:50:00Z"
    },
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["case_id", "ai_root_cause", "ai_confidence", "human_decision", "human_correction", "reason", "reviewer", "review_timestamp"]
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for r in reviews:
        writer.writerow(r)

print(f"Populated {len(reviews)} human review records into {csv_path}.")

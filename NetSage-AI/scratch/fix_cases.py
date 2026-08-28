import csv
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
csv_path = os.path.join(base_dir, 'data', 'cases.csv')
md_path = os.path.join(base_dir, 'docs', 'packet_tracer_scenarios.md')

with open(csv_path, 'r', encoding='utf-8') as f:
    cases = list(csv.DictReader(f))

for case in cases:
    # FIX 1: NET-014
    if case['case_id'] == 'NET-014':
        case['topology_note'] = "Host -> Router -> DNS Server (10.0.0.53)"
        case['show_outputs'] = "Host> ipconfig /all\nDNS Servers . . . . . . . . . . . : 10.0.0.99\n\nRouter# show ip route\nC 192.168.1.0 is directly connected, Gi0/0\nC 10.0.0.0 is directly connected, Gi0/1\n\nHost> ping 10.0.0.99\nRequest timed out."
        case['expected_fault'] = "The host is configured with an incorrect DNS server IP (10.0.0.99) instead of the actual DNS server (10.0.0.53)."

    # FIX 2: NET-015
    elif case['case_id'] == 'NET-015':
        case['topology_note'] = "Branch (192.168.1.0/24) -> R1 (172.16.0.1) -> R2 (172.16.0.2) -> HQ (10.0.0.0/24)"
        case['show_outputs'] = "R1# show ip route\nC 192.168.1.0/24 is directly connected\nC 172.16.0.0/30 is directly connected\n! Note: 10.0.0.0/24 is missing\n\nR2# show ip route\nC 10.0.0.0/24 is directly connected, Gi0/1\nC 172.16.0.0/30 is directly connected, Gi0/0\n\nR1# ping 10.0.0.10\n.....\nSuccess rate is 0 percent (0/5)"
        
    # FIX 3: NET-006
    elif case['case_id'] == 'NET-006':
        case['concept'] = 'Interface/connectivity'

    # FIX 4: NET-002
    elif case['case_id'] == 'NET-002':
        case['symptom'] = "New PC connected to SW1 Fa0/2 cannot reach the network."
        
    # FIX 5: NET-013
    elif case['case_id'] == 'NET-013':
        case['expected_fault'] = "ACL permits HTTP/HTTPS but denies other IP traffic, which blocks DNS UDP traffic on port 53."

    # FIX 6: NET-020
    elif case['case_id'] == 'NET-020':
        case['expected_fault'] = "ACL 101 is applied outbound on Gi0/1 and explicitly denies HTTP traffic from the user subnet to the web server."

    # FIX 7: NET-022
    elif case['case_id'] == 'NET-022':
        case['show_outputs'] = "R1# show access-lists 110\nExtended IP access list 110\n 10 permit tcp host 192.168.50.5 any eq 22  ! Incorrect\n ! Intended: permit tcp any host 192.168.50.5 eq 22\n 20 deny ip any any\n\nR1# show ip interface Gi0/0\n  Inbound access list is 110"

with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=cases[0].keys())
    writer.writeheader()
    writer.writerows(cases)

# Regenerate MD
with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# Packet Tracer Scenarios\n\n")
    for case in cases:
        f.write(f"## {case['case_id']} - {case['concept']}\n")
        f.write(f"- **Category:** {case['concept']}\n")
        f.write(f"- **Network Topology:** {case['topology_note']}\n")
        f.write(f"- **Intentional Fault:** {case['expected_fault']}\n")
        f.write(f"- **Expected User Symptom:** {case['symptom']}\n")
        f.write(f"- **Expected Evidence:** \n```text\n{case['show_outputs']}\n```\n")
        f.write(f"- **Expected Correct Diagnosis:** The issue is a {case['concept']} problem at {case['osi_layer']}. Specifically, {case['expected_fault']}\n")
        if case['case_id'] == 'NET-029':
            f.write("- **Note:** Port security on the router uplink is an intentional lab scenario.\n")
        f.write("- **Verification Method:** Correct the configuration and verify connectivity.\n\n")

print("Files generated successfully.")

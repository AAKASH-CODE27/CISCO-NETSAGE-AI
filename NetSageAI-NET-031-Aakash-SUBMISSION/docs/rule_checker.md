# Rule Checker Documentation

## 1. Purpose

The NetSage AI rule checker is a **deterministic, non-LLM** validation engine that detects common network configuration mistakes. It provides fast, reproducible, and explainable results without requiring an AI model.

## 2. Why Deterministic Rules?

> "Why use a deterministic rule checker when we already have an LLM?"

- **Predictability**: Deterministic checks always produce the same output for the same input. There is no randomness or hallucination.
- **Speed**: Basic configuration errors (duplicate IPs, wrong masks) can be identified in microseconds without waiting for an API call.
- **Reproducibility**: Results are fully reproducible across runs, which is critical for auditing and Responsible AI evaluation.
- **Independence**: The rule engine provides an independent signal. If the LLM disagrees with a deterministic finding, that discrepancy is itself useful evidence.
- **Reduced LLM load**: By catching obvious faults deterministically, the LLM can focus on complex reasoning over ambiguous symptoms and evidence.
- **Cost**: No API calls, no tokens, no billing.
- **Human review remains the final safety mechanism** — neither the rule checker nor the LLM autonomously applies network changes.

The rule checker is **not a replacement** for the AI. It is a complementary layer in the diagnosis pipeline.

## 3. Input Model

All input is provided via a `NetworkSnapshot` Pydantic model containing:

| Field               | Type                   | Description                                  |
|---------------------|------------------------|----------------------------------------------|
| `hosts`             | `List[HostInfo]`       | Devices with IP, mask, gateway, optional VLAN |
| `interfaces`        | `List[InterfaceInfo]`  | Device interfaces with status/protocol       |
| `vlans`             | `List[VlanInfo]`       | VLAN database entries per device             |
| `vlan_assignments`  | `List[VlanAssignment]` | Interface-to-VLAN mappings                   |
| `routes`            | `List[RouteEntry]`     | Routing table entries per device             |
| `required_routes`   | `List[RequiredRoute]`  | Destinations that must be reachable          |

### HostInfo

```python
HostInfo(
    device="PC1",
    ip_address="192.168.1.50",
    subnet_mask="255.255.255.0",
    default_gateway="192.168.1.1",  # optional
    vlan=10                          # optional
)
```

### InterfaceInfo

```python
InterfaceInfo(
    device="R1",
    interface_name="Gi0/0",
    status="up",                     # "up", "down", "administratively down"
    protocol="up"                    # "up", "down", "down (err-disabled)"
)
```

### VlanInfo / VlanAssignment

```python
VlanInfo(device="SW1", vlan_id=10, vlan_name="Sales", status="active")
VlanAssignment(device="SW1", interface_name="Fa0/1", access_vlan=10)
```

### RouteEntry / RequiredRoute

```python
RouteEntry(device="R1", destination="10.0.0.0/24", next_hop="172.16.0.2")
RequiredRoute(device="R1", destination="10.0.0.0/24")
```

## 4. Output Model

Every rule returns one or more `RuleResult` objects:

```json
{
    "rule": "gateway_mismatch",
    "status": "FAIL",
    "severity": "High",
    "message": "Gateway 192.168.20.1 is outside subnet 192.168.10.0/24 on PC1.",
    "evidence": [
        "PC1: IP 192.168.10.20/255.255.255.0",
        "Gateway: 192.168.20.1",
        "Subnet: 192.168.10.0/24"
    ]
}
```

### Possible statuses

| Status           | Meaning                                    |
|------------------|--------------------------------------------|
| `PASS`           | The check found no issues.                 |
| `FAIL`           | A deterministic fault was detected.        |
| `NOT_APPLICABLE` | Insufficient data to evaluate the rule.    |

## 5. The Six Rules

### Rule 1 — `duplicate_ip`
Detects when two or more devices share the same IP address.

### Rule 2 — `wrong_subnet_mask`
Detects non-contiguous (invalid) subnet masks. A valid mask in binary is a contiguous sequence of 1-bits followed by 0-bits. `255.255.0.255` is invalid.

### Rule 3 — `gateway_mismatch`
Detects when a host's default gateway IP is outside the host's subnet (calculated using Python's `ipaddress` module). If the mask is invalid, the check returns `NOT_APPLICABLE`.

### Rule 4 — `interface_down`
Detects interfaces not in `up/up` state. Distinguishes `administratively down`, `err-disabled`, and generic `down` states.

### Rule 5 — `missing_vlan`
Detects when an interface's access VLAN is absent from the device's VLAN database. Only checks VLAN existence — does not check trunk allowed lists or VLAN activity.

### Rule 6 — `missing_route`
Detects when a required destination network is absent from the device routing table. A destination is considered reachable if an exact match or a covering supernet (including a default route `0.0.0.0/0`) exists.

## 6. Rule Logic

```text
Input (NetworkSnapshot)
    │
    ├─► check_duplicate_ips()    → compare all host IPs for uniqueness
    ├─► check_subnet_masks()     → verify contiguous bit pattern
    ├─► check_gateways()         → ipaddress.IPv4Interface membership test
    ├─► check_interfaces()       → string match on status/protocol fields
    ├─► check_vlans()            → set membership: assignment VLAN ∈ DB VLANs
    └─► check_routes()           → ipaddress.IPv4Network.subnet_of() comparison
         │
         └─► List[RuleResult]
```

## 7. Examples

### Duplicate IP

```python
from rule_checker.checker import check_duplicate_ips
from rule_checker.models import NetworkSnapshot, HostInfo

snap = NetworkSnapshot(hosts=[
    HostInfo(device="A", ip_address="192.168.10.10", subnet_mask="255.255.255.0"),
    HostInfo(device="B", ip_address="192.168.10.10", subnet_mask="255.255.255.0"),
])
results = check_duplicate_ips(snap)
# results[0].status == RuleStatus.FAIL
```

### Gateway Mismatch

```python
from rule_checker.checker import check_gateways
from rule_checker.models import NetworkSnapshot, HostInfo

snap = NetworkSnapshot(hosts=[
    HostInfo(device="PC1", ip_address="192.168.10.20",
             subnet_mask="255.255.255.0", default_gateway="192.168.20.1"),
])
results = check_gateways(snap)
# results[0].status == RuleStatus.FAIL
```

## 8. Error Handling

- **Invalid IP addresses** (`999.999.1.1`) are rejected at input validation by the Pydantic model.
- **Invalid subnet masks** (non-4-octet or octet > 255) are rejected at input validation.
- **Invalid gateways** (`not-an-ip`) are rejected at input validation.
- **Non-contiguous masks** pass input validation but are flagged as `FAIL` by the `wrong_subnet_mask` rule, and cause the `gateway_mismatch` rule to return `NOT_APPLICABLE`.

## 9. Testing Strategy

Tests are in `tests/test_rule_checker.py` and cover:

- Every rule with at least PASS and FAIL scenarios.
- Edge cases: /32 hosts, /31 point-to-point, empty inputs, multiple duplicates.
- Input validation: malformed IPs, masks, and gateways.
- Integration: `run_all_checks()` returns results from all six rules.

Run tests:

```
python tests/test_rule_checker.py
```

## 10. Limitations

- The checker only implements the six Cisco-required deterministic rules.
- It does **not** detect: DHCP misconfigurations, DNS issues, ACL problems, NAT errors, OSPF/EIGRP/RIP issues, or wireless faults.
- It operates on structured input — it does not parse raw Cisco CLI output (that is a future integration concern).
- It does not distinguish VLAN inactive vs. VLAN missing from trunk — only VLAN existence.

## 11. Relationship to the Future LLM Component

```text
                    ┌─────────────────────┐
 NetworkSnapshot ──►│ Python Rule Checker  │──► Deterministic Findings
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
 Symptoms + Evidence──►│   LLM Diagnosis  │──► AI Reasoning
                    └─────────────────────┘
                              │
                    Both feed into ──► Diagnosis JSON ──► Human Review
```

The rule checker findings will be passed as **additional evidence** to the LLM in Phase 4. The LLM can then synthesise deterministic findings with symptoms and show-command evidence to produce a comprehensive diagnosis. Human review remains the final gate.

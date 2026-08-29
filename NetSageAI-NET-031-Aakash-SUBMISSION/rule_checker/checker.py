"""
NetSage AI — Deterministic Python Rule Checker
===============================================

This module performs deterministic (non-LLM) checks for common
network configuration mistakes.

Supported rules
----------------
1. duplicate_ip        – Two+ devices sharing the same IP.
2. wrong_subnet_mask   – Non-contiguous or otherwise invalid mask.
3. gateway_mismatch    – Default gateway outside the host subnet.
4. interface_down      – Interface not in up/up state.
5. missing_vlan        – Access VLAN absent from the VLAN database.
6. missing_route       – Required destination absent from routing table.

Usage
-----
    from rule_checker.checker import run_all_checks
    from rule_checker.models import NetworkSnapshot

    snapshot = NetworkSnapshot(hosts=[...], interfaces=[...], ...)
    results = run_all_checks(snapshot)
    for r in results:
        print(r.model_dump())
"""

from __future__ import annotations

import ipaddress
from collections import Counter
from typing import List

from .models import (
    NetworkSnapshot,
    RuleResult,
    RuleStatus,
)


# ===================================================================
# RULE 1 — Duplicate IP Detection
# ===================================================================

def check_duplicate_ips(snapshot: NetworkSnapshot) -> List[RuleResult]:
    """Detect when two or more hosts share the same IP address.

    Returns one RuleResult per duplicated IP found, or a single PASS
    result when no duplicates exist.
    """
    results: List[RuleResult] = []

    ip_devices: dict[str, list[str]] = {}
    for host in snapshot.hosts:
        ip_devices.setdefault(host.ip_address, []).append(host.device)

    found_duplicate = False
    for ip_addr, devices in ip_devices.items():
        if len(devices) > 1:
            found_duplicate = True
            results.append(RuleResult(
                rule="duplicate_ip",
                status=RuleStatus.FAIL,
                severity="High",
                message=f"Duplicate IP address {ip_addr} detected on {len(devices)} devices.",
                evidence=[f"{dev}: {ip_addr}" for dev in devices],
            ))

    if not found_duplicate:
        results.append(RuleResult(
            rule="duplicate_ip",
            status=RuleStatus.PASS,
            severity="Info",
            message="No duplicate IP addresses detected.",
            evidence=[],
        ))

    return results


# ===================================================================
# RULE 2 — Wrong Subnet Mask
# ===================================================================

def _is_contiguous_mask(mask_str: str) -> bool:
    """Return True if *mask_str* represents a valid contiguous subnet mask.

    A contiguous mask in binary is a sequence of 1-bits followed
    exclusively by 0-bits.  255.255.0.255 is NOT contiguous.
    """
    octets = [int(o) for o in mask_str.split(".")]
    bits = 0
    for o in octets:
        bits = (bits << 8) | o
    # A valid mask has the form 1...10...0.
    # Inverting gives 0...01...1, adding 1 gives a power of 2.
    inverted = bits ^ 0xFFFFFFFF
    return inverted >= 0 and ((inverted + 1) & inverted) == 0


def check_subnet_masks(snapshot: NetworkSnapshot) -> List[RuleResult]:
    """Detect invalid (non-contiguous) subnet masks.

    Returns one result per host checked.
    """
    results: List[RuleResult] = []

    if not snapshot.hosts:
        results.append(RuleResult(
            rule="wrong_subnet_mask",
            status=RuleStatus.NOT_APPLICABLE,
            severity="Info",
            message="No host information supplied.",
            evidence=[],
        ))
        return results

    for host in snapshot.hosts:
        if _is_contiguous_mask(host.subnet_mask):
            results.append(RuleResult(
                rule="wrong_subnet_mask",
                status=RuleStatus.PASS,
                severity="Info",
                message=f"Valid subnet mask on {host.device}.",
                evidence=[f"{host.device}: {host.subnet_mask}"],
            ))
        else:
            results.append(RuleResult(
                rule="wrong_subnet_mask",
                status=RuleStatus.FAIL,
                severity="Medium",
                message=f"Invalid (non-contiguous) subnet mask on {host.device}.",
                evidence=[f"{host.device}: Mask {host.subnet_mask}"],
            ))

    return results


# ===================================================================
# RULE 3 — Gateway Mismatch
# ===================================================================

def check_gateways(snapshot: NetworkSnapshot) -> List[RuleResult]:
    """Detect when a host's default gateway is outside the host subnet.

    Uses Python's ``ipaddress`` module for subnet calculation.
    Hosts without a gateway configured are marked NOT_APPLICABLE.
    """
    results: List[RuleResult] = []

    if not snapshot.hosts:
        results.append(RuleResult(
            rule="gateway_mismatch",
            status=RuleStatus.NOT_APPLICABLE,
            severity="Info",
            message="No host information supplied.",
            evidence=[],
        ))
        return results

    for host in snapshot.hosts:
        if host.default_gateway is None:
            results.append(RuleResult(
                rule="gateway_mismatch",
                status=RuleStatus.NOT_APPLICABLE,
                severity="Info",
                message=f"No gateway configured on {host.device}.",
                evidence=[],
            ))
            continue

        # We need a valid contiguous mask for subnet math.
        if not _is_contiguous_mask(host.subnet_mask):
            results.append(RuleResult(
                rule="gateway_mismatch",
                status=RuleStatus.NOT_APPLICABLE,
                severity="Info",
                message=f"Cannot evaluate gateway — invalid mask on {host.device}.",
                evidence=[f"{host.device}: Mask {host.subnet_mask}"],
            ))
            continue

        try:
            iface = ipaddress.IPv4Interface(f"{host.ip_address}/{host.subnet_mask}")
            network = iface.network
            gw = ipaddress.IPv4Address(host.default_gateway)
        except (ValueError, ipaddress.AddressValueError) as exc:
            results.append(RuleResult(
                rule="gateway_mismatch",
                status=RuleStatus.FAIL,
                severity="High",
                message=f"Invalid IP/mask/gateway on {host.device}: {exc}",
                evidence=[
                    f"IP: {host.ip_address}",
                    f"Mask: {host.subnet_mask}",
                    f"Gateway: {host.default_gateway}",
                ],
            ))
            continue

        if gw in network:
            results.append(RuleResult(
                rule="gateway_mismatch",
                status=RuleStatus.PASS,
                severity="Info",
                message=f"Gateway is within the host subnet on {host.device}.",
                evidence=[
                    f"{host.device}: IP {host.ip_address}/{host.subnet_mask}",
                    f"Gateway: {host.default_gateway}",
                    f"Subnet: {network}",
                ],
            ))
        else:
            results.append(RuleResult(
                rule="gateway_mismatch",
                status=RuleStatus.FAIL,
                severity="High",
                message=f"Gateway {host.default_gateway} is outside subnet {network} on {host.device}.",
                evidence=[
                    f"{host.device}: IP {host.ip_address}/{host.subnet_mask}",
                    f"Gateway: {host.default_gateway}",
                    f"Subnet: {network}",
                ],
            ))

    return results


# ===================================================================
# RULE 4 — Interface Down
# ===================================================================

_DOWN_KEYWORDS = {"down", "administratively down", "err-disabled"}


def check_interfaces(snapshot: NetworkSnapshot) -> List[RuleResult]:
    """Detect interfaces that are not in up/up state.

    Checks both *status* and *protocol* fields.  Preserves
    the actual evidence string so the operator sees the real
    state (e.g. ``administratively down/down`` vs ``down/down``).
    """
    results: List[RuleResult] = []

    if not snapshot.interfaces:
        results.append(RuleResult(
            rule="interface_down",
            status=RuleStatus.NOT_APPLICABLE,
            severity="Info",
            message="No interface information supplied.",
            evidence=[],
        ))
        return results

    for iface in snapshot.interfaces:
        status_lower = iface.status.strip().lower()
        proto_lower = iface.protocol.strip().lower()

        is_down = (
            status_lower in _DOWN_KEYWORDS
            or proto_lower in _DOWN_KEYWORDS
            or status_lower != "up"
            or proto_lower != "up"
        )

        evidence_str = f"{iface.device} {iface.interface_name}: {iface.status}/{iface.protocol}"

        if is_down:
            # Distinguish admin-down from other failures
            if "administratively" in status_lower:
                msg = f"Interface {iface.interface_name} on {iface.device} is administratively down."
                sev = "High"
            elif "err-disabled" in status_lower or "err-disabled" in proto_lower:
                msg = f"Interface {iface.interface_name} on {iface.device} is err-disabled."
                sev = "High"
            else:
                msg = f"Interface {iface.interface_name} on {iface.device} is down."
                sev = "High"

            results.append(RuleResult(
                rule="interface_down",
                status=RuleStatus.FAIL,
                severity=sev,
                message=msg,
                evidence=[evidence_str],
            ))
        else:
            results.append(RuleResult(
                rule="interface_down",
                status=RuleStatus.PASS,
                severity="Info",
                message=f"Interface {iface.interface_name} on {iface.device} is up.",
                evidence=[evidence_str],
            ))

    return results


# ===================================================================
# RULE 5 — Missing VLAN
# ===================================================================

def check_vlans(snapshot: NetworkSnapshot) -> List[RuleResult]:
    """Detect when an interface's access VLAN is absent from the VLAN database.

    Compares each VlanAssignment against the VlanInfo entries for the
    same device.  Only checks existence; does NOT check VLAN activity
    or trunk-allowed lists (those are different conditions).
    """
    results: List[RuleResult] = []

    if not snapshot.vlan_assignments:
        results.append(RuleResult(
            rule="missing_vlan",
            status=RuleStatus.NOT_APPLICABLE,
            severity="Info",
            message="No VLAN assignments supplied.",
            evidence=[],
        ))
        return results

    # Build per-device set of known VLAN IDs.
    device_vlans: dict[str, set[int]] = {}
    for vlan in snapshot.vlans:
        device_vlans.setdefault(vlan.device, set()).add(vlan.vlan_id)

    for assign in snapshot.vlan_assignments:
        known = device_vlans.get(assign.device, set())
        if assign.access_vlan in known:
            results.append(RuleResult(
                rule="missing_vlan",
                status=RuleStatus.PASS,
                severity="Info",
                message=f"VLAN {assign.access_vlan} exists on {assign.device}.",
                evidence=[
                    f"{assign.device} {assign.interface_name}: VLAN {assign.access_vlan}",
                    f"Known VLANs: {sorted(known)}",
                ],
            ))
        else:
            results.append(RuleResult(
                rule="missing_vlan",
                status=RuleStatus.FAIL,
                severity="Medium",
                message=f"VLAN {assign.access_vlan} is not in the VLAN database on {assign.device}.",
                evidence=[
                    f"{assign.device} {assign.interface_name}: VLAN {assign.access_vlan}",
                    f"Known VLANs: {sorted(known)}",
                ],
            ))

    return results


# ===================================================================
# RULE 6 — Missing Route
# ===================================================================

def check_routes(snapshot: NetworkSnapshot) -> List[RuleResult]:
    """Detect when a required destination is absent from the routing table.

    A required destination is considered reachable if:
    - An exact-match route exists, OR
    - A covering supernet route exists (including a default route).

    Uses Python's ``ipaddress`` module for prefix comparison.
    """
    results: List[RuleResult] = []

    if not snapshot.required_routes:
        results.append(RuleResult(
            rule="missing_route",
            status=RuleStatus.NOT_APPLICABLE,
            severity="Info",
            message="No required routes specified.",
            evidence=[],
        ))
        return results

    # Build per-device list of parsed networks.
    device_networks: dict[str, list[ipaddress.IPv4Network]] = {}
    for entry in snapshot.routes:
        try:
            net = ipaddress.IPv4Network(entry.destination, strict=False)
        except ValueError:
            continue
        device_networks.setdefault(entry.device, []).append(net)

    for req in snapshot.required_routes:
        try:
            target = ipaddress.IPv4Network(req.destination, strict=False)
        except ValueError:
            results.append(RuleResult(
                rule="missing_route",
                status=RuleStatus.FAIL,
                severity="High",
                message=f"Invalid destination network format: {req.destination}",
                evidence=[f"Device: {req.device}", f"Destination: {req.destination}"],
            ))
            continue

        networks = device_networks.get(req.device, [])
        covered = any(
            target.subnet_of(net) for net in networks
        )

        route_strs = [str(n) for n in networks] if networks else ["(empty)"]

        if covered:
            results.append(RuleResult(
                rule="missing_route",
                status=RuleStatus.PASS,
                severity="Info",
                message=f"Route to {req.destination} exists on {req.device}.",
                evidence=[
                    f"Device: {req.device}",
                    f"Required: {req.destination}",
                    f"Routes: {', '.join(route_strs)}",
                ],
            ))
        else:
            results.append(RuleResult(
                rule="missing_route",
                status=RuleStatus.FAIL,
                severity="Critical",
                message=f"No route to {req.destination} on {req.device}.",
                evidence=[
                    f"Device: {req.device}",
                    f"Required: {req.destination}",
                    f"Routes: {', '.join(route_strs)}",
                ],
            ))

    return results


# ===================================================================
# Aggregator
# ===================================================================

def run_all_checks(snapshot: NetworkSnapshot) -> List[RuleResult]:
    """Execute all six deterministic rule checks and return aggregated results.

    Parameters
    ----------
    snapshot : NetworkSnapshot
        Structured representation of the network configuration to validate.

    Returns
    -------
    list[RuleResult]
        One or more results per rule.
    """
    results: List[RuleResult] = []
    results.extend(check_duplicate_ips(snapshot))
    results.extend(check_subnet_masks(snapshot))
    results.extend(check_gateways(snapshot))
    results.extend(check_interfaces(snapshot))
    results.extend(check_vlans(snapshot))
    results.extend(check_routes(snapshot))
    return results


# ===================================================================
# CLI demo
# ===================================================================

def _demo() -> None:
    """Run a small built-in demonstration showing deterministic output."""
    from .models import (
        HostInfo, InterfaceInfo, VlanInfo, VlanAssignment,
        RouteEntry, RequiredRoute, NetworkSnapshot,
    )

    snapshot = NetworkSnapshot(
        hosts=[
            HostInfo(device="Host_A", ip_address="192.168.10.10",
                     subnet_mask="255.255.255.0", default_gateway="192.168.10.1"),
            HostInfo(device="Host_B", ip_address="192.168.10.10",
                     subnet_mask="255.255.255.0", default_gateway="192.168.10.1"),
            HostInfo(device="Server", ip_address="10.0.0.10",
                     subnet_mask="255.255.255.0", default_gateway="10.0.1.1"),
            HostInfo(device="BadMask", ip_address="172.16.0.5",
                     subnet_mask="255.255.0.255"),
        ],
        interfaces=[
            InterfaceInfo(device="R1", interface_name="Gi0/0",
                          status="up", protocol="up"),
            InterfaceInfo(device="R1", interface_name="Gi0/1",
                          status="administratively down", protocol="down"),
        ],
        vlans=[
            VlanInfo(device="SW1", vlan_id=1, vlan_name="default", status="active"),
            VlanInfo(device="SW1", vlan_id=20, vlan_name="Sales", status="active"),
        ],
        vlan_assignments=[
            VlanAssignment(device="SW1", interface_name="Fa0/2", access_vlan=10),
        ],
        routes=[
            RouteEntry(device="R1", destination="192.168.1.0/24"),
            RouteEntry(device="R1", destination="172.16.0.0/30"),
        ],
        required_routes=[
            RequiredRoute(device="R1", destination="10.0.0.0/24"),
        ],
    )

    results = run_all_checks(snapshot)

    print("=" * 60)
    print("NetSage AI — Deterministic Rule Checker Demo")
    print("=" * 60)
    for r in results:
        icon = "OK" if r.status == RuleStatus.PASS else ("XX" if r.status == RuleStatus.FAIL else "--")
        print(f"\n[{icon}] {r.rule}: {r.status.value}")
        print(f"    Severity: {r.severity}")
        print(f"    Message:  {r.message}")
        if r.evidence:
            for e in r.evidence:
                print(f"    Evidence: {e}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    _demo()

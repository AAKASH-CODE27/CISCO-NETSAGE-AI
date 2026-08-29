"""
Comprehensive unit tests for the NetSage AI deterministic rule checker.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rule_checker.models import (
    HostInfo, InterfaceInfo, VlanInfo, VlanAssignment,
    RouteEntry, RequiredRoute, NetworkSnapshot, RuleStatus,
)
from rule_checker.checker import (
    check_duplicate_ips,
    check_subnet_masks,
    check_gateways,
    check_interfaces,
    check_vlans,
    check_routes,
    run_all_checks,
)

passed = 0
failed = 0


def assert_eq(test_name: str, actual, expected):
    global passed, failed
    if actual == expected:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {test_name}")
        print(f"    Expected: {expected}")
        print(f"    Got:      {actual}")


def assert_true(test_name: str, condition: bool):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {test_name}")


def assert_raises(test_name: str, exc_type, fn, *args, **kwargs):
    global passed, failed
    try:
        fn(*args, **kwargs)
        failed += 1
        print(f"  FAIL: {test_name} — no exception raised")
    except exc_type:
        passed += 1
    except Exception as e:
        failed += 1
        print(f"  FAIL: {test_name} — wrong exception: {type(e).__name__}: {e}")


# ===================================================================
# RULE 1 — Duplicate IP
# ===================================================================

def test_duplicate_ip_fail():
    """Two hosts with the same IP → FAIL."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="A", ip_address="192.168.10.10", subnet_mask="255.255.255.0"),
        HostInfo(device="B", ip_address="192.168.10.10", subnet_mask="255.255.255.0"),
    ])
    results = check_duplicate_ips(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("dup_ip_fail: count", len(fails), 1)
    assert_eq("dup_ip_fail: rule", fails[0].rule, "duplicate_ip")


def test_duplicate_ip_pass():
    """Unique IPs → PASS."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="A", ip_address="192.168.10.10", subnet_mask="255.255.255.0"),
        HostInfo(device="B", ip_address="192.168.10.20", subnet_mask="255.255.255.0"),
    ])
    results = check_duplicate_ips(snap)
    passes = [r for r in results if r.status == RuleStatus.PASS]
    assert_eq("dup_ip_pass: count", len(passes), 1)


def test_duplicate_ip_multiple():
    """Three hosts with same IP → FAIL with all three in evidence."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="A", ip_address="10.0.0.1", subnet_mask="255.255.255.0"),
        HostInfo(device="B", ip_address="10.0.0.1", subnet_mask="255.255.255.0"),
        HostInfo(device="C", ip_address="10.0.0.1", subnet_mask="255.255.255.0"),
    ])
    results = check_duplicate_ips(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("dup_ip_multiple: count", len(fails), 1)
    assert_eq("dup_ip_multiple: evidence", len(fails[0].evidence), 3)


# ===================================================================
# RULE 2 — Subnet Mask
# ===================================================================

def test_subnet_mask_valid():
    """Standard /24 mask → PASS."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="H1", ip_address="10.0.0.1", subnet_mask="255.255.255.0"),
    ])
    results = check_subnet_masks(snap)
    assert_eq("mask_valid: status", results[0].status, RuleStatus.PASS)


def test_subnet_mask_invalid():
    """Non-contiguous mask → FAIL."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="H1", ip_address="10.0.0.1", subnet_mask="255.255.0.255"),
    ])
    results = check_subnet_masks(snap)
    assert_eq("mask_invalid: status", results[0].status, RuleStatus.FAIL)


def test_subnet_mask_all_ones():
    """/32 mask → PASS."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="H1", ip_address="10.0.0.1", subnet_mask="255.255.255.255"),
    ])
    results = check_subnet_masks(snap)
    assert_eq("mask_/32: status", results[0].status, RuleStatus.PASS)


def test_subnet_mask_slash31():
    """/31 point-to-point mask → PASS."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="R1", ip_address="10.0.0.0", subnet_mask="255.255.255.254"),
    ])
    results = check_subnet_masks(snap)
    assert_eq("mask_/31: status", results[0].status, RuleStatus.PASS)


def test_subnet_mask_no_hosts():
    """No hosts → NOT_APPLICABLE."""
    snap = NetworkSnapshot()
    results = check_subnet_masks(snap)
    assert_eq("mask_no_hosts: status", results[0].status, RuleStatus.NOT_APPLICABLE)


# ===================================================================
# RULE 3 — Gateway Mismatch
# ===================================================================

def test_gateway_in_subnet():
    """Gateway within the same /24 → PASS."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="PC1", ip_address="192.168.1.50",
                 subnet_mask="255.255.255.0", default_gateway="192.168.1.1"),
    ])
    results = check_gateways(snap)
    passes = [r for r in results if r.status == RuleStatus.PASS]
    assert_eq("gw_in_subnet: count", len(passes), 1)


def test_gateway_outside_subnet():
    """Gateway in a different subnet → FAIL."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="PC1", ip_address="192.168.10.20",
                 subnet_mask="255.255.255.0", default_gateway="192.168.20.1"),
    ])
    results = check_gateways(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("gw_outside: count", len(fails), 1)
    assert_eq("gw_outside: rule", fails[0].rule, "gateway_mismatch")


def test_gateway_equal_to_host():
    """Gateway equal to host IP (in same subnet) → PASS."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="R1", ip_address="10.0.0.1",
                 subnet_mask="255.255.255.0", default_gateway="10.0.0.1"),
    ])
    results = check_gateways(snap)
    passes = [r for r in results if r.status == RuleStatus.PASS]
    assert_eq("gw_eq_host: count", len(passes), 1)


def test_gateway_none():
    """No gateway configured → NOT_APPLICABLE."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="SW", ip_address="10.0.0.1", subnet_mask="255.255.255.0"),
    ])
    results = check_gateways(snap)
    na = [r for r in results if r.status == RuleStatus.NOT_APPLICABLE]
    assert_eq("gw_none: count", len(na), 1)


def test_gateway_with_invalid_mask():
    """Non-contiguous mask → NOT_APPLICABLE for gateway check."""
    snap = NetworkSnapshot(hosts=[
        HostInfo(device="H", ip_address="10.0.0.1",
                 subnet_mask="255.0.255.0", default_gateway="10.0.0.2"),
    ])
    results = check_gateways(snap)
    na = [r for r in results if r.status == RuleStatus.NOT_APPLICABLE]
    assert_eq("gw_bad_mask: count", len(na), 1)


# ===================================================================
# RULE 4 — Interface Down
# ===================================================================

def test_interface_up():
    """up/up → PASS."""
    snap = NetworkSnapshot(interfaces=[
        InterfaceInfo(device="R1", interface_name="Gi0/0", status="up", protocol="up"),
    ])
    results = check_interfaces(snap)
    assert_eq("iface_up: status", results[0].status, RuleStatus.PASS)


def test_interface_admin_down():
    """administratively down/down → FAIL."""
    snap = NetworkSnapshot(interfaces=[
        InterfaceInfo(device="R1", interface_name="Gi0/0",
                      status="administratively down", protocol="down"),
    ])
    results = check_interfaces(snap)
    assert_eq("iface_admin_down: status", results[0].status, RuleStatus.FAIL)
    assert_true("iface_admin_down: msg",
                "administratively" in results[0].message.lower())


def test_interface_down_down():
    """down/down → FAIL."""
    snap = NetworkSnapshot(interfaces=[
        InterfaceInfo(device="SW1", interface_name="Fa0/1",
                      status="down", protocol="down"),
    ])
    results = check_interfaces(snap)
    assert_eq("iface_down: status", results[0].status, RuleStatus.FAIL)


def test_interface_err_disabled():
    """err-disabled → FAIL."""
    snap = NetworkSnapshot(interfaces=[
        InterfaceInfo(device="SW1", interface_name="Gi0/24",
                      status="up", protocol="down (err-disabled)"),
    ])
    results = check_interfaces(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("iface_err_disabled: count", len(fails), 1)


def test_interface_no_data():
    """No interfaces → NOT_APPLICABLE."""
    snap = NetworkSnapshot()
    results = check_interfaces(snap)
    assert_eq("iface_no_data: status", results[0].status, RuleStatus.NOT_APPLICABLE)


def test_interface_multiple():
    """Mix of up and down interfaces."""
    snap = NetworkSnapshot(interfaces=[
        InterfaceInfo(device="R1", interface_name="Gi0/0", status="up", protocol="up"),
        InterfaceInfo(device="R1", interface_name="Gi0/1",
                      status="administratively down", protocol="down"),
        InterfaceInfo(device="R1", interface_name="Gi0/2", status="up", protocol="up"),
    ])
    results = check_interfaces(snap)
    passes = [r for r in results if r.status == RuleStatus.PASS]
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("iface_multi: passes", len(passes), 2)
    assert_eq("iface_multi: fails", len(fails), 1)


# ===================================================================
# RULE 5 — Missing VLAN
# ===================================================================

def test_vlan_exists():
    """VLAN present in database → PASS."""
    snap = NetworkSnapshot(
        vlans=[VlanInfo(device="SW1", vlan_id=10, vlan_name="Sales")],
        vlan_assignments=[VlanAssignment(device="SW1", interface_name="Fa0/1", access_vlan=10)],
    )
    results = check_vlans(snap)
    assert_eq("vlan_exists: status", results[0].status, RuleStatus.PASS)


def test_vlan_missing():
    """VLAN absent from database → FAIL."""
    snap = NetworkSnapshot(
        vlans=[
            VlanInfo(device="SW1", vlan_id=1, vlan_name="default"),
            VlanInfo(device="SW1", vlan_id=20, vlan_name="IT"),
        ],
        vlan_assignments=[VlanAssignment(device="SW1", interface_name="Fa0/2", access_vlan=10)],
    )
    results = check_vlans(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("vlan_missing: count", len(fails), 1)


def test_vlan_empty_database():
    """Empty VLAN database → FAIL."""
    snap = NetworkSnapshot(
        vlans=[],
        vlan_assignments=[VlanAssignment(device="SW1", interface_name="Fa0/1", access_vlan=10)],
    )
    results = check_vlans(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("vlan_empty_db: count", len(fails), 1)


def test_vlan_no_assignments():
    """No VLAN assignments → NOT_APPLICABLE."""
    snap = NetworkSnapshot()
    results = check_vlans(snap)
    assert_eq("vlan_no_assign: status", results[0].status, RuleStatus.NOT_APPLICABLE)


# ===================================================================
# RULE 6 — Missing Route
# ===================================================================

def test_route_exists():
    """Exact-match route → PASS."""
    snap = NetworkSnapshot(
        routes=[RouteEntry(device="R1", destination="10.0.0.0/24")],
        required_routes=[RequiredRoute(device="R1", destination="10.0.0.0/24")],
    )
    results = check_routes(snap)
    assert_eq("route_exists: status", results[0].status, RuleStatus.PASS)


def test_route_missing():
    """Required route absent → FAIL."""
    snap = NetworkSnapshot(
        routes=[
            RouteEntry(device="R1", destination="192.168.1.0/24"),
            RouteEntry(device="R1", destination="172.16.0.0/30"),
        ],
        required_routes=[RequiredRoute(device="R1", destination="10.0.0.0/24")],
    )
    results = check_routes(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("route_missing: count", len(fails), 1)


def test_route_default_covers():
    """Default route covers a required destination → PASS."""
    snap = NetworkSnapshot(
        routes=[RouteEntry(device="R1", destination="0.0.0.0/0")],
        required_routes=[RequiredRoute(device="R1", destination="10.0.0.0/24")],
    )
    results = check_routes(snap)
    passes = [r for r in results if r.status == RuleStatus.PASS]
    assert_eq("route_default_covers: count", len(passes), 1)


def test_route_supernet_covers():
    """Supernet route covers a more specific required destination → PASS."""
    snap = NetworkSnapshot(
        routes=[RouteEntry(device="R1", destination="10.0.0.0/8")],
        required_routes=[RequiredRoute(device="R1", destination="10.0.0.0/24")],
    )
    results = check_routes(snap)
    passes = [r for r in results if r.status == RuleStatus.PASS]
    assert_eq("route_supernet: count", len(passes), 1)


def test_route_empty_table():
    """Empty routing table → FAIL."""
    snap = NetworkSnapshot(
        routes=[],
        required_routes=[RequiredRoute(device="R1", destination="10.0.0.0/24")],
    )
    results = check_routes(snap)
    fails = [r for r in results if r.status == RuleStatus.FAIL]
    assert_eq("route_empty: count", len(fails), 1)


def test_route_no_requirements():
    """No required routes → NOT_APPLICABLE."""
    snap = NetworkSnapshot()
    results = check_routes(snap)
    assert_eq("route_no_req: status", results[0].status, RuleStatus.NOT_APPLICABLE)


# ===================================================================
# EDGE CASES
# ===================================================================

def test_malformed_ip_rejected():
    """HostInfo rejects an impossible IP address."""
    from pydantic import ValidationError
    assert_raises("malformed_ip", ValidationError,
                  HostInfo, device="X", ip_address="999.999.1.1", subnet_mask="255.255.255.0")


def test_malformed_mask_rejected():
    """HostInfo rejects a mask with invalid octets."""
    from pydantic import ValidationError
    assert_raises("malformed_mask", ValidationError,
                  HostInfo, device="X", ip_address="10.0.0.1", subnet_mask="256.0.0.0")


def test_malformed_gateway_rejected():
    """HostInfo rejects an invalid gateway string."""
    from pydantic import ValidationError
    assert_raises("malformed_gw", ValidationError,
                  HostInfo, device="X", ip_address="10.0.0.1",
                  subnet_mask="255.255.255.0", default_gateway="not-an-ip")


# ===================================================================
# INTEGRATION: run_all_checks
# ===================================================================

def test_run_all_checks():
    """run_all_checks returns results from all six rules."""
    snap = NetworkSnapshot(
        hosts=[
            HostInfo(device="A", ip_address="10.0.0.1", subnet_mask="255.255.255.0",
                     default_gateway="10.0.0.254"),
        ],
        interfaces=[
            InterfaceInfo(device="R1", interface_name="Gi0/0", status="up", protocol="up"),
        ],
        vlans=[VlanInfo(device="SW1", vlan_id=10)],
        vlan_assignments=[VlanAssignment(device="SW1", interface_name="Fa0/1", access_vlan=10)],
        routes=[RouteEntry(device="R1", destination="0.0.0.0/0")],
        required_routes=[RequiredRoute(device="R1", destination="10.0.0.0/24")],
    )
    results = run_all_checks(snap)
    rules_present = {r.rule for r in results}
    for expected_rule in ["duplicate_ip", "wrong_subnet_mask", "gateway_mismatch",
                          "interface_down", "missing_vlan", "missing_route"]:
        assert_true(f"run_all has {expected_rule}", expected_rule in rules_present)


# ===================================================================
# RUNNER
# ===================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("NetSage AI — Rule Checker Tests")
    print("=" * 60)

    # Duplicate IP
    print("\n--- Duplicate IP ---")
    test_duplicate_ip_fail()
    test_duplicate_ip_pass()
    test_duplicate_ip_multiple()

    # Subnet Mask
    print("\n--- Subnet Mask ---")
    test_subnet_mask_valid()
    test_subnet_mask_invalid()
    test_subnet_mask_all_ones()
    test_subnet_mask_slash31()
    test_subnet_mask_no_hosts()

    # Gateway
    print("\n--- Gateway Mismatch ---")
    test_gateway_in_subnet()
    test_gateway_outside_subnet()
    test_gateway_equal_to_host()
    test_gateway_none()
    test_gateway_with_invalid_mask()

    # Interface
    print("\n--- Interface Down ---")
    test_interface_up()
    test_interface_admin_down()
    test_interface_down_down()
    test_interface_err_disabled()
    test_interface_no_data()
    test_interface_multiple()

    # VLAN
    print("\n--- Missing VLAN ---")
    test_vlan_exists()
    test_vlan_missing()
    test_vlan_empty_database()
    test_vlan_no_assignments()

    # Route
    print("\n--- Missing Route ---")
    test_route_exists()
    test_route_missing()
    test_route_default_covers()
    test_route_supernet_covers()
    test_route_empty_table()
    test_route_no_requirements()

    # Edge cases
    print("\n--- Edge Cases ---")
    test_malformed_ip_rejected()
    test_malformed_mask_rejected()
    test_malformed_gateway_rejected()

    # Integration
    print("\n--- Integration ---")
    test_run_all_checks()

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("ALL RULE CHECKER TESTS PASSED.")

"""
Data models for the NetSage AI rule checker.

Defines Pydantic models for network configuration input and
structured rule-check results.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------

class RuleStatus(str, Enum):
    """Possible outcomes of a single rule check."""
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class RuleResult(BaseModel):
    """Structured result returned by every rule check."""
    rule: str
    status: RuleStatus
    severity: str
    message: str
    evidence: List[str]


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class HostInfo(BaseModel):
    """Represents a host or device interface with an IP configuration."""
    device: str
    ip_address: str
    subnet_mask: str
    default_gateway: Optional[str] = None
    vlan: Optional[int] = None

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        import ipaddress
        try:
            ipaddress.IPv4Address(v)
        except (ipaddress.AddressValueError, ValueError) as exc:
            raise ValueError(f"Invalid IPv4 address: {v}") from exc
        return v

    @field_validator("subnet_mask")
    @classmethod
    def validate_mask_format(cls, v: str) -> str:
        """Validate that the string looks like a dotted-decimal mask.

        We intentionally do NOT reject non-contiguous masks here so
        that the subnet-mask rule itself can report the failure.
        """
        parts = v.split(".")
        if len(parts) != 4:
            raise ValueError(f"Subnet mask must have 4 octets: {v}")
        for p in parts:
            if not p.isdigit() or not (0 <= int(p) <= 255):
                raise ValueError(f"Invalid octet in subnet mask: {v}")
        return v

    @field_validator("default_gateway")
    @classmethod
    def validate_gateway(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import ipaddress
        try:
            ipaddress.IPv4Address(v)
        except (ipaddress.AddressValueError, ValueError) as exc:
            raise ValueError(f"Invalid gateway address: {v}") from exc
        return v


class InterfaceInfo(BaseModel):
    """Represents a device interface and its operational state."""
    device: str
    interface_name: str
    ip_address: Optional[str] = None
    status: str          # e.g. "up", "down", "administratively down"
    protocol: str        # e.g. "up", "down"
    admin_state: Optional[str] = None  # e.g. "up", "administratively down", "err-disabled"


class VlanInfo(BaseModel):
    """Represents a VLAN entry in the VLAN database."""
    device: str
    vlan_id: int
    vlan_name: Optional[str] = None
    status: str = "active"
    interfaces: List[str] = []


class VlanAssignment(BaseModel):
    """Represents an interface's access VLAN assignment."""
    device: str
    interface_name: str
    access_vlan: int


class RouteEntry(BaseModel):
    """Represents a single routing-table entry."""
    device: str
    destination: str     # e.g. "10.0.0.0/24" or "0.0.0.0/0"
    next_hop: Optional[str] = None
    outgoing_interface: Optional[str] = None


class RequiredRoute(BaseModel):
    """A destination that must be reachable from a given device."""
    device: str
    destination: str     # e.g. "10.0.0.0/24"


class NetworkSnapshot(BaseModel):
    """Aggregated network configuration snapshot fed to the checker."""
    hosts: List[HostInfo] = []
    interfaces: List[InterfaceInfo] = []
    vlans: List[VlanInfo] = []
    vlan_assignments: List[VlanAssignment] = []
    routes: List[RouteEntry] = []
    required_routes: List[RequiredRoute] = []

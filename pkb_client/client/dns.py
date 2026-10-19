"""DNS record types and serialization helpers."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DNSRecordType(str, Enum):
    """DNS record types supported by the client."""

    A = "A"
    AAAA = "AAAA"
    MX = "MX"
    CNAME = "CNAME"
    ALIAS = "ALIAS"
    TXT = "TXT"
    NS = "NS"
    SRV = "SRV"
    TLSA = "TLSA"
    CAA = "CAA"
    HTTPS = "HTTPS"
    SSHFP = "SSHFP"
    SVCB = "SVCB"

    def __str__(self) -> str:
        """Return the DNS record type token."""
        return self.value


DNS_RECORDS_WITH_PRIORITY = {DNSRecordType.MX, DNSRecordType.SRV}


@dataclass
class DNSRecord:
    """Represent a DNS record returned by the Porkbun API."""

    id: str
    name: str
    type: DNSRecordType
    content: str
    ttl: int
    prio: int | None
    notes: str

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "DNSRecord":
        """Create a DNSRecord instance from a dictionary representation.

        :param d: Dictionary containing DNS record data.
        :return: DNSRecord instance.
        """
        # Use priority only for supported types;
        # the API returns a default value for others.
        prio = int(d["prio"]) if d["type"] in DNS_RECORDS_WITH_PRIORITY else None
        return DNSRecord(
            id=d["id"],
            name=d["name"],
            type=DNSRecordType[d["type"]],
            content=d["content"],
            ttl=int(d["ttl"]),
            prio=prio,
            notes=d["notes"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the DNSRecord instance to a dictionary representation.

        :return: Dictionary containing DNS record data.
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": str(self.type),
            "content": self.content,
            "ttl": self.ttl,
            "prio": self.prio,
            "notes": self.notes,
        }


class DNSRestoreMode(Enum):
    """Strategy used when restoring DNS records from a backup."""

    clear = 0
    replace = 1
    keep = 2

    def __str__(self) -> str:
        """Return the restore-mode name."""
        return self.name

    @staticmethod
    def from_string(a: str) -> "DNSRestoreMode":
        """Convert a string to a DNSRestoreMode enum member.

        :param a: String representation of the restore mode.
        :return: Corresponding DNSRestoreMode enum member.
        :raises KeyError: If the string does not match any enum member.
        """
        return DNSRestoreMode[a]

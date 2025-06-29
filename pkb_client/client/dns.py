from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DNSRecordType(str, Enum):
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

    def __str__(self):
        return self.value


DNS_RECORDS_WITH_PRIORITY = {DNSRecordType.MX, DNSRecordType.SRV}


@dataclass
class DNSRecord:
    id: str
    name: str
    type: DNSRecordType
    content: str
    ttl: int
    prio: Optional[int]
    notes: str

    @staticmethod
    def from_dict(d):
        # only use prio for supported record types since the API returns it for all records with default value 0
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

    def to_dict(self):
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
    clear = 0
    replace = 1
    keep = 2

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(a):
        try:
            return DNSRestoreMode[a]
        except KeyError:
            return a

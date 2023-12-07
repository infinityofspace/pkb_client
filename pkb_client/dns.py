from dataclasses import dataclass
from enum import Enum


@dataclass
class DNSRecord:
    id: str
    name: str
    type: str
    content: str
    ttl: str
    prio: str
    notes: str

    @staticmethod
    def from_dict(d):
        return DNSRecord(
            id=d["id"],
            name=d["name"],
            type=d["type"],
            content=d["content"],
            ttl=d["ttl"],
            prio=d["prio"],
            notes=d["notes"],
        )


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

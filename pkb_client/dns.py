from dataclasses import dataclass
from enum import Enum


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
    ttl: str
    prio: str
    notes: str

    @staticmethod
    def from_dict(d):
        return DNSRecord(
            id=d["id"],
            name=d["name"],
            type=DNSRecordType[d["type"]],
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


class DNSFileFormat(str, Enum):
    BIND = "BIND"
    JSON = "JSON"

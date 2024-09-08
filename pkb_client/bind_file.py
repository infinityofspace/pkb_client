from dataclasses import dataclass
from enum import Enum

from pkb_client.dns import DNSRecordType


class RecordClass(str, Enum):
    IN = "IN"

    def __str__(self):
        return self.value


@dataclass
class BindRecord:
    name: str
    ttl: int
    record_class: RecordClass
    record_type: DNSRecordType
    data: str

    def __str__(self):
        return f"{self.name} {self.ttl} {self.record_class} {self.record_type} {self.data}"


class BindFile:
    origin: str
    ttl: int = None
    records: list[BindRecord]

    @staticmethod
    def from_file(file_path: str) -> "BindFile":
        with open(file_path, "r") as f:
            file_data = f.readlines()

        # TODO: Implement parsing of bind files

    def to_file(self, file_path: str) -> None:
        with open(file_path, "w") as f:
            f.write(str(self))

    def __str__(self) -> str:
        bind = f"$ORIGIN {self.origin}\n"

        if self.ttl is not None:
            bind += f"$TTL {self.ttl}\n"

        for record in self.records:
            bind += f"{record}\n"
        return bind

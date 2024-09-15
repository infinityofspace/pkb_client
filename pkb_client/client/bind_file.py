import logging
from dataclasses import dataclass
from enum import Enum

from pkb_client.client.dns import DNSRecordType


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
    ttl: int | None = None
    records: list[BindRecord]

    def __init__(self, origin: str, ttl: int | None = None, records: list[BindRecord] | None = None) -> None:
        self.origin = origin
        self.ttl = ttl
        self.records = records or []

    @staticmethod
    def from_file(file_path: str) -> "BindFile":
        with open(file_path, "r") as f:
            file_data = f.readlines()

        # parse the file line by line
        origin = None
        ttl = None
        records = []
        for line in file_data:
            if line.startswith("$ORIGIN"):
                origin = line.split()[1]
            elif line.startswith("$TTL"):
                ttl = int(line.split()[1])
            else:
                # parse the records with the two possible formats:
                # 1: name 	ttl 	record-class 	record-type 	record-data
                # 2: name 	record-class 	ttl 	record-type 	record-data
                # whereby the ttl is optional

                # drop any right trailing comments
                line = line.split(";")[0].strip()

                # skip empty lines
                if not line:
                    continue

                # find which format the line is
                record_parts = line.split()
                if record_parts[1].isdigit():
                    # scheme 1
                    if record_parts[3] not in DNSRecordType.__members__:
                        logging.warning(f"Ignoring unsupported record type: {line}")
                        continue
                    record_name = record_parts[0]
                    record_ttl = int(record_parts[1])
                    record_class = RecordClass[record_parts[2]]
                    record_type = DNSRecordType[record_parts[3]]
                    record_data = " ".join(record_parts[4:])
                elif record_parts[2].isdigit():
                    # scheme 2
                    if record_parts[3] not in DNSRecordType.__members__:
                        logging.warning(f"Ignoring unsupported record type: {line}")
                        continue
                    record_name = record_parts[0]
                    record_ttl = int(record_parts[2])
                    record_class = RecordClass[record_parts[1]]
                    record_type = DNSRecordType[record_parts[3]]
                    record_data = " ".join(record_parts[4:])
                else:
                    # no ttl, use default or previous
                    if record_parts[2] not in DNSRecordType.__members__:
                        logging.warning(f"Ignoring unsupported record type: {line}")
                        continue
                    record_name = record_parts[0]
                    if ttl is None and not records:
                        raise ValueError("No TTL found in file")
                    record_ttl = ttl or records[-1].ttl
                    record_class = RecordClass[record_parts[1]]
                    record_type = DNSRecordType[record_parts[2]]
                    record_data = " ".join(record_parts[3:])

                # replace @ in record name with origin
                record_name = record_name.replace("@", origin)

                records.append(BindRecord(record_name, record_ttl, record_class, record_type, record_data))

        if origin is None:
            raise ValueError("No origin found in file")

        return BindFile(origin, ttl, records)

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

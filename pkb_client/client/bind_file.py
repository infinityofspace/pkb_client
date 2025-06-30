import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from pkb_client.client.dns import DNSRecordType, DNS_RECORDS_WITH_PRIORITY


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
    prio: Optional[int] = None
    comment: Optional[str] = None

    def __str__(self):
        record_string = f"{self.name} {self.ttl} {self.record_class} {self.record_type}"
        if self.prio is not None:
            record_string += f" {self.prio}"
        record_string += f' "{self.data}"'
        if self.comment:
            record_string += f" ; {self.comment}"
        return record_string


class BindFile:
    origin: str
    ttl: Optional[int] = None
    records: List[BindRecord]

    def __init__(
        self,
        origin: str,
        ttl: Optional[int] = None,
        records: Optional[List[BindRecord]] = None,
    ) -> None:
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

                record_parts = line.strip().split()

                # skip comments
                if not record_parts or record_parts[0].startswith(";"):
                    continue

                prio = None

                if record_parts[1].isdigit():
                    # scheme 1
                    if record_parts[3] not in DNSRecordType.__members__:
                        logging.warning(f"Ignoring unsupported record type: {line}")
                        continue
                    if record_parts[2] not in RecordClass.__members__:
                        logging.warning(f"Ignoring unsupported record class: {line}")
                        continue
                    record_name = record_parts[0]
                    record_ttl = int(record_parts[1])
                    record_class = RecordClass[record_parts[2]]
                    record_type = DNSRecordType[record_parts[3]]
                    if record_type in DNS_RECORDS_WITH_PRIORITY:
                        prio = int(record_parts[4])
                        record_data = " ".join(record_parts[5:])
                    else:
                        record_data = " ".join(record_parts[4:])
                elif record_parts[2].isdigit():
                    # scheme 2
                    if record_parts[3] not in DNSRecordType.__members__:
                        logging.warning(f"Ignoring unsupported record type: {line}")
                        continue
                    if record_parts[1] not in RecordClass.__members__:
                        logging.warning(f"Ignoring unsupported record class: {line}")
                        continue
                    record_name = record_parts[0]
                    record_ttl = int(record_parts[2])
                    record_class = RecordClass[record_parts[1]]
                    record_type = DNSRecordType[record_parts[3]]
                    if record_type in DNS_RECORDS_WITH_PRIORITY:
                        prio = int(record_parts[4])
                        record_data = " ".join(record_parts[5:])
                    else:
                        record_data = " ".join(record_parts[4:])
                else:
                    # no ttl, use default or previous
                    if record_parts[2] not in DNSRecordType.__members__:
                        logging.warning(f"Ignoring unsupported record type: {line}")
                        continue
                    if record_parts[1] not in RecordClass.__members__:
                        logging.warning(f"Ignoring unsupported record class: {line}")
                        continue
                    record_name = record_parts[0]
                    if ttl is None and not records:
                        raise ValueError("No TTL found in file")
                    record_ttl = ttl or records[-1].ttl
                    record_class = RecordClass[record_parts[1]]
                    record_type = DNSRecordType[record_parts[2]]
                    if record_type in DNS_RECORDS_WITH_PRIORITY:
                        prio = int(record_parts[3])
                        record_data = " ".join(record_parts[4:])
                    else:
                        record_data = " ".join(record_parts[3:])

                # replace @ in record name with origin
                record_name = record_name.replace("@", origin)

                # handle comments and quoted strings as record data
                comment = None
                line = record_data.strip()
                if line.startswith('"'):
                    # find rightmost double quote
                    rindex = line.rfind('"')
                    if rindex != -1:
                        # split at the last double quote
                        line_parts = line.rsplit('"', 1)
                        record_data = line_parts[0].strip('"')

                        comment = line_parts[1].strip() if len(line_parts) > 1 else None
                        # left strip semicolon from comment
                        if comment and comment.startswith(";"):
                            comment = comment[1:].strip()

                        if not comment:
                            comment = None
                    else:
                        record_data = line.strip('"')
                else:
                    # try to split at the first semicolon for comments
                    if ";" in line:
                        record_data, comment = line.split(";", 1)
                        record_data = record_data.strip()
                        comment = comment.strip()
                    else:
                        record_data = line

                records.append(
                    BindRecord(
                        record_name,
                        record_ttl,
                        record_class,
                        record_type,
                        record_data,
                        prio=prio,
                        comment=comment,
                    )
                )

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

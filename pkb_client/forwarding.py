from dataclasses import dataclass
from enum import Enum


class URLForwardingType(str, Enum):
    temporary = "temporary"
    permanent = "permanent"


@dataclass
class URLForwarding:
    id: str
    subdomain: str
    location: str
    type: URLForwardingType
    include_path: bool
    wildcard: bool

    @staticmethod
    def from_dict(d):
        return URLForwarding(
            id=d["id"],
            subdomain=d["subdomain"],
            location=d["location"],
            type=URLForwardingType[d["type"]],
            include_path=d["includePath"] == "yes",
            wildcard=d["wildcard"] == "yes",
        )

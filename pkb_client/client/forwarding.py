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

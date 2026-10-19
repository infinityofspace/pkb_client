"""URL-forwarding types and models."""

from dataclasses import dataclass
from enum import Enum


class URLForwardingType(str, Enum):
    """URL-forwarding redirect type supported by Porkbun."""

    temporary = "temporary"
    permanent = "permanent"


@dataclass
class URLForwarding:
    """Represent a URL-forwarding rule."""

    id: str
    subdomain: str
    location: str
    type: URLForwardingType
    include_path: bool
    wildcard: bool

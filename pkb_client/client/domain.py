"""Domain and glue-record models returned by the Porkbun API."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainInfo:
    """Represent domain registration information."""

    domain: str
    status: str
    tld: str
    create_date: datetime
    expire_date: datetime
    security_lock: bool
    whois_privacy: bool
    auto_renew: bool
    not_local: bool


@dataclass
class DomainPrice:
    """Represent a domain's current and regular prices."""

    type: str
    price: float
    regular_price: float


@dataclass
class DomainAvailability(DomainPrice):
    """Represent domain availability and associated prices."""

    available: bool
    first_year_promo: bool
    premium: bool
    additional_prices: list[DomainPrice]


@dataclass
class DomainCheckRateLimit:
    """Represent the remaining rate-limit information for domain checks."""

    ttl: int
    limit: int
    used: int
    natural_language: str


@dataclass
class GlueRecord:
    """Represent a host and its glue-record IP addresses."""

    host: str
    v4: str | None
    v6: str | None

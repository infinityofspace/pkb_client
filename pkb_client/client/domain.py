from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DomainInfo:
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
    type: str
    price: float
    regular_price: float


@dataclass
class DomainAvailability(DomainPrice):
    available: bool
    first_year_promo: bool
    premium: bool
    additional_prices: list[DomainPrice]


@dataclass
class DomainCheckRateLimit:
    ttl: int
    limit: int
    used: int
    natural_language: str


@dataclass
class GlueRecord:
    host: str
    v4: Optional[str]
    v6: Optional[str]

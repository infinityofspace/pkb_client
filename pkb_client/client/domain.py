from dataclasses import dataclass
from datetime import datetime


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

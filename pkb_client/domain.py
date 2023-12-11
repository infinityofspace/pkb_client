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

    @staticmethod
    def from_dict(d):
        return DomainInfo(
            domain=d["domain"],
            status=d["status"],
            tld=d["tld"],
            create_date=datetime.fromisoformat(d["createDate"]),
            expire_date=datetime.fromisoformat(d["expireDate"]),
            security_lock=bool(d["securityLock"]),
            whois_privacy=bool(d["whoisPrivacy"]),
            auto_renew=bool(d["autoRenew"]),
            not_local=bool(d["notLocal"]),
        )

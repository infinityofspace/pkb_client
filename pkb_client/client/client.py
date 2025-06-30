import json
import logging
from hashlib import sha256
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import urljoin

import dns.resolver
import requests

from pkb_client.client import BindFile
from pkb_client.client.dns import (
    DNS_RECORDS_WITH_PRIORITY,
    DNSRecord,
    DNSRecordType,
    DNSRestoreMode,
)
from pkb_client.client.dnssec import DNSSECRecord
from pkb_client.client.domain import DomainInfo
from pkb_client.client.forwarding import URLForwarding, URLForwardingType
from pkb_client.client.ssl_cert import SSLCertBundle

API_ENDPOINT = "https://api.porkbun.com/api/json/v3/"

logger = logging.getLogger("pkb_client")
logging.basicConfig(level=logging.INFO)


class PKBClientException(Exception):
    def __init__(self, status, message):
        super().__init__(f"{status}: {message}")


class PKBClient:
    """
    API client for Porkbun.
    """

    default_ttl: int = 300

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_api_key: Optional[str] = None,
        api_endpoint: str = API_ENDPOINT,
        debug: bool = False,
    ) -> None:
        """
        Creates a new PKBClient object.

        :param api_key: the API key used for Porkbun API calls
        :param secret_api_key: the API secret used for Porkbun API calls
        :param api_endpoint: the endpoint of the Porkbun API.
        :param debug: boolean to enable debug logging
        """
        self.api_key = api_key
        self.secret_api_key = secret_api_key
        self.api_endpoint = api_endpoint
        self.debug = debug
        if self.debug:
            logger.setLevel(logging.DEBUG)

    def _get_auth_request_json(self) -> dict:
        """
        Get the request json for the authentication of the Porkbun API calls.

        :return: the request json for the authentication of the Porkbun API calls
        """

        if self.api_key is None or self.secret_api_key is None:
            raise ValueError("api_key and secret_api_key must be set")

        return {"apikey": self.api_key, "secretapikey": self.secret_api_key}

    def ping(self) -> str:
        """
        API ping method: get the current public ip address of the requesting system; can also be used for auth checking.
        See https://api.porkbun.com/api/json/v3/documentation#Authentication for more info.

        :return: the current public ip address of the requesting system
        """

        url = urljoin(self.api_endpoint, "ping")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("yourIp", None)
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def create_dns_record(
        self,
        domain: str,
        record_type: DNSRecordType,
        content: str,
        name: Optional[str] = None,
        ttl: int = default_ttl,
        prio: Optional[int] = None,
    ) -> str:
        """
        API DNS create method: create a new DNS record for given domain.
        See https://api.porkbun.com/api/json/v3/documentation#DNS%20Create%20Record for more info.

        :param domain: the domain for which the DNS record should be created
        :param record_type: the type of the new DNS record
        :param content: the content of the new DNS record
        :param name: the subdomain for which the new DNS record entry should apply; the * can be used for a
                     wildcard DNS record; if not used, then a DNS record for the root domain will be created
        :param ttl: the time to live in seconds of the new DNS record; have to be between 300 and 86400
        :param prio: the priority of the new DNS record (only records of type MX and SRV) otherwise None
        :return: the id of the new created DNS record
        """

        if ttl > 86400 or ttl < self.default_ttl:
            raise ValueError(f"ttl must be between {self.default_ttl} and 86400")

        if prio is not None and record_type not in DNS_RECORDS_WITH_PRIORITY:
            raise ValueError(
                f"Priority can only be set for {DNS_RECORDS_WITH_PRIORITY}"
            )

        url = urljoin(self.api_endpoint, f"dns/create/{domain}")
        req_json = {
            **self._get_auth_request_json(),
            "name": name,
            "type": record_type.value,
            "content": content,
            "ttl": ttl,
            "prio": prio,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return str(json.loads(r.text).get("id", None))
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def update_dns_record(
        self,
        domain: str,
        record_id: str,
        record_type: DNSRecordType,
        content: str,
        name: Optional[str] = None,
        ttl: int = default_ttl,
        prio: Optional[int] = None,
    ) -> bool:
        """
        API DNS edit method: edit an existing DNS record specified by the id for a given domain.
        See https://api.porkbun.com/api/json/v3/documentation#DNS%20Edit%20Record for more info.

        :param domain: the domain for which the DNS record should be edited
        :param record_id: the id of the DNS record which should be edited
        :param record_type: the new type of the DNS record
        :param content: the new content of the DNS record
        :param name: the new value of the subdomain for which the DNS record should apply; the * can be used for a
                     wildcard DNS record; if not set, the record will be set for the record domain
        :param ttl: the new time to live in seconds of the DNS record, have to be between 300 and 86400
        :param prio: the priority of the new DNS record (only records of type MX and SRV) otherwise None

        :return: True if the editing was successful
        """

        if ttl > 86400 or ttl < self.default_ttl:
            raise ValueError(f"ttl must be between {self.default_ttl} and 86400")

        if prio is not None and record_type not in DNS_RECORDS_WITH_PRIORITY:
            raise ValueError(
                f"Priority can only be set for {DNS_RECORDS_WITH_PRIORITY}"
            )

        url = urljoin(self.api_endpoint, f"dns/edit/{domain}/{record_id}")
        req_json = {
            **self._get_auth_request_json(),
            "name": name,
            "type": record_type.value,
            "content": content,
            "ttl": ttl,
            "prio": prio,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def update_all_dns_records(
        self,
        domain: str,
        record_type: DNSRecordType,
        subdomain: str,
        content: str,
        ttl: int = default_ttl,
        prio: Optional[int] = None,
    ) -> bool:
        """
        API DNS edit method: edit all existing DNS record matching the domain, record type and subdomain.
        See https://api.porkbun.com/api/json/v3/documentation#DNS%20Edit%20Record%20by%20Domain,%20Subdomain%20and%20Type for more info.

        :param domain: the domain for which the DNS record should be edited
        :param record_type: the type of the DNS record
        :param subdomain: the subdomain of the DNS record can be empty string for root domain
        :param content: the new content of the DNS record
        :param ttl: the new time to live in seconds of the DNS record, have to be between 300 and 86400
        :param prio: the priority of the new DNS record (only records of type MX and SRV) otherwise None

        :return: True if the editing was successful
        """

        if ttl > 86400 or ttl < self.default_ttl:
            raise ValueError(f"ttl must be between {self.default_ttl} and 86400")

        if prio is not None and record_type not in DNS_RECORDS_WITH_PRIORITY:
            raise ValueError(
                f"Priority can only be set for {DNS_RECORDS_WITH_PRIORITY}"
            )

        url = urljoin(
            self.api_endpoint, f"dns/editByNameType/{domain}/{record_type}/{subdomain}"
        )
        req_json = {
            **self._get_auth_request_json(),
            "type": record_type.value,
            "content": content,
            "ttl": ttl,
            "prio": prio,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def delete_dns_record(self, domain: str, record_id: str) -> bool:
        """
        API DNS delete method: delete an existing DNS record specified by the id for a given domain.
        See https://api.porkbun.com/api/json/v3/documentation#DNS%20Delete%20Record for more info.

        :param domain: the domain for which the DNS record should be deleted
        :param record_id: the id of the DNS record which should be deleted

        :return: True if the deletion was successful
        """

        url = urljoin(self.api_endpoint, f"dns/delete/{domain}/{record_id}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def delete_all_dns_records(
        self, domain: str, record_type: DNSRecordType, subdomain: str
    ) -> bool:
        """
        API DNS delete method: delete all existing DNS record matching the domain, record type and subdomain.
        See https://api.porkbun.com/api/json/v3/documentation#DNS%20Delete%20Records%20by%20Domain,%20Subdomain%20and%20Type for more info.

        :param domain: the domain for which the DNS record should be deleted
        :param record_type: the type of the DNS record
        :param subdomain: the subdomain of the DNS record can be empty string for root domain

        :return: True if the deletion was successful
        """

        url = urljoin(
            self.api_endpoint,
            f"dns/deleteByNameType/{domain}/{record_type}/{subdomain}",
        )
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_dns_records(
        self, domain, record_id: Optional[str] = None
    ) -> List[DNSRecord]:
        """
        API DNS retrieve method: retrieve all DNS records for given domain if no record id is specified.
        Otherwise, retrieve the DNS record of the specified domain with the given record id.
        See https://api.porkbun.com/api/json/v3/documentation#DNS%20Retrieve%20Records for more info.

        :param domain: the domain for which the DNS records should be retrieved
        :param record_id: the id of the DNS record which should be retrieved

        :return: list of DNSRecords objects
        """

        if record_id is None:
            url = urljoin(self.api_endpoint, f"dns/retrieve/{domain}")
        else:
            url = urljoin(self.api_endpoint, f"dns/retrieve/{domain}/{record_id}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [
                DNSRecord.from_dict(record)
                for record in json.loads(r.text).get("records", [])
            ]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_all_dns_records(
        self, domain: str, record_type: DNSRecordType, subdomain: str
    ) -> List[DNSRecord]:
        """
        API DNS retrieve method: retrieve all DNS records matching the domain, record type and subdomain.
        See https://api.porkbun.com/api/json/v3/documentation#DNS%20Retrieve%20Records%20by%20Domain,%20Subdomain%20and%20Type for more info.

        :param domain: the domain for which the DNS records should be retrieved
        :param record_type: the type of the DNS records
        :param subdomain: the subdomain of the DNS records can be empty string for root domain

        :return: list of DNSRecords objects
        """

        url = urljoin(
            self.api_endpoint,
            f"dns/retrieveByNameType/{domain}/{record_type}/{subdomain}",
        )
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [
                DNSRecord.from_dict(record)
                for record in json.loads(r.text).get("records", [])
            ]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def export_dns_records(self, domain: str, filepath: Union[Path, str]) -> bool:
        """
        Export all DNS record from the given domain to a json file.
        This method does not represent a Porkbun API method.
        DNS records with all custom fields like notes are exported.

        :param domain: the domain for which the DNS record should be retrieved and saved
        :param filepath: the filepath where to save the exported DNS records

        :return: True if everything went well
        """

        filepath = Path(filepath)

        logger.debug("retrieve current DNS records...")
        dns_records = self.get_dns_records(domain)

        logger.debug("save DNS records to {} ...".format(filepath))
        # merge the single DNS records into one single dict with the record id as key
        dns_records_dict = dict()
        for record in dns_records:
            dns_records_dict[record.id] = record

        if filepath.exists():
            logger.warning("file already exists, overwriting...")

        with open(filepath, "w") as f:
            json.dump(dns_records_dict, f, default=lambda o: o.__dict__, indent=4)

        logger.info("export finished")

        return True

    def export_bind_dns_records(self, domain: str, filepath: Union[Path, str]) -> bool:
        """
        Export all DNS record from the given domain to a BIND file.
        This method does not represent a Porkbun API method.
        Porkbun DNS record notes are exported as comments.

        :param domain: the domain for which the DNS record should be retrieved and saved
        :param filepath: the filepath where to save the exported DNS records

        :return: True if everything went well
        """

        filepath = Path(filepath)

        logger.debug("retrieve current DNS records...")
        dns_records = self.get_dns_records(domain)

        logger.debug("save DNS records to {} ...".format(filepath))
        # merge the single DNS records into one single dict with the record id as key
        dns_records_dict = dict()
        for record in dns_records:
            dns_records_dict[record.id] = record

        if filepath.exists():
            logger.warning("file already exists, overwriting...")

        # domain header
        bind_file_content = f"$ORIGIN {domain}."

        # SOA record
        soa_records = dns.resolver.resolve(domain, "SOA")
        if soa_records:
            soa_record = soa_records[0]
            bind_file_content += f"\n@ IN SOA {soa_record.mname} {soa_record.rname} ({soa_record.serial} {soa_record.refresh} {soa_record.retry} {soa_record.expire} {soa_record.minimum})"

        # records
        for record in dns_records:
            # name 	record class 	ttl 	record type 	record data
            # add trailing dot to the name if it is a supported record type, to make it a fully qualified domain name
            if record.type in [
                DNSRecordType.MX,
                DNSRecordType.CNAME,
                DNSRecordType.NS,
                DNSRecordType.SRV,
            ]:
                record.content += "."
            if record.prio is not None:
                record_content = f"{record.prio} {record.content}"
            else:
                record_content = record.content
            bind_file_content += (
                f"\n{record.name} IN {record.ttl} {record.type} {record_content}"
            )

            if record.notes:
                bind_file_content += f" ; {record.notes}"

        with open(filepath, "w") as f:
            f.write(bind_file_content)

        logger.info("export finished")

        return True

    def import_dns_records(
        self, domain: str, filepath: Union[Path, str], restore_mode: DNSRestoreMode
    ) -> bool:
        """
        Restore all DNS records from a json file to the given domain.
        This method does not represent a Porkbun API method.

        :param domain: the domain for which the DNS record should be restored
        :param filepath: the filepath from which the DNS records are to be restored
        :param restore_mode: The restore mode (DNS records are identified by the record type, name and prio if supported):
            clear: remove all existing DNS records and restore all DNS records from the provided file
            replace: replace only existing DNS records with the DNS records from the provided file,
                     but do not create any new DNS records
            keep: keep the existing DNS records and only create new ones for all DNS records from
                  the specified file if they do not exist

        :return: True if everything went well
        """

        filepath = Path(filepath)

        existing_dns_records = self.get_dns_records(domain)

        with open(filepath, "r") as f:
            exported_dns_records_dict = json.load(f)

        if restore_mode is DNSRestoreMode.clear:
            logger.debug("restore mode: clear")

            try:
                # delete all existing DNS records
                for record in existing_dns_records:
                    self.delete_dns_record(domain, record.id)

                # restore all exported records by creating new DNS records
                for _, exported_record in exported_dns_records_dict.items():
                    name = ".".join(exported_record["name"].split(".")[:-2])
                    self.create_dns_record(
                        domain=domain,
                        record_type=DNSRecordType(exported_record["type"]),
                        content=exported_record["content"],
                        name=name,
                        ttl=exported_record["ttl"],
                        prio=exported_record["prio"],
                    )
            except Exception as e:
                logger.error("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                logger.error("import failed")
                return False
        elif restore_mode is DNSRestoreMode.replace:
            logger.debug("restore mode: replace")

            try:
                existing_dns_record_hashed = {
                    sha256(
                        f"{record.type}{record.name}{record.prio}".encode()
                    ).hexdigest(): record
                    for record in existing_dns_records
                }
                for record in exported_dns_records_dict.values():
                    record_hash = sha256(
                        f"{record['type']}{record['name']}{record['prio']}".encode()
                    ).hexdigest()
                    existing_record = existing_dns_record_hashed.get(record_hash, None)
                    # check if the exported dns record is different to the existing record,
                    # so we can reduce unnecessary api calls
                    if existing_record is not None and (
                        record["content"] != existing_record.content
                        or record["ttl"] != existing_record.ttl
                        or record["prio"] != existing_record.prio
                    ):
                        self.update_dns_record(
                            domain=domain,
                            record_id=existing_record.id,
                            record_type=DNSRecordType(record["type"]),
                            content=record["content"],
                            name=record["name"].replace(f".{domain}", ""),
                            ttl=record["ttl"],
                            prio=record["prio"],
                        )
            except Exception as e:
                logger.error("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                logger.error("import failed")
                return False
        elif restore_mode is DNSRestoreMode.keep:
            logger.debug("restore mode: keep")

            existing_dns_record_hashed = {
                sha256(
                    f"{record.type}{record.name}{record.prio}".encode()
                ).hexdigest(): record
                for record in existing_dns_records
            }

            try:
                for record in exported_dns_records_dict.values():
                    record_hash = sha256(
                        f"{record['type']}{record['name']}{record['prio']}".encode()
                    ).hexdigest()
                    existing_record = existing_dns_record_hashed.get(record_hash, None)
                    if existing_record is None:
                        self.create_dns_record(
                            domain=domain,
                            record_type=DNSRecordType(record["type"]),
                            content=record["content"],
                            name=record["name"].replace(f".{domain}", ""),
                            ttl=record["ttl"],
                            prio=record["prio"],
                        )
            except Exception as e:
                logger.error("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                logger.error("import failed")
                return False
        else:
            raise Exception("restore mode not supported")

        logger.info("import successfully completed")

        return True

    def import_bind_dns_records(
        self, filepath: Union[Path, str], restore_mode: DNSRestoreMode
    ) -> bool:
        """
        Restore all DNS records from a BIND file.
        This method does not represent a Porkbun API method.

        :param filepath: the bind filepath from which the DNS records are to be restored
        :param restore_mode: The restore mode:
            clear: remove all existing DNS records and restore all DNS records from the provided file
        :return: True if everything went well
        """

        bind_file = BindFile.from_file(filepath)

        existing_dns_records = self.get_dns_records(bind_file.origin[:-1])

        if restore_mode is DNSRestoreMode.clear:
            logger.debug("restore mode: clear")

            try:
                # delete all existing DNS records
                for record in existing_dns_records:
                    self.delete_dns_record(bind_file.origin[:-1], record.id)

                nameserver_records = []
                # restore all records from BIND file by creating new DNS records
                for record in bind_file.records:
                    if record.record_type == DNSRecordType.NS:
                        # collect nameserver records to update them later in bulk
                        nameserver_records.append(record)
                        continue
                    if record.name.endswith("."):
                        # extract subdomain from record name, by removing the domain and TLD
                        subdomain = record.name.removesuffix(bind_file.origin)
                        subdomain = subdomain.removesuffix(".")
                    else:
                        subdomain = record.name

                    self.create_dns_record(
                        domain=bind_file.origin[:-1],
                        record_type=record.record_type,
                        content=record.data,
                        name=subdomain,
                        ttl=record.ttl,
                        prio=record.prio,
                    )

                # update nameservers in bulk
                if nameserver_records:
                    name_servers = []
                    # remove trailing dot from nameserver records
                    for nameserver in nameserver_records:
                        if nameserver.data.endswith("."):
                            name_servers.append(nameserver.data[:-1])
                        else:
                            name_servers.append(nameserver.data)
                    self.update_dns_servers(bind_file.origin[:-1], name_servers)

            except Exception as e:
                logger.error("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                logger.error("import failed")
                return False
        else:
            raise Exception(f"restore mode '{restore_mode.value}' not supported")

        logger.info("import successfully completed")

        return True

    def update_dns_servers(self, domain: str, name_servers: List[str]) -> bool:
        """
        Update the name servers of the specified domain.
        See https://api.porkbun.com/api/json/v3/documentation#Domain%20Update%20Name%20Servers for more info.

        :return: True if everything went well
        """

        url = urljoin(self.api_endpoint, f"domain/updateNs/{domain}")
        req_json = {**self._get_auth_request_json(), "ns": name_servers}
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200 and json.loads(r.text).get("status", None) == "SUCCESS":
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_dns_servers(self, domain: str) -> List[str]:
        """
        Get the name servers for the given domain.
        See https://api.porkbun.com/api/json/v3/documentation#Domain%20Get%20Name%20Servers for more info.

        :return: list of name servers
        """

        url = urljoin(self.api_endpoint, f"domain/getNs/{domain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("ns", [])
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_domains(self, start: int = 0) -> List[DomainInfo]:
        """
        Get all domains for the account in chunks of 1000. If you reach the end of all domains, the list will be empty.
        See https://api.porkbun.com/api/json/v3/documentation#Domain%20List%20All for more info.

        :param start: the index of the first domain to retrieve

        :return: list of DomainInfo objects
        """

        url = urljoin(self.api_endpoint, "domain/listAll")

        req_json = {**self._get_auth_request_json(), "start": start}
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [
                DomainInfo.from_dict(domain)
                for domain in json.loads(r.text).get("domains", [])
            ]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_url_forwards(self, domain: str) -> List[URLForwarding]:
        """
        Get the url forwarding for the given domain.
        See https://api.porkbun.com/api/json/v3/documentation#Domain%20Get%20URL%20Forwarding for more info.

        :return: list of URLForwarding objects
        """

        url = urljoin(self.api_endpoint, f"domain/getUrlForwarding/{domain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [
                URLForwarding.from_dict(forwarding)
                for forwarding in json.loads(r.text).get("forwards", [])
            ]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def create_url_forward(
        self,
        domain: str,
        subdomain: str,
        location: str,
        type: URLForwardingType,
        include_path: bool,
        wildcard: bool,
    ) -> bool:
        """
        Add a url forward for the given domain.
        See https://api.porkbun.com/api/json/v3/documentation#Domain%20Add%20URL%20Forward for more info.

        :param domain: the domain for which the url forwarding should be added
        :param subdomain: the subdomain for which the url forwarding should be added, can be empty for root domain
        :param location: the location to which the url forwarding should redirect
        :param type: the type of the url forwarding
        :param include_path: if the path should be included in the url forwarding
        :param wildcard: if the url forwarding should also be applied to all subdomains

        :return: True if the forwarding was added successfully
        """

        url = urljoin(self.api_endpoint, f"domain/addUrlForward/{domain}")
        req_json = {
            **self._get_auth_request_json(),
            "subdomain": subdomain,
            "location": location,
            "type": type.value,
            "includePath": include_path,
            "wildcard": wildcard,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def delete_url_forward(self, domain: str, id: str) -> bool:
        """
        Delete an url forward for the given domain.
        See https://api.porkbun.com/api/json/v3/documentation#Domain%20Delete%20URL%20Forward for more info.

        :param domain: the domain for which the url forwarding should be deleted
        :param id: the id of the url forwarding which should be deleted

        :return: True if the deletion was successful
        """

        url = urljoin(self.api_endpoint, f"domain/deleteUrlForward/{domain}/{id}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_domain_pricing(self) -> dict:
        """
        Get the pricing for all Porkbun domains.
        See https://api.porkbun.com/api/json/v3/documentation#Domain%20Pricing for more info.

        :return: dict with pricing
        """

        url = urljoin(self.api_endpoint, "pricing/get")
        r = requests.post(url=url)

        if r.status_code == 200:
            return json.loads(r.text)["pricing"]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_ssl_bundle(self, domain) -> SSLCertBundle:
        """
        API SSL bundle retrieve method: retrieve an SSL bundle for the given domain.
        See https://api.porkbun.com/api/json/v3/documentation#SSL%20Retrieve%20Bundle%20by%20Domain for more info.

        :param domain: the domain for which the SSL bundle should be retrieved

        :return: tuple of intermediate certificate, certificate chain, private key, public key
        """

        url = urljoin(self.api_endpoint, f"ssl/retrieve/{domain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            ssl_bundle = json.loads(r.text)

            return SSLCertBundle(
                certificate_chain=ssl_bundle["certificatechain"],
                private_key=ssl_bundle["privatekey"],
                public_key=ssl_bundle["publickey"],
            )
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def get_dnssec_records(self, domain: str) -> List[DNSSECRecord]:
        """
        API DNSSEC retrieve method: retrieve all DNSSEC records for the given domain.
        See https://porkbun.com/api/json/v3/documentation#DNSSEC%20Get%20Records for more info.

        :param domain: the domain for which the DNSSEC records should be retrieved
        :return: list of :class:`DNSSECRecord` objects
        """

        url = urljoin(self.api_endpoint, f"dns/getDnssecRecords/{domain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [
                DNSSECRecord.from_dict(record)
                for record in json.loads(r.text).get("records", {}).values()
            ]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def create_dnssec_record(
        self,
        domain: str,
        key_tag: int,
        alg: int,
        digest_type: int,
        digest: str,
        max_sig_life: Optional[int] = None,
        key_data_flags: Optional[int] = None,
        key_data_protocol: Optional[int] = None,
        key_data_algo: Optional[int] = None,
        key_data_pub_key: Optional[str] = None,
    ) -> bool:
        """
        API DNSSEC create method: create a new DNSSEC record for the given domain.
        See https://porkbun.com/api/json/v3/documentation#DNSSEC%20Create%20Record for more info.

        :param domain: the domain for which the DNSSEC record should be created
        :param key_tag: the key tag of the DNSSEC record
        :param alg: algorithm of the DNSSEC record
        :param digest_type: digest type of the DNSSEC record
        :param digest: digest of the DNSSEC record
        :param max_sig_life: maximum signature life of the DNSSEC record in seconds
        :param key_data_flags: key data flags of the DNSSEC record
        :param key_data_protocol: key data protocol of the DNSSEC record
        :param key_data_algo: key data algorithm of the DNSSEC record
        :param key_data_pub_key: key data public key of the DNSSEC record

        :return: True if everything went well
        """

        if max_sig_life is not None and max_sig_life < 0:
            raise ValueError("max_sig_life must be greater than 0")

        url = urljoin(self.api_endpoint, f"dns/createDnssecRecord/{domain}")
        req_json = {
            **self._get_auth_request_json(),
            "keyTag": key_tag,
            "alg": alg,
            "digestType": digest_type,
            "digest": digest,
            "maxSigLife": max_sig_life,
            "keyDataFlags": key_data_flags,
            "keyDataProtocol": key_data_protocol,
            "keyDataAlgo": key_data_algo,
            "keyDataPubKey": key_data_pub_key,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    def delete_dnssec_record(self, domain: str, key_tag: int) -> bool:
        """
        API DNSSEC delete method: delete an existing DNSSEC record for the given domain.
        See https://porkbun.com/api/json/v3/documentation#DNSSEC%20Delete%20Record for more info.

        :param domain: the domain for which the DNSSEC record should be deleted
        :param key_tag: the key tag of the DNSSEC record
        :return: True if everything went well
        """

        url = urljoin(self.api_endpoint, f"dns/deleteDnssecRecord/{domain}/{key_tag}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(
                response_json.get("status", "Unknown status"),
                response_json.get("message", "Unknown message"),
            )

    @staticmethod
    def __handle_error_backup__(dns_records: list[DNSRecord]) -> None:
        """
        Handle errors when working with dns records by creating a backup of the given DNS records.
        Crates a backup file in the current working directory with an incremental suffix.

        :param dns_records: the DNS records to backup
        """

        # merge the single DNS records into one single dict with the record id as key
        dns_records_dict = dict()
        for record in dns_records:
            dns_records_dict[record.id] = record.to_dict()

        # generate filename with incremental suffix
        base_backup_filename = "pkb_client_dns_records_backup"
        suffix = 0
        backup_file_path = Path("{}_{}.json".format(base_backup_filename, suffix))
        while backup_file_path.exists():
            suffix += 1
            backup_file_path = Path("{}_{}.json".format(base_backup_filename, suffix))

        with open(backup_file_path, "w") as f:
            json.dump(dns_records_dict, f)

        logger.warning(
            "a backup of your existing dns records was saved to {}".format(
                str(backup_file_path)
            )
        )

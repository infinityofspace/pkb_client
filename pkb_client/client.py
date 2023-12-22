import json
import logging
from pathlib import Path
from typing import Optional, List
from urllib.parse import urljoin

import requests

from pkb_client.dns import DNSRecord, DNSRestoreMode, DNSRecordType
from pkb_client.domain import DomainInfo
from pkb_client.forwarding import URLForwarding, URLForwardingType
from pkb_client.ssl_cert import SSLCertBundle

API_ENDPOINT = "https://porkbun.com/api/json/v3/"

# prevent urllib3 to log request with the api key and secret
logging.getLogger("urllib3").setLevel(logging.WARNING)


class PKBClientException(Exception):
    def __init__(self, status, message):
        super().__init__(f"{status}: {message}")


class PKBClient:
    """
    API client for Porkbun.
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 secret_api_key: Optional[str] = None,
                 api_endpoint: str = API_ENDPOINT) -> None:
        """
        Creates a new PKBClient object.

        :param api_key: the API key used for Porkbun API calls
        :param secret_api_key: the API secret used for Porkbun API calls
        """

        self.api_key = api_key
        self.secret_api_key = secret_api_key
        self.api_endpoint = api_endpoint

    def _get_auth_request_json(self) -> dict:
        """
        Get the request json for the authentication of the Porkbun API calls.

        :return: the request json for the authentication of the Porkbun API calls
        """

        assert self.api_key is not None and len(self.api_key) > 0
        assert self.secret_api_key is not None and len(self.secret_api_key) > 0

        return {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key
        }

    def ping(self, **kwargs) -> str:
        """
        API ping method: get the current public ip address of the requesting system; can also be used for auth checking.
        See https://porkbun.com/api/json/v3/documentation#Authentication for more info.

        :return: the current public ip address of the requesting system
        """

        url = urljoin(self.api_endpoint, "ping")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("yourIp", None)
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_create(self,
                   domain: str,
                   record_type: DNSRecordType,
                   content: str,
                   name: Optional[str] = None,
                   ttl: Optional[int] = 300,
                   prio: Optional[int] = None, **kwargs) -> str:
        """
        API DNS create method: create a new DNS record for given domain.
        See https://porkbun.com/api/json/v3/documentation#DNS%20Create%20Record for more info.

        :param domain: the domain for which the DNS record should be created
        :param record_type: the type of the new DNS record
        :param content: the content of the new DNS record
        :param name: the subdomain for which the new DNS record entry should apply; the * can be used for a
                     wildcard DNS record; if not used, then a DNS record for the root domain will be created
        :param ttl: the time to live in seconds of the new DNS record; have to be between 0 and 2147483647
        :param prio: the priority of the new DNS record

        :return: the id of the new created DNS record
        """

        assert domain is not None and len(domain) > 0
        assert content is not None and len(content) > 0
        assert ttl is None or 300 <= ttl <= 2147483647

        url = urljoin(self.api_endpoint, f"dns/create/{domain}")
        req_json = {
            **self._get_auth_request_json(),
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": ttl,
            "prio": prio
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return str(json.loads(r.text).get("id", None))
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_edit(self,
                 domain: str,
                 record_id: str,
                 record_type: DNSRecordType,
                 content: str,
                 name: str = None,
                 ttl: int = 300,
                 prio: int = None,
                 **kwargs) -> bool:
        """
        API DNS edit method: edit an existing DNS record specified by the id for a given domain.
        See https://porkbun.com/api/json/v3/documentation#DNS%20Edit%20Record for more info.

        :param domain: the domain for which the DNS record should be edited
        :param record_id: the id of the DNS record which should be edited
        :param record_type: the new type of the DNS record
        :param content: the new content of the DNS record
        :param name: the new value of the subdomain for which the DNS record should apply; the * can be used for a
                     wildcard DNS record; if not set, the record will be set for the record domain
        :param ttl: the new time to live in seconds of the DNS record, have to be between 0 and 2147483647
        :param prio: the new priority of the DNS record

        :return: True if the editing was successful
        """

        assert domain is not None and len(domain) > 0
        assert record_id is not None and len(record_id) > 0
        assert content is not None and len(content) > 0
        assert ttl is None or 300 <= ttl <= 2147483647

        url = urljoin(self.api_endpoint, f"dns/edit/{domain}/{record_id}")
        req_json = {
            **self._get_auth_request_json(),
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": ttl,
            "prio": prio
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_edit_all(self,
                     domain: str,
                     record_type: DNSRecordType,
                     subdomain: str,
                     content: str,
                     ttl: int = 300,
                     prio: int = None, **kwargs) -> bool:
        """
        API DNS edit method: edit all existing DNS record matching the domain, record type and subdomain.
        See https://porkbun.com/api/json/v3/documentation#DNS%20Edit%20Record%20by%20Domain,%20Subdomain%20and%20Type for more info.

        :param domain: the domain for which the DNS record should be edited
        :param record_type: the type of the DNS record
        :param subdomain: the subdomain of the DNS record can be empty string for root domain
        :param content: the new content of the DNS record
        :param ttl: the new time to live in seconds of the DNS record, have to be between 0 and 2147483647
        :param prio: the new priority of the DNS record

        :return: True if the editing was successful
        """

        assert domain is not None and len(domain) > 0
        assert content is not None and len(content) > 0

        url = urljoin(self.api_endpoint, f"dns/editByNameType/{domain}/{record_type}/{subdomain}")
        req_json = {
            **self._get_auth_request_json(),
            "type": record_type,
            "content": content,
            "ttl": ttl,
            "prio": prio
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_delete(self,
                   domain: str,
                   record_id: str,
                   **kwargs) -> bool:
        """
        API DNS delete method: delete an existing DNS record specified by the id for a given domain.
        See https://porkbun.com/api/json/v3/documentation#DNS%20Delete%20Record for more info.

        :param domain: the domain for which the DNS record should be deleted
        :param record_id: the id of the DNS record which should be deleted

        :return: True if the deletion was successful
        """

        assert domain is not None and len(domain) > 0
        assert record_id is not None and len(record_id) > 0

        url = urljoin(self.api_endpoint, f"dns/delete/{domain}/{record_id}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_delete_all(self,
                       domain: str,
                       record_type: DNSRecordType,
                       subdomain: str,
                       **kwargs) -> bool:
        """
        API DNS delete method: delete all existing DNS record matching the domain, record type and subdomain.
        See https://porkbun.com/api/json/v3/documentation#DNS%20Delete%20Records%20by%20Domain,%20Subdomain%20and%20Type for more info.

        :param domain: the domain for which the DNS record should be deleted
        :param record_type: the type of the DNS record
        :param subdomain: the subdomain of the DNS record can be empty string for root domain

        :return: True if the deletion was successful
        """

        assert domain is not None and len(domain) > 0
        assert record_type is not None

        url = urljoin(self.api_endpoint, f"dns/deleteByNameType/{domain}/{record_type}/{subdomain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_retrieve(self, domain, **kwargs) -> List[DNSRecord]:
        """
        API DNS retrieve method: retrieve all DNS records for given domain.
        See https://porkbun.com/api/json/v3/documentation#DNS%20Retrieve%20Records for more info

        :param domain: the domain for which the DNS records should be retrieved

        :return: list of DNSRecords objects
        """

        assert domain is not None and len(domain) > 0

        url = urljoin(self.api_endpoint, "dns/retrieve/{}".format(domain))
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [DNSRecord.from_dict(record) for record in json.loads(r.text).get("records", [])]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_retrieve_all(self,
                         domain: str,
                         record_type: DNSRecordType,
                         subdomain: str,
                         **kwargs) -> List[DNSRecord]:
        """
        API DNS retrieve method: retrieve all DNS records matching the domain, record type and subdomain.
        See https://porkbun.com/api/json/v3/documentation#DNS%20Retrieve%20Records%20by%20Domain,%20Subdomain%20and%20Type for more info.

        :param domain: the domain for which the DNS records should be retrieved
        :param record_type: the type of the DNS records
        :param subdomain: the subdomain of the DNS records can be empty string for root domain

        :return: list of DNSRecords objects
        """

        assert domain is not None and len(domain) > 0
        assert record_type is not None

        url = urljoin(self.api_endpoint, f"dns/retrieveByNameType/{domain}/{record_type}/{subdomain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [DNSRecord.from_dict(record) for record in json.loads(r.text).get("records", [])]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def dns_export(self, domain: str, filename: str, **kwargs) -> bool:
        """
        Export all DNS record from the given domain as json to a file.
        This method does not represent a Porkbun API method.

        :param domain: the domain for which the DNS record should be retrieved and saved
        :param filename: the filename where to save the exported DNS records

        :return: True if everything went well
        """

        assert domain is not None and len(domain) > 0
        assert filename is not None and len(filename) > 0

        logging.info("retrieve current DNS records...")
        dns_records = self.dns_retrieve(domain)

        logging.info("save DNS records to {} ...".format(filename))
        # merge the single DNS records into one single dict with the record id as key
        dns_records_dict = dict()
        for record in dns_records:
            dns_records_dict[record.id] = record

        filepath = Path(filename)
        if filepath.exists():
            raise Exception("File already exists. Please try another filename")
        with open(filepath, "w") as f:
            json.dump(dns_records_dict, f)
        logging.info("export finished")

        return True

    def dns_import(self, domain: str, filename: str, restore_mode: DNSRestoreMode, **kwargs) -> bool:
        """
        Restore all DNS records from a json file to the given domain.
        This method does not represent a Porkbun API method.

        :param domain: the domain for which the DNS record should be restored
        :param filename: the filename from which the DNS records are to be restored
        :param restore_mode: The restore mode (DNS records are identified by the record id)
            clean: remove all existing DNS records and restore all DNS records from the provided file
            replace: replace only existing DNS records with the DNS records from the provided file,
                     but do not create any new DNS records
            keep: keep the existing DNS records and only create new ones for all DNS records from
                  the specified file if they do not exist

        :return: True if everything went well
        """

        assert domain is not None and len(domain) > 0
        assert filename is not None and len(filename) > 0
        assert isinstance(restore_mode, DNSRestoreMode)

        existing_dns_records = self.dns_retrieve(domain)

        with open(filename, "r") as f:
            exported_dns_records_dict = json.load(f)

        if restore_mode is DNSRestoreMode.clear:
            logging.debug("restore mode: clear")

            try:
                # delete all existing DNS records
                for record in existing_dns_records:
                    self.dns_delete(domain, record.id)

                # restore all exported records by creating new DNS records
                for _, exported_record in exported_dns_records_dict.items():
                    name = ".".join(exported_record["name"].split(".")[:-2])
                    self.dns_create(domain=domain,
                                    record_type=exported_record["type"],
                                    content=exported_record["content"],
                                    name=name,
                                    ttl=exported_record["ttl"],
                                    prio=exported_record["prio"])
            except Exception as e:
                logging.error("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                logging.error("import failed")
                return False
        elif restore_mode is DNSRestoreMode.replace:
            logging.debug("restore mode: replace")

            try:
                for existing_record in existing_dns_records:
                    record_id = existing_record.id
                    exported_record = exported_dns_records_dict.get(record_id, None)
                    # also check if the exported dns record is different to the existing record,
                    # so we can reduce unnecessary api calls
                    if exported_record is not None and exported_record != existing_record:
                        name = ".".join(exported_record["name"].split(".")[:-2])
                        self.dns_edit(domain=domain,
                                      record_id=record_id,
                                      record_type=exported_record["type"],
                                      content=exported_record["content"],
                                      name=name,
                                      ttl=exported_record["ttl"],
                                      prio=exported_record["prio"])
            except Exception as e:
                print("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                print("import failed")
                return False
        elif restore_mode is DNSRestoreMode.keep:
            logging.debug("restore mode: keep")

            existing_dns_records_dict = dict()
            for record in existing_dns_records:
                existing_dns_records_dict[record.id] = record

            try:
                for _, exported_record in exported_dns_records_dict.items():
                    if exported_record["id"] not in existing_dns_records_dict:
                        name = ".".join(exported_record["name"].split(".")[:-2])
                        self.dns_create(domain=domain,
                                        record_type=exported_record["type"],
                                        content=exported_record["content"],
                                        name=name,
                                        ttl=exported_record["ttl"],
                                        prio=exported_record["prio"])
            except Exception as e:
                print("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                print("import failed")
                return False
        else:
            raise Exception("restore mode not supported")

        logging.info("import successfully completed")

        return True

    def update_dns_servers(self, domain: str, name_servers: List[str], **kwargs) -> bool:
        """
        Update the name servers of the specified domain.
        See https://porkbun.com/api/json/v3/documentation#Domain%20Update%20Name%20Servers for more info.

        :return: True if everything went well
        """

        assert domain is not None and len(domain) > 0
        assert name_servers is not None and len(name_servers) > 0

        url = urljoin(self.api_endpoint, f"domain/updateNs/{domain}")
        req_json = {
            **self._get_auth_request_json(),
            "ns": name_servers
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200 and json.loads(r.text).get("status", None) == "SUCCESS":
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def get_dns_servers(self, domain: str, **kwargs) -> List[str]:
        """
        Get the name servers for the given domain.
        See https://porkbun.com/api/json/v3/documentation#Domain%20Get%20Name%20Servers for more info.

        :return: list of name servers
        """

        assert domain is not None and len(domain) > 0

        url = urljoin(self.api_endpoint, f"domain/getNs/{domain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("ns", [])
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def list_domains(self, start: int = 0, **kwargs) -> List[DomainInfo]:
        """
        Get all domains for the account in chunks of 1000. If you reach the end of all domains, the list will be empty.
        See https://porkbun.com/api/json/v3/documentation#Domain%20List%20All for more info.

        :param start: the index of the first domain to retrieve

        :return: list of DomainInfo objects
        """
        assert start >= 0

        url = urljoin(self.api_endpoint, "domain/listAll")

        req_json = {
            **self._get_auth_request_json(),
            "start": start
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [DomainInfo.from_dict(domain) for domain in json.loads(r.text).get("domains", [])]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def get_url_forward(self, domain: str, **kwargs) -> List[URLForwarding]:
        """
        Get the url forwarding for the given domain.
        See https://porkbun.com/api/json/v3/documentation#Domain%20Get%20URL%20Forwarding for more info.

        :return: list of URLForwarding objects
        """

        assert domain is not None and len(domain) > 0

        url = urljoin(self.api_endpoint, f"domain/getUrlForwarding/{domain}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [URLForwarding.from_dict(forwarding) for forwarding in json.loads(r.text).get("forwards", [])]
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def add_url_forward(self,
                        domain: str,
                        subdomain: str,
                        location: str,
                        type: URLForwardingType,
                        include_path: bool,
                        wildcard: bool,
                        **kwargs) -> bool:
        """
        Add an url forward for the given domain.
        See https://porkbun.com/api/json/v3/documentation#Domain%20Add%20URL%20Forward for more info.

        :param domain: the domain for which the url forwarding should be added
        :param subdomain: the subdomain for which the url forwarding should be added, can be empty for root domain
        :param location: the location to which the url forwarding should redirect
        :param type: the type of the url forwarding
        :param include_path: if the path should be included in the url forwarding
        :param wildcard: if the url forwarding should also be applied to all subdomains

        :return: True if the forwarding was added successfully
        """

        assert domain is not None and len(domain) > 0
        assert location is not None and len(location) > 0
        assert type is not None

        url = urljoin(self.api_endpoint, f"domain/addUrlForward/{domain}")
        req_json = {
            **self._get_auth_request_json(),
            "subdomain": subdomain,
            "location": location,
            "type": type,
            "includePath": include_path,
            "wildcard": wildcard
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def delete_url_forward(self, domain: str, id: str, **kwargs) -> bool:
        """
        Delete an url forward for the given domain.
        See https://porkbun.com/api/json/v3/documentation#Domain%20Delete%20URL%20Forward for more info.

        :param domain: the domain for which the url forwarding should be deleted
        :param id: the id of the url forwarding which should be deleted

        :return: True if the deletion was successful
        """

        assert domain is not None and len(domain) > 0
        assert id is not None and len(id) > 0

        url = urljoin(self.api_endpoint, f"domain/deleteUrlForward/{domain}/{id}")
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def get_domain_pricing(self, **kwargs) -> dict:
        """
        Get the pricing for all Porkbun domains.
        See https://porkbun.com/api/json/v3/documentation#Domain%20Pricing for more info.

        :return: dict with pricing
        """

        url = urljoin(self.api_endpoint, "pricing/get")
        r = requests.post(url=url)

        if r.status_code == 200:
            return json.loads(r.text)
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    def ssl_retrieve(self, domain, **kwargs) -> SSLCertBundle:
        """
        API SSL bundle retrieve method: retrieve an SSL bundle for the given domain.
        See https://porkbun.com/api/json/v3/documentation#SSL%20Retrieve%20Bundle%20by%20Domain for more info.

        :param domain: the domain for which the SSL bundle should be retrieved

        :return: tuple of intermediate certificate, certificate chain, private key, public key
        """

        assert domain is not None and len(domain) > 0

        url = urljoin(self.api_endpoint, "ssl/retrieve/{}".format(domain))
        req_json = self._get_auth_request_json()
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            ssl_bundle = json.loads(r.text)

            return SSLCertBundle(intermediate_certificate=ssl_bundle["intermediate_certificate"],
                                 certificate_chain=ssl_bundle["certificate_chain"],
                                 private_key=ssl_bundle["private_key"],
                                 public_key=ssl_bundle["public_key"])
        else:
            response_json = json.loads(r.text)
            raise PKBClientException(response_json.get("status", "Unknown status"),
                                     response_json.get("message", "Unknown message"))

    @staticmethod
    def __handle_error_backup__(dns_records):
        # merge the single DNS records into one single dict with the record id as key
        dns_records_dict = dict()
        for record in dns_records:
            dns_records_dict[record["id"]] = record

        # generate filename with incremental suffix
        base_backup_filename = "pkb_client_dns_records_backup"
        suffix = 0
        backup_file_path = Path("{}_{}.json".format(base_backup_filename, suffix))
        while backup_file_path.exists():
            suffix += 1
            backup_file_path = Path("{}_{}.json".format(base_backup_filename, suffix))

        with open(backup_file_path, "w") as f:
            json.dump(dns_records_dict, f)

        print("a backup of your existing dns records was saved to {}".format(str(backup_file_path)))

import json
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests

from pkb_client.helper import parse_dns_record

API_ENDPOINT = "https://porkbun.com/api/json/v3/"
SUPPORTED_DNS_RECORD_TYPES = ["A", "AAAA", "MX", "CNAME", "ALIAS", "TXT", "NS", "SRV", "TLSA", "CAA"]


class DNSRestoreMode(Enum):
    clear = 0
    replace = 1
    keep = 2

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(a):
        try:
            return DNSRestoreMode[a]
        except KeyError:
            return a


class PKBClient:
    """
    API client for Porkbun.
    """

    def __init__(self, api_key: str, secret_api_key: str) -> None:
        """
        Creates a new PKBClient object.

        :param api_key: the API key used for Porkbun API calls
        :param secret_api_key: the API secret used for Porkbun API calls
        """

        assert api_key is not None and len(api_key) > 0
        assert secret_api_key is not None and len(secret_api_key) > 0

        self.api_key = api_key
        self.secret_api_key = secret_api_key

    def ping(self, **kwargs) -> str:
        """
        API ping method: get the current public ip address of the requesting system; can also be used for auth checking
        see https://porkbun.com/api/json/v3/documentation#Authentication for more info

        :return: the current public ip address of the requesting system
        """

        url = urljoin(API_ENDPOINT, "ping")
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("yourIp", None)
        else:
            raise Exception("ERROR: ping api call was not successfully\n"
                            "Status code: {}\n"
                            "Message: {}".format(r.status_code, json.loads(r.text).get("message", "no message found")))

    def dns_create(self,
                   domain: str,
                   record_type: str,
                   content: str,
                   name: Optional[str] = None,
                   ttl: Optional[int] = 300,
                   prio: Optional[int] = None, **kwargs) -> str:
        """
        API DNS create method: create a new DNS record for given domain
        see https://porkbun.com/api/json/v3/documentation#DNS%20Create%20Record for more info

        :param domain: the domain for which the DNS record should be created
        :param record_type: the type of the new DNS record;
                            supported DNS record types: A, AAAA, MX, CNAME, ALIAS, TXT, NS, SRV, TLSA, CAA
        :param content: the content of the new DNS record
        :param name: the subdomain for which the new DNS record entry should apply; the * can be used for a
                     wildcard DNS record; if not used, then a DNS record for the root domain will be created
        :param ttl: the time to live in seconds of the new DNS record; have to be between 0 and 2147483647
        :param prio: the priority of the new DNS record

        :return: the id of the new created DNS record
        """

        assert domain is not None and len(domain) > 0
        assert record_type in SUPPORTED_DNS_RECORD_TYPES
        assert content is not None and len(content) > 0
        assert ttl is None or 300 <= ttl <= 2147483647

        url = urljoin(API_ENDPOINT, "dns/create/{}".format(domain))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key,
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
            raise Exception("ERROR: DNS create api call was not successfully\n"
                            "Status code: {}\n"
                            "Message: {}".format(r.status_code, json.loads(r.text).get("message", "no message found")))

    def dns_edit(self,
                 domain: str,
                 record_id: str,
                 record_type: str,
                 content: str,
                 name: str = None,
                 ttl: int = 300,
                 prio: int = None,
                 **kwargs) -> bool:
        """
        API DNS edit method: edit an existing DNS record specified by the id for a given domain
        see https://porkbun.com/api/json/v3/documentation#DNS%20Edit%20Record for more info

        :param domain: the domain for which the DNS record should be edited
        :param record_id: the id of the DNS record which should be edited
        :param record_type: the new type of the DNS record;
                            supported DNS record types: A, AAAA, MX, CNAME, ALIAS, TXT, NS, SRV, TLSA, CAA
        :param content: the new content of the DNS record
        :param name: the new value of the subdomain for which the DNS record should apply; the * can be used for a
                     wildcard DNS record; if not set, the record will be set for the record domain
        :param ttl: the new time to live in seconds of the DNS record, have to be between 0 and 2147483647
        :param prio: the new priority of the DNS record

        :return: True if the editing was successful
        """

        assert domain is not None and len(domain) > 0
        assert record_id is not None and len(record_id) > 0
        assert record_type in SUPPORTED_DNS_RECORD_TYPES
        assert content is not None and len(content) > 0
        assert ttl is None or 300 <= ttl <= 2147483647

        url = urljoin(API_ENDPOINT, "dns/edit/{}/{}".format(domain, record_id))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key,
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
            raise Exception("ERROR: DNS edit api call was not successfully\n"
                            "Status code: {}\n"
                            "Message: {}".format(r.status_code, json.loads(r.text).get("message", "no message found")))

    def dns_delete(self,
                   domain: str,
                   record_id: str,
                   **kwargs) -> bool:
        """
        API DNS delete method: delete an existing DNS record specified by the id for a given domain
        see https://porkbun.com/api/json/v3/documentation#DNS%20Delete%20Record for more info

        :param domain: the domain for which the DNS record should be deleted
        :param record_id: the id of the DNS record which should be deleted

        :return: True if the deletion was successful
        """

        assert domain is not None and len(domain) > 0
        assert record_id is not None and len(record_id) > 0

        url = urljoin(API_ENDPOINT, "dns/delete/{}/{}".format(domain, record_id))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            raise Exception("ERROR: DNS delete api call was not successfully\n"
                            "Status code: {}\n"
                            "Message: {}".format(r.status_code, json.loads(r.text).get("message", "no message found")))

    def dns_retrieve(self, domain, **kwargs) -> list:
        """
        API DNS retrieve method: retrieve all DNS records for given domain
        see https://porkbun.com/api/json/v3/documentation#DNS%20Retrieve%20Records for more info

        :param domain: the domain for which the DNS records should be retrieved

        :return: list of DNS records as dicts

        The list structure will be:
        [
            {
                "id": "123456789",
                "name": "example.com",
                "type": "TXT",
                "content": "this is a nice text",
                "ttl": "300",
                "prio": None,
                "notes": ""
            },
            {
                "id": "234567890",
                "name": "example.com",
                "type": "A",
                "content": "0.0.0.0",
                "ttl": "300",
                "prio": 0,
                "notes": ""
            }
        ]
        """

        assert domain is not None and len(domain) > 0

        url = urljoin(API_ENDPOINT, "dns/retrieve/{}".format(domain))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return [parse_dns_record(record) for record in json.loads(r.text).get("records", [])]
        else:
            raise Exception("ERROR: DNS retrieve api call was not successfully\n"
                            "Status code: {}\n"
                            "Message: {}".format(r.status_code, json.loads(r.text).get("message", "no message found")))

    def dns_export(self, domain: str, filename: str, **kwargs) -> bool:
        """
        Export all DNS record from the given domain as json to a file.
        This method does not not represent a Porkbun API method.

        :param domain: the domain for which the DNS record should be retrieved and saved
        :param filename: the filename where to save the exported DNS records

        :return: True if everything went well
        """

        assert domain is not None and len(domain) > 0
        assert filename is not None and len(filename) > 0

        print("retrieve current DNS records...")
        dns_records = self.dns_retrieve(domain)

        print("save DNS records to {} ...".format(filename))
        # merge the single DNS records into one single dict with the record id as key
        dns_records_dict = dict()
        for record in dns_records:
            dns_records_dict[record["id"]] = record

        filepath = Path(filename)
        if filepath.exists():
            raise Exception("File already exists. Please try another filename")
        with open(filepath, "w") as f:
            json.dump(dns_records_dict, f)
        print("export finished")

        return True

    def dns_import(self, domain: str, filename: str, restore_mode: DNSRestoreMode, **kwargs) -> bool:
        """
        Restore
        This method does not not represent a Porkbun API method.

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
            print("restore mode: clear")

            try:
                # delete all existing DNS records
                for record in existing_dns_records:
                    self.dns_delete(domain, record["id"])

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
                print("something went wrong: {}".format(e.__str__()))
                self.__handle_error_backup__(existing_dns_records)
                print("import failed")
                return False
        elif restore_mode is DNSRestoreMode.replace:
            print("restore mode: replace")

            try:
                for existing_record in existing_dns_records:
                    record_id = existing_record["id"]
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
            print("restore mode: keep")

            existing_dns_records_dict = dict()
            for record in existing_dns_records:
                existing_dns_records_dict[record["id"]] = record

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

        print("import successfully completed")

        return True

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

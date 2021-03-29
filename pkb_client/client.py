import json
from typing import Optional
from urllib.parse import urljoin

import requests

API_ENDPOINT = "https://porkbun.com/api/json/v3/"
SUPPORTED_DNS_RECORD_TYPES = ["A", "AAAA", "MX", "CNAME", "ALIAS", "TXT", "NS", "SRV", "TLSA", "CAA"]


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
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

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
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

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
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

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
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

    def dns_retrieve(self, domain, **kwargs) -> list:
        """
        API DNS retrieve method: retrieve all DNS records for given domain
        see https://porkbun.com/api/json/v3/documentation#DNS%20Retrieve%20Records for more info

        :param domain: the domain for which the DNS records should be retrieved

        :return: list of DNS records as dicts
        """

        assert domain is not None and len(domain) > 0

        url = urljoin(API_ENDPOINT, "dns/retrieve/{}".format(domain))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("records", None)
        else:
            raise Exception("ERROR: DNS retrieve api call was not successfully\n"
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

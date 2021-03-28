import json
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

        :param api_key: the api key used for Porkbun API calls
        :param secret_api_key: the api secret used for Porkbun API calls
        """

        assert api_key is not None and len(api_key) > 0
        assert secret_api_key is not None and len(secret_api_key) > 0

        self.api_key = api_key
        self.secret_api_key = secret_api_key

    def ping(self, **kwargs) -> str:
        url = urljoin(API_ENDPOINT, "ping")
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("yourIp", None)
        else:
            raise Exception("ERROR: ping api call was not successfully\n"
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

    def dns_create(self, domain, record_type, content, name=None, ttl=300, prio=None, **kwargs):
        assert domain is not None and len(domain) > 0
        assert record_type in SUPPORTED_DNS_RECORD_TYPES
        assert content is not None and len(content) > 0
        assert ttl is None or 300 <= int(ttl) <= 2147483647

        url = urljoin(API_ENDPOINT, "dns/create/{}".format(domain))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key,
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": ttl,
            "prio": prio,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("id", None)
        else:
            raise Exception("ERROR: dns create api call was not successfully\n"
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

    def dns_edit(self, domain, record_id, record_type, content, name=None, ttl=300, prio=None, **kwargs) -> bool:
        assert domain is not None and len(domain) > 0
        assert record_id is not None and len(str(record_id)) > 0
        assert record_type in SUPPORTED_DNS_RECORD_TYPES
        assert content is not None and len(content) > 0
        assert ttl is None or 300 <= int(ttl) <= 2147483647

        url = urljoin(API_ENDPOINT, "dns/edit/{}/{}".format(domain, record_id))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key,
            "name": name,
            "type": record_type,
            "content": content,
            "ttl": ttl,
            "prio": prio,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            raise Exception("ERROR: dns edit api call was not successfully\n"
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

    def dns_delete(self, domain, record_id, **kwargs):
        assert domain is not None and len(domain) > 0
        assert record_id is not None and len(str(record_id)) > 0

        url = urljoin(API_ENDPOINT, "dns/delete/{}/{}".format(domain, record_id))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return True
        else:
            raise Exception("ERROR: dns delete api call was not successfully\n"
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

    def dns_retrieve(self, domain, **kwargs) -> dict:
        assert domain is not None and len(domain) > 0

        url = urljoin(API_ENDPOINT, "dns/retrieve/{}".format(domain))
        req_json = {
            "apikey": self.api_key,
            "secretapikey": self.secret_api_key,
        }
        r = requests.post(url=url, json=req_json)

        if r.status_code == 200:
            return json.loads(r.text).get("records", None)
        else:
            raise Exception("ERROR: dns retrieve api call was not successfully\n"
                            "Request status code: {}\n"
                            "Request response text: {}".format(r.status_code, r.text))

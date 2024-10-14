import unittest
from urllib.parse import urljoin

import responses
from responses import matchers
from responses.registries import OrderedRegistry

from pkb_client.client import PKBClient, PKBClientException, API_ENDPOINT
from pkb_client.client.dns import DNSRecord, DNSRecordType
from pkb_client.client.forwarding import URLForwarding, URLForwardingType


class TestClientAuth(unittest.TestCase):

    @responses.activate
    def test_valid_auth(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "ping"),
            json={"status": "SUCCESS", "yourIp": "127.0.0.1"},
            match=[matchers.json_params_matcher({"apikey": "key", "secretapikey": "secret"})],
        )

        ip_address = pkb_client.ping()
        self.assertEqual("127.0.0.1", ip_address)

    @responses.activate
    def test_invalid_auth(self):
        pkb_client = PKBClient("key" + "s", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "ping"),
            json={"status": "ERROR", "message": "Invalid credentials"},
            status=401,
        )
        with self.assertRaises(PKBClientException):
            pkb_client.ping()

    @responses.activate
    def test_ping(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "ping"),
            json={"status": "SUCCESS", "yourIp": "127.0.0.1"},
            match=[matchers.json_params_matcher({"apikey": "key", "secretapikey": "secret"})],
        )
        ip_address = pkb_client.ping()
        self.assertEqual("127.0.0.1", ip_address)

    @responses.activate(registry=OrderedRegistry)
    def test_dns_create(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "dns/create/example.com"),
            json={
                "status": "SUCCESS",
                "id": "123456"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret", "name": "sub.example.com", "type": "A",
                 "content": "127.0.0.1", "ttl": 3600, "prio": None})],
        )
        assert "123456" == pkb_client.dns_create("example.com", DNSRecordType.A, "127.0.0.1", "sub.example.com", 3600)

        responses.post(
            url=urljoin(API_ENDPOINT, "dns/create/example.com"),
            json={
                "status": "SUCCESS",
                "id": "234561"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret", "name": "sub.example.com", "type": "MX",
                 "content": "127.0.0.1", "ttl": 3600, "prio": 2})],
        )
        assert "234561" == pkb_client.dns_create("example.com", DNSRecordType.MX, "127.0.0.1", "sub.example.com", 3600,
                                                 2)

    def test_dns_create_invalid_prio_record_type(self):
        pkb_client = PKBClient("key", "secret")
        with self.assertRaises(ValueError):
            pkb_client.dns_create("example.com", DNSRecordType.A, "127.0.0.1", "sub.example.com", 3600, 2)

    @responses.activate(registry=OrderedRegistry)
    def test_dns_edit(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "dns/edit/example.com/123456"),
            json={
                "status": "SUCCESS"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret", "type": "A", "content": "127.0.0.1",
                 "name": "sub.example.com", "ttl": 3600, "prio": None})],
        )

        success = pkb_client.dns_edit("example.com", "123456", DNSRecordType.A, "127.0.0.1", "sub.example.com", 3600)
        self.assertTrue(success)

        responses.post(
            url=urljoin(API_ENDPOINT, "dns/edit/example.com/123456"),
            json={
                "status": "SUCCESS"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret", "type": "MX", "content": "127.0.0.1",
                 "name": "sub.example.com", "ttl": 3600, "prio": 2})],
        )

        success = pkb_client.dns_edit("example.com", "123456", DNSRecordType.MX, "127.0.0.1", "sub.example.com", 3600,
                                      2)
        self.assertTrue(success)

    def test_dns_edit_invalid_prio_record_type(self):
        pkb_client = PKBClient("key", "secret")
        with self.assertRaises(ValueError):
            pkb_client.dns_edit("example.com", "123456", DNSRecordType.A, "127.0.0.1", "sub.example.com", 3600, 2)

    @responses.activate
    def test_dns_edit_all(self):
        pkb_client = PKBClient("key", "secret")

    @responses.activate
    def test_dns_delete(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "dns/delete/example.com/123456"),
            json={
                "status": "SUCCESS"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret"})],
        )

        success = pkb_client.dns_delete("example.com", "123456")

        self.assertTrue(success)

    @responses.activate
    def test_dns_retrieve(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "dns/retrieve/example.com"),
            json={
                "status": "SUCCESS",
                "records": [
                    {
                        "id": "123456",
                        "name": "example.com",
                        "type": "A",
                        "content": "127.0.0.1",
                        "ttl": "600",
                        "prio": None,
                        "notes": ""
                    },
                    {
                        "id": "1234567",
                        "name": "sub.example.com",
                        "type": "A",
                        "content": "127.0.0.2",
                        "ttl": 600,
                        "prio": None,
                        "notes": ""
                    }
                ]
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret"})],
        )
        records = pkb_client.dns_retrieve("example.com")

        expected_records = [
            DNSRecord("123456", "example.com", DNSRecordType.A, "127.0.0.1", 600, None, ""),
            DNSRecord("1234567", "sub.example.com", DNSRecordType.A, "127.0.0.2", 600, None, "")
        ]
        self.assertEqual(expected_records, records)

    @responses.activate
    def test_set_dns_servers(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "domain/updateNs/example.com"),
            json={
                "status": "SUCCESS"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret",
                 "ns": ["ns1.example.com", "ns2.example.com"]})],
        )

        success = pkb_client.update_dns_servers("example.com", ["ns1.example.com", "ns2.example.com"])

        self.assertTrue(success)

    @responses.activate
    def test_get_url_forward(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "domain/getUrlForwarding/example.com"),
            json={
                "status": "SUCCESS",
                "forwards": [
                    {
                        "id": "123456",
                        "subdomain": "",
                        "location": "https://example.com",
                        "type": "temporary",
                        "includePath": "no",
                        "wildcard": "yes"
                    },
                    {
                        "id": "234567",
                        "subdomain": "sub1",
                        "location": "https://sub1.example.com",
                        "type": "permanent",
                        "includePath": "no",
                        "wildcard": "yes"
                    }
                ]
            }
        )

        forwards = pkb_client.get_url_forward("example.com")

        expected_forwards = [
            URLForwarding("123456", "", "https://example.com", URLForwardingType.temporary, False, True),
            URLForwarding("234567", "sub1", "https://sub1.example.com", URLForwardingType.permanent, False, True)
        ]

        self.assertEqual(expected_forwards, forwards)

    @responses.activate
    def test_add_url_forward(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "domain/addUrlForward/example.com"),
            json={
                "status": "SUCCESS"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret",
                 "subdomain": "sub.example.com", "location": "https://www.example.com",
                 "type": "permanent", "includePath": False, "wildcard": False})]
        )

        success = pkb_client.add_url_forward("example.com",
                                             "sub.example.com",
                                             "https://www.example.com",
                                             URLForwardingType.permanent,
                                             False,
                                             False)

        self.assertTrue(success)

    @responses.activate
    def test_delete_url_forwarding(self):
        pkb_client = PKBClient("key", "secret")

        responses.post(
            url=urljoin(API_ENDPOINT, "domain/deleteUrlForward/example.com/123456"),
            json={
                "status": "SUCCESS"
            },
            match=[matchers.json_params_matcher(
                {"apikey": "key", "secretapikey": "secret"})]
        )
        success = pkb_client.delete_url_forward("example.com",
                                                "123456")

        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()

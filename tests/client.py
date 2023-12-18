import json
import unittest
from http.server import HTTPServer
from importlib import resources
from threading import Thread

from pkb_client.client import PKBClient, PKBClientException
from pkb_client.dns import DNSRecord, DNSRecordType
from pkb_client.forwarding import URLForwarding, URLForwardingType
from tests import responses
from tests.handler import RequestHandler

BASE_URL = "http://localhost:8000/api/json/v3/"

YOUR_IP = "172.0.0.1"
KEY = "key"
SECRET = "secret"


class TestClientAuth(unittest.TestCase):
    server = None

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("localhost", 8000), RequestHandler)
        server_thread = Thread(target=cls.server.serve_forever)
        # daemon threads exit when the main thread exits
        server_thread.daemon = True
        server_thread.start()

    def test_valid_auth(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        ip_address = pkb_client.ping()

        self.assertEqual(YOUR_IP, ip_address)

    def test_invalid_auth(self):
        pkb_client = PKBClient(KEY + "s", SECRET, BASE_URL)

        with self.assertRaises(PKBClientException):
            pkb_client.ping()

    def test_ping(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        ip_address = pkb_client.ping()

        self.assertEqual(YOUR_IP, ip_address)

    def test_dns_create(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        dns_id = pkb_client.dns_create("example.com", DNSRecordType.A, "172.0.0.1", "sub.example.com", 3600, 2)

        self.assertEqual("123456", dns_id)

    def test_dns_edit(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        success = pkb_client.dns_edit("example.com", "123456", DNSRecordType.A, "172.0.0.1", "sub.example.com", 3600, 2)

        self.assertTrue(success)

    def test_dns_delete(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        success = pkb_client.dns_delete("example.com", "123456")

        self.assertTrue(success)

    def test_dns_retrieve(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        success = pkb_client.dns_retrieve("example.com")

        with resources.open_text(responses, "dns_retrieve.json") as f:
            response = json.load(f)
        records = [DNSRecord.from_dict(d) for d in response["records"]]

        self.assertEqual(records, success)

    def test_set_dns_servers(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        success = pkb_client.update_dns_servers("example.com", ["ns1.example.com", "ns2.example.com"])

        self.assertTrue(success)

    def test_get_url_forward(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        forwardings = pkb_client.get_url_forward("example.com")

        with resources.open_text(responses, "domain_getUrlForwarding.json") as f:
            response = json.load(f)
        expected_forwards = [URLForwarding.from_dict(d) for d in response["forwards"]]

        self.assertEqual(forwardings, expected_forwards)

    def test_add_url_forward(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        success = pkb_client.add_url_forward("example.com",
                                             "sub.example.com",
                                             "https://www.example.com",
                                             URLForwardingType.permanent,
                                             False,
                                             False)

        self.assertTrue(success)

    def test_delete_url_forwarding(self):
        pkb_client = PKBClient(KEY, SECRET, BASE_URL)
        success = pkb_client.delete_url_forward("example.com",
                                                "123456")

        self.assertTrue(success)

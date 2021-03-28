import os
import unittest

import requests

from pkb_client.client import PKBClient

"""
WARNING: DO NOT RUN THIS TEST WITH A PRODUCTION DOMAIN OR IN A PRODUCTION ENVIRONMENT!!
         This test sets, edits and deletes dns record entries and if the test fails,
         unintended changes to dns entries may result.
"""

TEST_DOMAIN = os.environ.get("TEST_DOMAIN")
PORKBUN_API_KEY = os.environ.get("PORKBUN_API_KEY")
PORKBUN_API_SECRET = os.environ.get("PORKBUN_API_SECRET")
DNS_RECORDS = os.environ.get("DNS_RECORDS")

PUBLIC_IP_URL = "https://api64.ipify.org"


class DNSTestWithCleanup(unittest.TestCase):

    def tearDown(self):
        if hasattr(self, "record_id") and self.record_id is not None:
            pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
            try:
                pkb_client.dns_delete(TEST_DOMAIN, self.record_id)
            except:
                pass


class TestClientAuth(unittest.TestCase):
    def test_valid_auth(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        ip_address = pkb_client.ping()

        self.assertEqual(ip_address, requests.get(PUBLIC_IP_URL).text)

    def test_invalid_api_key(self):
        pkb_client = PKBClient("invalid-api-key", PORKBUN_API_SECRET)
        with self.assertRaises(Exception):
            pkb_client.ping()

    def test_invalid_api_secret(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, "invalid-api-secret")
        with self.assertRaises(Exception):
            pkb_client.ping()

    def test_invalid_api_key_and_secret(self):
        pkb_client = PKBClient("invalid-api-key", "invalid-api-secret")
        with self.assertRaises(Exception):
            pkb_client.ping()


class TestPingMethod(unittest.TestCase):
    def test_ping(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        ip_address = pkb_client.ping()

        self.assertEqual(ip_address, requests.get(PUBLIC_IP_URL).text)


class TestDNSCreateMethod(DNSTestWithCleanup):

    def test_valid_request(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        ttl = "342"
        name = "test_pkb_client"

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name, ttl=ttl)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == str(self.record_id):
                with self.subTest():
                    self.assertEqual(txt_content, record["content"])
                with self.subTest():
                    self.assertEqual(ttl, record["ttl"])
                with self.subTest():
                    self.assertEqual("{}.{}".format(name, TEST_DOMAIN), record["name"])
                return
        self.assertTrue(False)

    def test_invalid_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        with self.assertRaises(Exception):
            self.record_id = pkb_client.dns_create("notvaliddomain", "TXT", "interesting-content",
                                                   name="test_pkb_client")

    def test_invalid_record_type(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        with self.assertRaises(AssertionError):
            self.record_id = pkb_client.dns_create(TEST_DOMAIN, "ABC", "interesting-content", name="test_pkb_client")

    def test_larger_than_allowed_content_length(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        txt_content = "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-cont"
        assert len(txt_content) == 256

        with self.assertRaises(Exception):
            self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client")

    def test_largest_allowed_content_length(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        txt_content = "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-con"
        assert len(txt_content) == 255

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client")
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == str(self.record_id):
                self.assertEqual(txt_content, record["content"])
                return
        self.assertTrue(False)

    def test_empty_content_str(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        txt_content = "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-con"
        assert len(txt_content) == 255

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client")
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == str(self.record_id):
                self.assertEqual(txt_content, record["content"])
                return
        self.assertTrue(False)

    def test_none_content(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", None, name="test_pkb_client")

    def test_smaller_than_allowed_ttl(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", "interesting-content", ttl=299,
                                                   name="test_pkb_client")

    def test_negative_ttl(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", "interesting-content", ttl=-1,
                                                   name="test_pkb_client")

    def test_larger_than_allowed_ttl(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", "interesting-content", name="test_pkb_client",
                                                   ttl=2147483648)

    def test_largest_allowed_ttl(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client", ttl=2147483647)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == str(self.record_id):
                self.assertEqual(txt_content, record["content"])
                return
        self.assertTrue(False)

    def test_smaller_than_allowed_prio_with_txt(self):
        # if we sent the prio with an unsupported dns record type, the prio should be ignored
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        prio = 10

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client", prio=prio)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == str(self.record_id):
                with self.subTest():
                    self.assertEqual(txt_content, record["content"])
                with self.subTest():
                    self.assertEqual(record["content"], 0)
                return
        self.assertTrue(False)

    def test_negative_prio_with_txt(self):
        # if we sent the prio with an unsupported dns record type, the prio should be ignored (set to 0)
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        prio = -42

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client", prio=prio)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == str(self.record_id):
                with self.subTest():
                    self.assertEqual(txt_content, record["content"])
                with self.subTest():
                    self.assertEqual(0, record["prio"])
                return
        self.assertTrue(False)


class TestDNSEditMethod(DNSTestWithCleanup):
    def test_valid_edit_request(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        name = "test_pkb_client"
        tll = "342"
        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name, ttl=tll)

        edited_txt_content = "more-interesting-content"
        edited_name = "more_test_pkb_client"
        edited_tll = "423"
        pkb_client.dns_edit(TEST_DOMAIN, self.record_id, "TXT", edited_txt_content, name=edited_name, ttl=edited_tll)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == str(self.record_id):
                with self.subTest("txt record content is not edited"):
                    self.assertEqual(edited_txt_content, record["content"])
                with self.subTest("txt record name is not edited"):
                    self.assertEqual("{}.{}".format(edited_name, TEST_DOMAIN), record["name"])
                with self.subTest("txt record ttl is not edited"):
                    self.assertEqual(edited_tll, record["ttl"])
                return
        self.assertTrue(False)


class TestDNSDeleteMethod(DNSTestWithCleanup):
    def test_valid_delete_request(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        name = "test_pkb_client"
        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        record_exists = False
        for record in records:
            if record["id"] == str(self.record_id):
                record_exists = True
                break
        with self.subTest("test txt record setup failed"):
            self.assertTrue(record_exists)

        pkb_client.dns_delete(TEST_DOMAIN, self.record_id)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        record_exists = False
        for record in records:
            if record["id"] == str(self.record_id):
                record_exists = True
                break
        if not record_exists:
            self.record_id = None
        with self.subTest("txt record is not deleted"):
            self.assertFalse(record_exists)


class TestDNSReceiveMethod(unittest.TestCase):
    def test_valid_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        self.assertEqual(records, DNS_RECORDS)

    def test_invalid_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        with self.assertRaises(Exception):
            pkb_client.dns_retrieve("invaliddomain")


if __name__ == '__main__':
    unittest.main()

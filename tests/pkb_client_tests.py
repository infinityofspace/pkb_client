import json
import os
import unittest
from pathlib import Path

import requests

from pkb_client.client import PKBClient, DNSRestoreMode

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
            pkb_client.dns_delete(TEST_DOMAIN, self.record_id)


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
        ttl = 342
        name = "test_pkb_client"

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name, ttl=ttl)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)

        for record in records:
            if record["id"] == self.record_id:
                with self.subTest():
                    self.assertEqual(txt_content, record["content"])
                with self.subTest():
                    self.assertEqual(ttl, int(record["ttl"]))
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
        # the api call should not fail because the api creates multiple TXT entries which will be concatenated
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        txt_content = "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content-interesting-content-interesting-content-interesting-content-" \
                      "interesting-content"
        assert len(txt_content) == 259

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client")
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                self.assertEqual(txt_content, record["content"])
                return
        self.assertTrue(False)

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
            if record["id"] == self.record_id:
                self.assertEqual(txt_content, record["content"])
                return
        self.assertTrue(False)

    def test_empty_content_str(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)
        txt_content = ""
        assert len(txt_content) == 0

        with self.assertRaises(AssertionError):
            self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client")

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
        ttl = 2147483647

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client", ttl=ttl)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                with self.subTest():
                    self.assertEqual(txt_content, record["content"])
                with self.subTest():
                    self.assertEqual(ttl, int(record["ttl"]))
                return
        self.assertTrue(False)

    def test_valid_prio_with_txt(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        prio = 10

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client", prio=prio)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                with self.subTest():
                    self.assertEqual(txt_content, record["content"])
                with self.subTest():
                    self.assertEqual(prio, int(record["prio"]))
                return
        self.assertTrue(False)

    def test_negative_prio_with_txt(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        prio = -42

        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name="test_pkb_client", prio=prio)
        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                with self.subTest():
                    self.assertEqual(txt_content, record["content"])
                with self.subTest():
                    self.assertEqual(prio, int(record["prio"]))
                return
        self.assertTrue(False)


class TestDNSEditMethod(DNSTestWithCleanup):
    def test_valid_edit_request(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        name = "test_pkb_client"
        tll = 342
        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name, ttl=tll)

        edited_txt_content = "more-interesting-content"
        edited_name = "more_test_pkb_client"
        edited_tll = 423
        pkb_client.dns_edit(TEST_DOMAIN, self.record_id, "TXT", edited_txt_content, name=edited_name, ttl=edited_tll)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                with self.subTest("txt record content is not edited"):
                    self.assertEqual(edited_txt_content, record["content"])
                with self.subTest("txt record name is not edited"):
                    self.assertEqual("{}.{}".format(edited_name, TEST_DOMAIN), record["name"])
                with self.subTest("txt record ttl is not edited"):
                    self.assertEqual(edited_tll, int(record["ttl"]))
                return
        self.assertTrue(False)

    def test_change_subdomain_to_root_txt_record(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        name = "test_pkb_client"
        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name)

        edited_txt_content = "more-interesting-content"
        edited_name = ""
        pkb_client.dns_edit(TEST_DOMAIN, self.record_id, "TXT", edited_txt_content, name=edited_name)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                with self.subTest("txt record content is not edited"):
                    self.assertEqual(edited_txt_content, record["content"])
                with self.subTest("txt record name is not edited"):
                    self.assertEqual(TEST_DOMAIN, record["name"])
                return
        self.assertTrue(False)

    def test_no_name_change(self):
        # the name is required for each edit, otherwise the record will apply for the root domain
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        name = "test_pkb_client"
        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name)

        edited_txt_content = "more-interesting-content"
        pkb_client.dns_edit(TEST_DOMAIN, self.record_id, "TXT", edited_txt_content)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                with self.subTest("txt record content is not edited"):
                    self.assertEqual(edited_txt_content, record["content"])
                with self.subTest("txt record name is not edited"):
                    self.assertEqual(TEST_DOMAIN, record["name"])
                return
        self.assertTrue(False)

    def test_record_type_change(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        txt_content = "interesting-content"
        name = "test_pkb_client"
        self.record_id = pkb_client.dns_create(TEST_DOMAIN, "TXT", txt_content, name=name)

        edited_txt_content = "more-interesting-content"
        name = "test_pkb_client"
        edited_record_type = "MX"
        pkb_client.dns_edit(TEST_DOMAIN, self.record_id, edited_record_type, edited_txt_content, name=name)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in records:
            if record["id"] == self.record_id:
                with self.subTest("txt record content is not edited"):
                    self.assertEqual(edited_txt_content, record["content"])
                with self.subTest("record type is not edited"):
                    self.assertEqual(edited_record_type, record["type"])
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
            if record["id"] == self.record_id:
                record_exists = True
                break
        with self.subTest("test txt record setup failed"):
            self.assertTrue(record_exists)

        pkb_client.dns_delete(TEST_DOMAIN, self.record_id)

        records = pkb_client.dns_retrieve(TEST_DOMAIN)
        record_exists = False
        for record in records:
            if record["id"] == self.record_id:
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


class TestDNSExport(unittest.TestCase):
    def test_valid_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        dns_records = pkb_client.dns_retrieve(domain=TEST_DOMAIN)
        # reformat the dns records to a single dict
        dns_records_dict = dict()
        for record in dns_records:
            dns_records_dict[record["id"]] = record

        filepath = Path("dns_backup.json")
        if filepath.exists():
            filepath.unlink()
        pkb_client.dns_export(domain=TEST_DOMAIN, filename=str(filepath))

        with open(str("dns_backup.json"), "r") as f:
            self.assertEqual(json.load(f), dns_records_dict)

        filepath.unlink()

    def test_invalid_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(Exception):
            pkb_client.dns_export(domain="invaliddomain", filename="dns_backup.json")

    def test_empty_str_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_export(domain="", filename="dns_backup.json")

    def test_none_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_export(domain=None, filename="dns_backup.json")

    def test_filename_already_exists(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        filepath = Path("dns_backup.json")
        filepath.touch()

        with self.assertRaises(Exception):
            pkb_client.dns_export(domain=TEST_DOMAIN, filename=str(filepath))

        filepath.unlink()

    def test_empty_str_filename(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_export(domain=TEST_DOMAIN, filename="")

    def test_none_filename(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_export(domain=TEST_DOMAIN, filename=None)


class TestDNSImport(unittest.TestCase):
    def test_valid_clear_import(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        existing_dns_record_ids = set()
        dns_records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in dns_records:
            existing_dns_record_ids.add(record["id"])

        filename = "dns_backup_clear.json"

        with open(filename, "r") as f:
            file_dns_records = json.load(f)

        pkb_client.dns_import(domain=TEST_DOMAIN, filename=filename, restore_mode=DNSRestoreMode.clear)

        new_dns_records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for new_record in new_dns_records:
            # test if the previous dns records still exists
            if new_record["id"] in existing_dns_record_ids:
                self.assertTrue(False)
            # test if the new dns record was created
            new_record_created = False
            for _, file_dns_record in file_dns_records.items():
                if file_dns_record["name"] == new_record["name"] \
                        and file_dns_record["type"] == new_record["type"] \
                        and file_dns_record["content"] == new_record["content"] \
                        and file_dns_record["ttl"] == new_record["ttl"] \
                        and file_dns_record["prio"] == new_record["prio"]:
                    new_record_created = True
            self.assertTrue(new_record_created)

    def test_valid_replace_import(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        existing_dns_record_ids = set()
        dns_records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in dns_records:
            existing_dns_record_ids.add(record["id"])

        filename = "dns_backup_replace.json"

        with open(filename, "r") as f:
            file_dns_records = json.load(f)

        pkb_client.dns_import(domain=TEST_DOMAIN, filename=filename, restore_mode=DNSRestoreMode.replace)

        new_dns_records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for new_record in new_dns_records:
            # test if the previous dns records still exists
            if new_record["id"] not in existing_dns_record_ids:
                self.assertTrue(False)
            # test if the dns record was edited
            record_edited = False
            for _, file_dns_record in file_dns_records.items():
                if file_dns_record["name"] == new_record["name"] \
                        and file_dns_record["type"] == new_record["type"] \
                        and file_dns_record["content"] == new_record["content"] \
                        and file_dns_record["ttl"] == new_record["ttl"] \
                        and file_dns_record["prio"] == new_record["prio"]:
                    record_edited = True
                    break
            self.assertTrue(record_edited)

    def test_valid_keep_import(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        existing_dns_records = dict()
        dns_records = pkb_client.dns_retrieve(TEST_DOMAIN)
        for record in dns_records:
            existing_dns_records[record["id"]] = record

        filename = "dns_backup_keep.json"

        with open(filename, "r") as f:
            file_dns_records = json.load(f)

        pkb_client.dns_import(domain=TEST_DOMAIN, filename=filename, restore_mode=DNSRestoreMode.keep)

        new_dns_records = pkb_client.dns_retrieve(TEST_DOMAIN)

        # test if the all old dns records are kept
        for _, existing_record in existing_dns_records.items():
            record_kept = False
            for new_record in new_dns_records:
                if existing_record["id"] == new_record["id"] \
                        and existing_record["name"] == new_record["name"] \
                        and existing_record["type"] == new_record["type"] \
                        and existing_record["content"] == new_record["content"] \
                        and existing_record["ttl"] == new_record["ttl"] \
                        and existing_record["prio"] == new_record["prio"]:
                    record_kept = True
                    break
            with self.subTest():
                self.assertTrue(record_kept)

        # test if the new records are created
        for new_record in new_dns_records:
            if new_record["id"] not in existing_dns_records:
                record_created = False
                for _, file_dns_record in file_dns_records.items():
                    if file_dns_record["name"] == new_record["name"] \
                            and file_dns_record["type"] == new_record["type"] \
                            and file_dns_record["content"] == new_record["content"] \
                            and file_dns_record["ttl"] == new_record["ttl"] \
                            and file_dns_record["prio"] == new_record["prio"]:
                        record_created = True
                        break
                with self.subTest():
                    self.assertTrue(record_created)

    def test_invalid_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(Exception):
            pkb_client.dns_import(domain="invaliddomain", filename="dns_backup.json", restore_mode=DNSRestoreMode.clear)

    def test_empty_str_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_import(domain="", filename="dns_backup.json", restore_mode=DNSRestoreMode.clear)

    def test_none_domain(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_import(domain=None, filename="dns_backup.json", restore_mode=DNSRestoreMode.clear)

    def test_empty_str_filename(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_import(domain=TEST_DOMAIN, filename="", restore_mode=DNSRestoreMode.clear)

    def test_none_filename(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.assertRaises(AssertionError):
            pkb_client.dns_import(domain=TEST_DOMAIN, filename=None, restore_mode=DNSRestoreMode.clear)

    def test_invalid_restore_mode(self):
        pkb_client = PKBClient(PORKBUN_API_KEY, PORKBUN_API_SECRET)

        with self.subTest("None as restore mode"):
            with self.assertRaises(AssertionError):
                pkb_client.dns_import(domain=TEST_DOMAIN, filename="dns_backup.json", restore_mode=None)
        with self.subTest("empty string as restore mode"):
            with self.assertRaises(AssertionError):
                pkb_client.dns_import(domain=TEST_DOMAIN, filename="dns_backup.json", restore_mode="")
        with self.subTest("number as restore mode"):
            with self.assertRaises(AssertionError):
                pkb_client.dns_import(domain=TEST_DOMAIN, filename="dns_backup.json", restore_mode=0)


if __name__ == '__main__':
    unittest.main()

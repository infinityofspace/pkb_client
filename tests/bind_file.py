import tempfile
import unittest
from importlib import resources

from pkb_client.client.bind_file import BindFile, BindRecord, RecordClass
from pkb_client.client.dns import DNSRecordType
from tests import data


class TestBindFileParsing(unittest.TestCase):
    def test_reading_bind_file(self):
        with self.subTest("With default TTL"):
            with resources.open_text(data, "test.bind") as f:
                bind_file = BindFile.from_file(f.name)

            self.assertEqual("test.com.", bind_file.origin)
            self.assertEqual(1234, bind_file.ttl)
            self.assertEqual(7, len(bind_file.records))
            self.assertEqual(
                BindRecord(
                    "test.com.", 600, RecordClass.IN, DNSRecordType.A, "1.2.3.4"
                ),
                bind_file.records[0],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.",
                    600,
                    RecordClass.IN,
                    DNSRecordType.A,
                    "1.2.3.5",
                    comment="This is a comment",
                ),
                bind_file.records[1],
            )
            self.assertEqual(
                BindRecord(
                    "sub.test.com.", 600, RecordClass.IN, DNSRecordType.A, "4.3.2.1"
                ),
                bind_file.records[2],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.",
                    600,
                    RecordClass.IN,
                    DNSRecordType.AAAA,
                    "2001:db8::1",
                    comment="This is a comment",
                ),
                bind_file.records[3],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.", 1234, RecordClass.IN, DNSRecordType.TXT, "pkb-client"
                ),
                bind_file.records[4],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.",
                    600,
                    RecordClass.IN,
                    DNSRecordType.MX,
                    "mail.test.com.",
                    prio=10,
                ),
                bind_file.records[5],
            )

        with self.subTest("Without default TTL"):
            with resources.open_text(data, "test_no_ttl.bind") as f:
                bind_file = BindFile.from_file(f.name)

            self.assertEqual("test.com.", bind_file.origin)
            self.assertEqual(None, bind_file.ttl)
            self.assertEqual(7, len(bind_file.records))
            self.assertEqual(
                BindRecord(
                    "test.com.", 600, RecordClass.IN, DNSRecordType.A, "1.2.3.4"
                ),
                bind_file.records[0],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.",
                    600,
                    RecordClass.IN,
                    DNSRecordType.A,
                    "1.2.3.5",
                    comment="This is a comment",
                ),
                bind_file.records[1],
            )
            self.assertEqual(
                BindRecord(
                    "sub.test.com.", 600, RecordClass.IN, DNSRecordType.A, "4.3.2.1"
                ),
                bind_file.records[2],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.",
                    700,
                    RecordClass.IN,
                    DNSRecordType.AAAA,
                    "2001:db8::1",
                    comment="This is a comment",
                ),
                bind_file.records[3],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.", 700, RecordClass.IN, DNSRecordType.TXT, "pkb-client"
                ),
                bind_file.records[4],
            )
            self.assertEqual(
                BindRecord(
                    "test.com.",
                    600,
                    RecordClass.IN,
                    DNSRecordType.MX,
                    "mail.test.com.",
                    prio=10,
                ),
                bind_file.records[5],
            )

    def test_writing_bind_file(self):
        records = [
            BindRecord("test.com.", 600, RecordClass.IN, DNSRecordType.A, "1.2.3.4"),
            BindRecord(
                "sub.test.com.", 700, RecordClass.IN, DNSRecordType.A, "4.3.2.1"
            ),
            BindRecord(
                "test.com.", 600, RecordClass.IN, DNSRecordType.AAAA, "2001:db8::1"
            ),
            BindRecord(
                "test.com.", 600, RecordClass.IN, DNSRecordType.TXT, "pkb-client"
            ),
            BindRecord(
                "test.com.",
                600,
                RecordClass.IN,
                DNSRecordType.MX,
                "mail.test.com.",
                prio=10,
            ),
        ]
        bind_file = BindFile("test.com.", 1234, records)

        file_content = (
            "$ORIGIN test.com.\n"
            "$TTL 1234\n"
            'test.com. 600 IN A "1.2.3.4"\n'
            'sub.test.com. 700 IN A "4.3.2.1"\n'
            'test.com. 600 IN AAAA "2001:db8::1"\n'
            'test.com. 600 IN TXT "pkb-client"\n'
            'test.com. 600 IN MX 10 "mail.test.com."\n'
        )

        with tempfile.NamedTemporaryFile() as f:
            bind_file.to_file(f.name)
            with open(f.name) as f2:
                self.assertEqual(file_content.strip(), f2.read().strip())


if __name__ == "__main__":
    unittest.main()

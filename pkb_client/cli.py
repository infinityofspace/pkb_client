import argparse
import pprint
import textwrap

from pkb_client.client import PKBClient, SUPPORTED_DNS_RECORD_TYPES, DNSRestoreMode


def main():
    parser = argparse.ArgumentParser(
        description="Unofficial client for the Porkbun API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
                                    License:
                                    MIT - Copyright (c) Marvin Heptner

                                    Copyright notices:
                                        requests:
                                            Project: https://github.com/psf/requests
                                            License: Apache-2.0 https://github.com/psf/requests/blob/master/LICENSE
                                        setuptools:
                                            Project: https://github.com/pypa/setuptools
                                            License: MIT https://raw.githubusercontent.com/pypa/setuptools/main/LICENSE                                            
                                    """)
    )

    parser.add_argument("-k", "--key", help="The API key used for Porkbun API calls (usually starts with \"pk\").")
    parser.add_argument("-s", "--secret",
                        help="The API secret used for Porkbun API calls (usually starts with \"sk\").")

    subparsers = parser.add_subparsers(help="Supported API methods")

    parser_ping = subparsers.add_parser("ping", help="Ping the API Endpoint")
    parser_ping.set_defaults(func=PKBClient.ping)

    parser_dns_create = subparsers.add_parser("dns-create", help="Create a new DNS record.")
    parser_dns_create.set_defaults(func=PKBClient.dns_create)
    parser_dns_create.add_argument("domain", help="The domain for which the new DNS record should be created.")
    parser_dns_create.add_argument("record_type", help="The type of the new DNS record.",
                                   choices=SUPPORTED_DNS_RECORD_TYPES)
    parser_dns_create.add_argument("content", help="The content of the new DNS record.")
    parser_dns_create.add_argument("--name",
                                   help="The subdomain for which the new DNS record should be created."
                                        "The * can be used for a wildcard DNS record."
                                        "If not used, then a DNS record for the root domain will be created",
                                   required=False)
    parser_dns_create.add_argument("--ttl", type=int, help="The ttl of the new DNS record.", required=False)
    parser_dns_create.add_argument("--prio", type=int, help="The priority of the new DNS record.", required=False)

    parser_dns_edit = subparsers.add_parser("dns-edit", help="Edit an existing DNS record.")
    parser_dns_edit.set_defaults(func=PKBClient.dns_edit)
    parser_dns_edit.add_argument("domain", help="The domain for which the DNS record should be edited.")
    parser_dns_edit.add_argument("record_id", help="The id of the DNS record which should be edited.")
    parser_dns_edit.add_argument("record_type", help="The new type of the DNS record.",
                                 choices=SUPPORTED_DNS_RECORD_TYPES)
    parser_dns_edit.add_argument("content", help="The new content of the DNS record.")
    parser_dns_edit.add_argument("--name",
                                 help="The new value of the subdomain for which the DNS record should apply. "
                                      "The * can be used for a wildcard DNS record. If not set, the record will "
                                      "be set for the root domain.",
                                 required=False)
    parser_dns_edit.add_argument("--ttl", type=int, help="The new ttl of the DNS record.", required=False)
    parser_dns_edit.add_argument("--prio", type=int, help="The new priority of the DNS record.", required=False)

    parser_dns_delete = subparsers.add_parser("dns-delete", help="Delete an existing DNS record.")
    parser_dns_delete.set_defaults(func=PKBClient.dns_delete)
    parser_dns_delete.add_argument("domain", help="The domain for which the DNS record should be deleted.")
    parser_dns_delete.add_argument("record_id", help="The id of the DNS record which should be deleted.")

    parser_dns_receive = subparsers.add_parser("dns-retrieve", help="Get all DNS records.")
    parser_dns_receive.set_defaults(func=PKBClient.dns_retrieve)
    parser_dns_receive.add_argument("domain", help="The domain for which the DNS record should be retrieved.")

    parser_dns_export = subparsers.add_parser("dns-export", help="Save all DNS records to a local file as json.")
    parser_dns_export.set_defaults(func=PKBClient.dns_export)
    parser_dns_export.add_argument("domain",
                                   help="The domain for which the DNS record should be retrieved and saved.")
    parser_dns_export.add_argument("filename", help="The filename where to save the exported DNS records.")

    parser_dns_import = subparsers.add_parser("dns-import", help="Restore all DNS records from a local file.",
                                              formatter_class=argparse.RawTextHelpFormatter)
    parser_dns_import.set_defaults(func=PKBClient.dns_import)
    parser_dns_import.add_argument("domain", help="The domain for which the DNS record should be restored.")
    parser_dns_import.add_argument("filename", help="The filename from which the DNS records are to be restored.")
    parser_dns_import.add_argument("restore_mode", help="""The restore mode (DNS records are identified by the record id):
    clean: remove all existing DNS records and restore all DNS records from the provided file
    replace: replace only existing DNS records with the DNS records from the provided file, but do not create any new DNS records
    keep: keep the existing DNS records and only create new ones for all DNS records from the specified file if they do not exist
    """, type=DNSRestoreMode.from_string, choices=list(DNSRestoreMode))

    args = parser.parse_args()

    if not hasattr(args, "func"):
        raise argparse.ArgumentError(None, "No method specified. Please provide a method and try again.")

    if args.key is None:
        while True:
            api_key = input("Please enter your API key you got from Porkbun (usually starts with \"pk\"): ")
            if len(api_key) == 0:
                print("The api key can not be empty.")
            else:
                break
    else:
        api_key = args.key

    if args.secret is None:
        while True:
            api_secret = input("Please enter your API key secret you got from Porkbun (usually starts with \"sk\"): ")
            if len(api_secret) == 0:
                print("The api key secret can not be empty.")
            else:
                break
    else:
        api_secret = args.secret

    pkb_client = PKBClient(api_key, api_secret)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(args.func(pkb_client, **vars(args)))


if __name__ == "__main__":
    main()

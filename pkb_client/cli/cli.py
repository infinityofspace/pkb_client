import argparse
import dataclasses
import json
import os
import textwrap
from datetime import datetime

from pkb_client.client import PKBClient, API_ENDPOINT
from pkb_client.client.dns import DNSRecordType, DNSRestoreMode
from pkb_client.client.forwarding import URLForwardingType


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def main():
    parser = argparse.ArgumentParser(
        description="Python client for the Porkbun API",
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
    parser.add_argument("--debug", help="Enable debug mode.", action="store_true")
    parser.add_argument("--endpoint", help="The API endpoint to use.", default=API_ENDPOINT)

    subparsers = parser.add_subparsers(help="Supported API methods")

    parser_ping = subparsers.add_parser("ping", help="Ping the API Endpoint")
    parser_ping.set_defaults(func=PKBClient.ping)

    parser_dns_create = subparsers.add_parser("dns-create", help="Create a new DNS record.")
    parser_dns_create.set_defaults(func=PKBClient.dns_create)
    parser_dns_create.add_argument("domain", help="The domain for which the new DNS record should be created.")
    parser_dns_create.add_argument("record_type", help="The type of the new DNS record.",
                                   choices=list(DNSRecordType))
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
                                 choices=list(DNSRecordType))
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

    parser_dns_export = subparsers.add_parser("dns-export", help="Save all DNS records to a local json file.")
    parser_dns_export.set_defaults(func=PKBClient.dns_export)
    parser_dns_export.add_argument("domain",
                                   help="The domain for which the DNS record should be retrieved and saved.")
    parser_dns_export.add_argument("filename", help="The filename where to save the exported DNS records.")

    parser_dns_export_bind = subparsers.add_parser("dns-export-bind", help="Save all DNS records to a local BIND file.")
    parser_dns_export_bind.set_defaults(func=PKBClient.dns_export_bind)
    parser_dns_export_bind.add_argument("domain",
                                        help="The domain for which the DNS record should be retrieved and saved.")
    parser_dns_export_bind.add_argument("filename", help="The filename where to save the exported DNS records.")

    parser_dns_import = subparsers.add_parser("dns-import", help="Restore all DNS records from a local json file.",
                                              formatter_class=argparse.RawTextHelpFormatter)
    parser_dns_import.set_defaults(func=PKBClient.dns_import)
    parser_dns_import.add_argument("domain", help="The domain for which the DNS record should be restored.")
    parser_dns_import.add_argument("filename", help="The filename from which the DNS records are to be restored.")
    parser_dns_import.add_argument("restore_mode", help="""The restore mode (DNS records are identified by the record id):
    clear: remove all existing DNS records and restore all DNS records from the provided file
    replace: replace only existing DNS records with the DNS records from the provided file, but do not create any new DNS records
    keep: keep the existing DNS records and only create new ones for all DNS records from the specified file if they do not exist
    """, type=DNSRestoreMode.from_string, choices=list(DNSRestoreMode))

    parser_dns_import_bind = subparsers.add_parser("dns-import-bind",
                                                   help="Restore all DNS records from a local BIND file.",
                                                   formatter_class=argparse.RawTextHelpFormatter)
    parser_dns_import_bind.set_defaults(func=PKBClient.dns_import_bind)
    parser_dns_import_bind.add_argument("filename", help="The filename from which the DNS records are to be restored.")
    parser_dns_import_bind.add_argument("restore_mode", help="""The restore mode (DNS records are identified by the record id):
    clear: remove all existing DNS records and restore all DNS records from the provided file
    """, type=DNSRestoreMode.from_string, choices=[DNSRestoreMode.clear])

    parser_domain_pricing = subparsers.add_parser("domain-pricing", help="Get the pricing for Porkbun domains.")
    parser_domain_pricing.set_defaults(func=PKBClient.get_domain_pricing)

    parser_ssl_retrieve = subparsers.add_parser("ssl-retrieve", help="Retrieve an SSL bundle for given domain.")
    parser_ssl_retrieve.set_defaults(func=PKBClient.ssl_retrieve)
    parser_ssl_retrieve.add_argument("domain", help="The domain for which the SSL bundle should be retrieve.")

    parser_update_dns_server = subparsers.add_parser("dns-servers-update", help="Update the DNS servers for a domain.")
    parser_update_dns_server.set_defaults(func=PKBClient.update_dns_servers)
    parser_update_dns_server.add_argument("domain", help="The domain for which the DNS servers should be set.")
    parser_update_dns_server.add_argument("dns_servers", nargs="+", help="The DNS servers to be set.")

    parser_get_dns_server = subparsers.add_parser("dns-servers-receive", help="Retrieve the DNS servers for a domain.")
    parser_get_dns_server.set_defaults(func=PKBClient.get_dns_servers)
    parser_get_dns_server.add_argument("domain", help="The domain for which the DNS servers should be retrieved.")

    parser_list_domains = subparsers.add_parser("domains-list",
                                                help="List all domains in this account in chunks of 1000.")
    parser_list_domains.set_defaults(func=PKBClient.list_domains)
    parser_list_domains.add_argument("--start", type=int, help="The start index of the list.", default=0,
                                     required=False)

    parser_get_url_forward = subparsers.add_parser("url-forward-retrieve", help="Retrieve all URL forwards.")
    parser_get_url_forward.set_defaults(func=PKBClient.get_url_forward)
    parser_get_url_forward.add_argument("domain", help="The domain for which the URL forwards should be retrieved.")

    parser_add_url_forward = subparsers.add_parser("url-forward-create", help="Create a new URL forward.")
    parser_add_url_forward.set_defaults(func=PKBClient.add_url_forward)
    parser_add_url_forward.add_argument("domain", help="The domain for which the new URL forward should be created.")
    parser_add_url_forward.add_argument("location", help="The location to which the url forwarding should redirect.", )
    parser_add_url_forward.add_argument("type", help="The type of the url forwarding.",
                                        choices=list(URLForwardingType))
    parser_add_url_forward.add_argument("--subdomain",
                                        help="The subdomain for which the url forwarding should be added.",
                                        required=False, default="")
    parser_add_url_forward.add_argument("--include-path",
                                        help="Whether the path should be included in the url forwarding.",
                                        action="store_true", default=False)
    parser_add_url_forward.add_argument("--wildcard",
                                        help="Whether the url forwarding should be also applied to subdomains.",
                                        action="store_true", default=False)

    parser_delete_url_forward = subparsers.add_parser("url-forward-delete", help="Delete an existing URL forward.")
    parser_delete_url_forward.set_defaults(func=PKBClient.delete_url_forward)
    parser_delete_url_forward.add_argument("domain", help="The domain for which the URL forward should be deleted.")
    parser_delete_url_forward.add_argument("id", help="The id of the URL forward which should be deleted.")

    args = parser.parse_args()

    if not hasattr(args, "func"):
        raise argparse.ArgumentError(None, "No method specified. Please provide a method and try again.")

    # call the api methods which do not require authentication
    if args.func == PKBClient.get_domain_pricing:
        pkb_client = PKBClient(api_endpoint=args.endpoint)
        ret = args.func(pkb_client, **vars(args))

        print(json.dumps(ret, cls=CustomJSONEncoder, indent=4))
        exit(0)

    if args.key is None:
        # try to get the api key from the environment variable or fallback to user input
        api_key = os.environ.get("PKB_API_KEY", "")
        if len(api_key.strip()) == 0:
            while True:
                api_key = input("Please enter your API key you got from Porkbun (usually starts with \"pk\"): ")
                if len(api_key.strip()) == 0:
                    print("The api key can not be empty.")
                else:
                    break
    else:
        api_key = args.key

    if args.secret is None:
        # try to get the api secret from the environment variable or fallback to user input
        api_secret = os.environ.get("PKB_API_SECRET", "")
        if len(api_secret.strip()) == 0:
            while True:
                api_secret = input(
                    "Please enter your API key secret you got from Porkbun (usually starts with \"sk\"): ")
                if len(api_secret.strip()) == 0:
                    print("The api key secret can not be empty.")
                else:
                    break
    else:
        api_secret = args.secret

    pkb_client = PKBClient(api_key, api_secret, args.endpoint)
    ret = args.func(pkb_client, **vars(args))

    print(json.dumps(ret, cls=CustomJSONEncoder, indent=4))


if __name__ == "__main__":
    main()

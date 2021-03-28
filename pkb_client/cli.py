import argparse
import pprint
import textwrap

from pkb_client.client import PKBClient, SUPPORTED_DNS_RECORD_TYPES


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

    parser.add_argument("-k", "--key", help="The API key used for Porkbun API calls")
    parser.add_argument("-s", "--secret", help="The API secret used for Porkbun API calls")

    subparsers = parser.add_subparsers(help="Supported API methods")

    parser_ping = subparsers.add_parser("ping", help="API ping method")
    parser_ping.set_defaults(func=PKBClient.ping)

    parser_dns_create = subparsers.add_parser("dns-create", help="API dns create method")
    parser_dns_create.set_defaults(func=PKBClient.dns_create)
    parser_dns_create.add_argument("domain", help="The domain for which the new DNS record entry should be created.")
    parser_dns_create.add_argument("record_type", help="The type of the new DNS record entry.",
                                   choices=SUPPORTED_DNS_RECORD_TYPES)
    parser_dns_create.add_argument("content", help="The content of the new DNS record entry.")
    parser_dns_create.add_argument("--name",
                                   help="The subdomain or * for wildcard for which the new DNS record entry should be "
                                        "created. Not used will to create a DNS record on the root domain,",
                                   required=False)
    parser_dns_create.add_argument("--ttl", help="The ttl of the new DNS record entry.", required=False)
    parser_dns_create.add_argument("--prio", help="The priority of the new DNS record entry.", required=False)

    parser_dns_edit = subparsers.add_parser("dns-edit", help="API dns edit method")
    parser_dns_edit.set_defaults(func=PKBClient.dns_edit)
    parser_dns_edit.add_argument("domain", help="The domain for which the DNS record entry should be edited.")
    parser_dns_edit.add_argument("record_id", help="The id of the DNS record entry which should be edited.")
    parser_dns_edit.add_argument("record_type", help="The new type of the DNS record entry.",
                                 choices=SUPPORTED_DNS_RECORD_TYPES)
    parser_dns_edit.add_argument("content", help="The new content of the DNS record entry.")
    parser_dns_edit.add_argument("--name",
                                 help="The subdomain or * for wildcard for which the new DNS record entry should be "
                                      "created. Not used will to create a DNS record on the root domain,",
                                 required=False)
    parser_dns_edit.add_argument("--ttl", help="The new ttl of the DNS record entry.", required=False)
    parser_dns_edit.add_argument("--prio", help="The new priority of the DNS record entry.", required=False)

    parser_dns_delete = subparsers.add_parser("dns-delete", help="API dns delete method")
    parser_dns_delete.set_defaults(func=PKBClient.dns_delete)
    parser_dns_delete.add_argument("domain", help="The domain for which the DNS record entry should be deleted.")
    parser_dns_delete.add_argument("record_id", help="The id of the DNS record entry which should be deleted.")

    parser_dns_receive = subparsers.add_parser("dns-receive", help="API dns receive method")
    parser_dns_receive.set_defaults(func=PKBClient.dns_retrieve)
    parser_dns_receive.add_argument("domain", help="The domain for which the DNS record entries should be received.")

    args = parser.parse_args()

    if not hasattr(args, "func"):
        raise argparse.ArgumentError(None, "No api method specified. Please provide an API method and try again.")

    if args.key is None:
        while True:
            api_key = input("Please enter your API key you got from Porkbun: ")
            if len(api_key) == 0:
                print("The api key can not be empty.")
            else:
                break
    else:
        api_key = args.key

    if args.secret is None:
        while True:
            api_secret = input("Please enter your API secret you got from Porkbun: ")
            if len(api_secret) == 0:
                print("The api key can not be empty.")
            else:
                break
    else:
        api_secret = args.secret

    pkb_client = PKBClient(api_key, api_secret)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(args.func(pkb_client, **vars(args)))


if __name__ == "__main__":
    main()

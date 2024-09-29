Usage
=====

Module
++++++

The module provides the :class:`PKBClient <pkb_client.client.client.PKBClient>` class, which is used to interact with the PKB API.
To use the PKB client, you need to create an instance of the :class:`PKBClient <pkb_client.client.client.PKBClient>` class:

.. code-block:: python

    from pkb_client.client import PKBClient

    pkb = PKBClient(
        api_key="<your-api-key>",
        secret_api_key="<your-secret-api-key>",
        api_endpoint="https://porkbun.com/api/json/v3",
    )

Whereby the api_key and secret_api_key are optional and only required if you want to use the PKB API with API endpoints
that require authentication (e.g. to manage dns records of your domains). Moreover the api_endpoint is also optional and
defaults to the latest version of the official PKB API endpoint.

For example to get the domain pricing, which does not require authentication, you can use the
:func:`get_domain_pricing <pkb_client.client.client.PKBClient.get_domain_pricing>` method:

.. code-block:: python

    from pkb_client.client import PKBClient

    pkb = PKBClient()
    domain_pricing = pkb.get_domain_pricing()
    print(domain_pricing)

You can find all available methods in the :class:`PKBClient <pkb_client.client.client.PKBClient>` class documentation.

CLI
+++

The module also provides a CLI to interact with the PKB API. For example to get the domain pricing, you can use the `get-domain-pricing` command:

.. code-block:: bash

    pkb-client domain-pricing

All available commands can be listed with the `--help` option:

.. code-block:: bash

    pkb-client --help

.. code-block:: bash

    usage: cli.py [-h] [-k KEY] [-s SECRET] [--debug] [--endpoint ENDPOINT]
              {ping,dns-create,dns-edit,dns-delete,dns-retrieve,dns-export,dns-export-bind,dns-import,dns-import-bind,domain-pricing,ssl-retrieve,dns-servers-update,dns-servers-receive,domains-list,url-forward-retrieve,url-forward-create,url-forward-delete}
              ...

    Python client for the Porkbun API

    positional arguments:
      {ping,dns-create,dns-edit,dns-delete,dns-retrieve,dns-export,dns-export-bind,dns-import,dns-import-bind,domain-pricing,ssl-retrieve,dns-servers-update,dns-servers-receive,domains-list,url-forward-retrieve,url-forward-create,url-forward-delete}
                            Supported API methods
        ping                Ping the API Endpoint
        dns-create          Create a new DNS record.
        dns-edit            Edit an existing DNS record.
        dns-delete          Delete an existing DNS record.
        dns-retrieve        Get all DNS records.
        dns-export          Save all DNS records to a local json file.
        dns-export-bind     Save all DNS records to a local BIND file.
        dns-import          Restore all DNS records from a local json file.
        dns-import-bind     Restore all DNS records from a local BIND file.
        domain-pricing      Get the pricing for Porkbun domains.
        ssl-retrieve        Retrieve an SSL bundle for given domain.
        dns-servers-update  Update the DNS servers for a domain.
        dns-servers-receive
                            Retrieve the DNS servers for a domain.
        domains-list        List all domains in this account in chunks of 1000.
        url-forward-retrieve
                            Retrieve all URL forwards.
        url-forward-create  Create a new URL forward.
        url-forward-delete  Delete an existing URL forward.

    options:
      -h, --help            show this help message and exit
      -k KEY, --key KEY     The API key used for Porkbun API calls (usually starts with "pk").
      -s SECRET, --secret SECRET
                            The API secret used for Porkbun API calls (usually starts with "sk").
      --debug               Enable debug mode.
      --endpoint ENDPOINT   The API endpoint to use.
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
        api_endpoint="https://api.porkbun.com/api/json/v3",
    )

Whereby the `api_key` and `secret_api_key` are optional and only required if you want to use the PKB API with API endpoints
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

    usage: pkb-client [-h] [-k KEY] [-s SECRET] [--debug] [--endpoint ENDPOINT]
                  {ping,create-dns-record,update-dns-record,delete-dns-records,get-dns-records,export-dns-records,export-bind-dns-records,import-dns-records,import-bind-dns-records,get-domain-pricing,get-ssl-bundle,update-dns-servers,get-dns-servers,get-domains,get-url-forwards,create-url-forward,delete-url-forward}
                  ...

    Python client for the Porkbun API

    positional arguments:
      {ping,create-dns-record,update-dns-record,delete-dns-records,get-dns-records,export-dns-records,export-bind-dns-records,import-dns-records,import-bind-dns-records,get-domain-pricing,get-ssl-bundle,update-dns-servers,get-dns-servers,get-domains,get-url-forwards,create-url-forward,delete-url-forward}
                            Supported API methods
        ping                Ping the API Endpoint
        create-dns-record   Create a new DNS record.
        update-dns-record   Edit an existing DNS record.
        delete-dns-records  Delete an existing DNS record.
        get-dns-records     Get all DNS records.
        export-dns-records  Save all DNS records to a local json file.
        export-bind-dns-records
                            Save all DNS records to a local BIND file.
        import-dns-records  Restore all DNS records from a local json file.
        import-bind-dns-records
                            Restore all DNS records from a local BIND file.
        get-domain-pricing  Get the pricing for Porkbun domains.
        get-ssl-bundle      Retrieve an SSL bundle for given domain.
        update-dns-servers  Update the DNS servers for a domain.
        get-dns-servers     Retrieve the DNS servers for a domain.
        get-domains         List all domains in this account in chunks of 1000.
        get-url-forwards    Retrieve all URL forwards.
        create-url-forward  Create a new URL forward.
        delete-url-forward  Delete an existing URL forward.

    options:
      -h, --help            show this help message and exit
      -k KEY, --key KEY     The API key used for Porkbun API calls (usually starts with "pk").
      -s SECRET, --secret SECRET
                            The API secret used for Porkbun API calls (usually starts with "sk").
      --debug               Enable debug mode.
      --endpoint ENDPOINT   The API endpoint to use.

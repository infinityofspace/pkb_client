Usage
=====

Module
++++++

The module provides the :class:`PKBClient <pkb_client.client.PKBClient>` class, which is used to interact with the PKB API.
To use the PKB client, you need to create an instance of the :class:`PKBClient <pkb_client.client.PKBClient>` class:

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
:func:`get_domain_pricing <pkb_client.client.PKBClient.get_domain_pricing>` method:

.. code-block:: python

    from pkb_client.client import PKBClient

    pkb = PKBClient()
    domain_pricing = pkb.get_domain_pricing()
    print(domain_pricing)

You can find all available methods in the :class:`PKBClient <pkb_client.client.PKBClient>` class documentation.

CLI
+++

The module also provides a CLI to interact with the PKB API. To use the CLI, you need to install the package:

.. code-block:: bash

    pip install pkb_client

This creates the `pkb-client` command, which can be used to interact with the PKB API.
For example to get the domain pricing, you can use the `get-domain-pricing` command:

.. code-block:: bash

    pkb-client domain-pricing

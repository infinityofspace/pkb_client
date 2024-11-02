Migration Guide
===============

From v1 to v2
+++++++++++++

The version 2 of the package is a major release that introduces a lot of changes. The main changes are:

- support for new API methods
- package is now a proper Python package with focus on usage as a library (in general more object oriented):
    - return types are now objects instead of tuples or dictionaries (except domain pricing method)
    - improved and more consistent error handling
    - fixed method signatures/no more additional keyworded arguments

These changes are not backward compatible with the version 1 of the package. If you are using the version 1 of the
package, you will need to update your code to work with the version 2.

To migrate your code from the version 1 to the version 2, follow these steps:

1. Update the package to the version 2 or higher:
    - if you are using the package from PyPI, run the following command:
        .. code-block:: bash

           pip3 install --upgrade pkb_client
    - if you are using the package from the source code, run the following commands:
        .. code-block:: bash

           git fetch
           git checkout v2.0.0 # or any later tag
           pip3 install .
2. Remove any additional keyworded arguments from all `PKBClient` methods. The methods now have fixed signatures.
3. Refactor the usage of the following methods:
    - `PKBClient.dns_create`:
        - renamed to `PKBClient.create_dns_record`
        - the method argument `record_type` needs to be enum of :class:`DNSRecordType <pkb_client.client.dns.DNSRecordType>`
    - `PKBClient.dns_edit`:
        - renamed to `PKBClient.update_dns_record`
        - the method argument `record_type` needs to be enum of :class:`DNSRecordType <pkb_client.client.dns.DNSRecordType>`
    - `PKBClient.dns_delete`:
        - renamed to `PKBClient.delete_dns_records`
    - `PKBClient.dns_retrieve`:
        - renamed to `PKBClient.get_dns_records`
        - return type is now a list of :class:`DNSRecord <pkb_client.client.dns.DNSRecord>`
    - `PKBClient.dns_export`:
        - renamed to `PKBClient.export_dns_records`
        - the methods argument `filename` is renamed to `filepath`
    - `PKBClient.dns_import`:
        - renamed to `PKBClient.import_dns_records`
        - the methods argument `filename` is renamed to `filepath`
    - `PKBClient.get_domain_pricing`:
        - method is not static anymore, you need to create an instance of `PKBClient` to use it
    - `PKBClient.ssl_retrieve`:
        - renamed to `PKBClient.get_ssl_bundle`
        - return type is now :class:`SSLCertificate <pkb_client.client.ssl_cert.SSLCertBundle>`

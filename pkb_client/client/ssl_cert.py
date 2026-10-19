"""SSL certificate bundle data returned by the Porkbun API."""

from dataclasses import dataclass


@dataclass
class SSLCertBundle:
    """Represent the certificate bundle for a domain."""

    # The complete certificate chain.
    certificate_chain: str

    # The private key.
    private_key: str

    # The public key.
    public_key: str

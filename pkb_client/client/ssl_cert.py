from dataclasses import dataclass


@dataclass
class SSLCertBundle:
    # The complete certificate chain.
    certificate_chain: str

    # The private key.
    private_key: str

    # The public key.
    public_key: str

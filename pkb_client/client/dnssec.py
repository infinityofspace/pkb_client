from dataclasses import dataclass


@dataclass
class DNSSECRecord:
    key_tag: int  # The key tag is a 16-bit integer that identifies the DNSKEY record
    alg: int  # Indicates the algorithm used to generate the public key
    digest_type: int  # Indicates the type of digest algorithm used
    digest: str  # The digest of the public key
    max_sig_life: int | None  # Indicates the amount of time in seconds the signature is valid
    key_data_flags: int | None  # Indicates the key type (Zone-signing or Key-signing)
    key_data_protocol: int | None  # Indicates the protocol used for the key
    key_data_algo: int | None  # Indicates the algorithm used for the key
    key_data_pub_key: str | None  # The public key in base64 format

from dataclasses import dataclass
from typing import Optional


@dataclass
class DNSSECRecord:
    key_tag: int  # The key tag is a 16-bit integer that identifies the DNSKEY record
    alg: int  # Indicates the algorithm used to generate the public key
    digest_type: int  # Indicates the type of digest algorithm used
    digest: str  # The digest of the public key
    max_sig_life: Optional[
        int
    ]  # Indicates the amount of time in seconds the signature is valid
    key_data_flags: Optional[
        int
    ]  # Indicates the key type (Zone-signing or Key-signing)
    key_data_protocol: Optional[int]  # Indicates the protocol used for the key
    key_data_algo: Optional[int]  # Indicates the algorithm used for the key
    key_data_pub_key: Optional[str]  # The public key in base64 format

    @staticmethod
    def from_dict(d):
        return DNSSECRecord(
            key_tag=int(d["keyTag"]),
            alg=int(d["alg"]),
            digest_type=int(d["digestType"]),
            digest=d["digest"],
            max_sig_life=int(d["maxSigLife"]) if "maxSigLife" in d else None,
            key_data_flags=int(d["keyDataFlags"]) if "keyDataFlags" in d else None,
            key_data_protocol=int(d["keyDataProtocol"])
            if "keyDataProtocol" in d
            else None,
            key_data_algo=int(d["keyDataAlgo"]) if "keyDataAlgo" in d else None,
            key_data_pub_key=d["keyDataPubKey"] if "keyDataPubKey" in d else None,
        )

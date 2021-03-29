def parse_dns_record(record: dict) -> dict:
    """
    Parse the DNS record.
    Replace the ttl and prio string values with the int values.

    :param record: the unparsed DNS record dict

    :return: the parsed dns record dict
    """
    if record.get("ttl", None) is not None:
        record["ttl"] = int(record["ttl"])
    if record.get("prio", None) is not None:
        record["prio"] = int(record["prio"])

    return record

# pkb_client

Unofficial client for the Porkbun API

---
[![PyPI](https://img.shields.io/pypi/v/pkb_client)](https://pypi.org/project/pkb-client/) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pkb_client) [![Downloads](https://static.pepy.tech/personalized-badge/pkb-client?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Total%20Downloads)](https://pepy.tech/project/pkb-client) ![GitHub](https://img.shields.io/github/license/infinityofspace/pkb_client) ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/infinityofspace/pkb_client/pypi-publish-release.yml)
---

### Table of Contents

1. [About](#about)
2. [Installation](#installation)
    1. [With pip (recommend)](#with-pip-recommend)
    2. [From source](#from-source)
3. [Usage](#usage)
4. [Notes](#notes)
5. [Third party notices](#third-party-notices)
6. [License](#license)

---

### About

*pkb_client* is an unofficial client for the [Porkbun](https://porkbun.com) API. It supports the v3 of the API. You can
find the official documentation of the Porkbun API [here](https://porkbun.com/api/json/v3/documentation).

### Installation

This project only works with Python 3, make sure you have at least Python 3.8 installed.

#### With pip (recommend)

Use the following command to install *pkb_client* with pip:

```commandline
pip3 install pkb_client
```

You can also very easily update to a newer version:

```commandline
pip3 install pkb_client -U
```

#### From source

```commandline
git clone https://github.com/infinityofspace/pkb_client.git
cd pkb_client
pip install .
```

### Usage

Each request must be made with the API key and secret. You can easily create them at Porkbun. Just follow
the [official instructions](https://porkbun.com/api/json/v3/documentation#Authentication). Make sure that you explicitly
activate the API usage for your domain at the end.

After installation *pkb_client* is available under the command `pkb-client`.

You have to specify your API key and secret each time as follows:

```commandline
pkb-client -k <YOUR-API-KEY> -s <YOUR-API-SECRET> ping
```

If you don't want to specify the key and secret in the program call, because for example the command line calls are
logged and you don't want to log the API access, then you can also omit both arguments and *pkb-client* asks for a user
input.

You can see an overview of all usable API methods via the help:

```commandline
pkb-client -h
```

If you need more help on a supported API method, you can use the following command, for example for the ping method:

```commandline
pkb-client ping -h
```

#### Here are a few usage examples:

Create a new TXT record for the subdomain `test` of the domain `example.com` with the value `porkbun is cool` and a TTL
of `500`:

```commandline
pkb-client -k <YOUR-API-KEY> -s <YOUR-API-KEY-SECRET> dns-create example.com TXT "porkbun is cool" --name test --ttl 500
```

The call returns the DNS record id. The record DNS ids are used to distinguish the DNS records and can be used for
editing or deleting records. The ID is only a Porkbun internal identifier and is not publicly available.

Delete the DNS record with the ID `12345` of the domain `example.com`:

```commandline
pkb-client -k <YOUR-API-KEY> -s <YOUR-API-SECRET> dns-delete example.com 12345
```

Get all DNS records of the domain `example.com`:

```commandline
pkb-client -k <YOUR-API-KEY> -s <YOUR-API-SECRET> dns-retrieve example.com
```

Change the TXT DNS record content with the ID `456789` of the domain `example.com` to `the answer is 42`:

```commandline
pkb-client -k <YOUR-API-KEY> -s <YOUR-API-SECRET> dns-edit example.com 456789 TXT "the answer is 42"
```

Exporting all current DNS records of the domain `example.com` to the file `dns_recods.json`:

```commandline
pkb-client -k <YOUR-API-KEY> -s <YOUR-API-SECRET> dns-export example.com dns_recods.json
```

Remove all existing DNS records of the domain `example.com` and restore the DNS records from the file `dns_recods.json`:

```commandline
pkb-client -k <YOUR-API-KEY> -s <YOUR-API-SECRET> dns-import example.com dns_recods.json clear
```

*Note:* The import function uses the record ID to distinguish DNS records.

### Notes

Currently, TTL smaller than `600` are ignored by the Porkbun API and the minimum value is `600`, although a minimum
value of `300` is [supported](https://porkbun.com/api/json/v3/documentation) and allowed by the RFC standard. However,
you can do TTL smaller than `600` via the web dashboard.

### Third party notices

All modules used by this project are listed below:

|                       Name                       |                                   License                                   |
|:------------------------------------------------:|:---------------------------------------------------------------------------:|
|   [requests](https://github.com/psf/requests)    | [Apache 2.0](https://raw.githubusercontent.com/psf/requests/master/LICENSE) |
| [setuptools](https://github.com/pypa/setuptools) |    [MIT](https://raw.githubusercontent.com/pypa/setuptools/main/LICENSE)    |

Furthermore, this readme file contains embeddings of [Shields.io](https://github.com/badges/shields)
and [PePy](https://github.com/psincraian/pepy). The tests use [ipify](https://github.com/rdegges/ipify-api).

### License

[MIT](https://github.com/infinityofspace/pkb_client/blob/master/License) - Copyright (c) Marvin Heptner

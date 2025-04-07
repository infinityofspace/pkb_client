from setuptools import setup, find_packages

import pkb_client

with open("Readme.md") as f:
    long_description = f.read()

setup(
    name="pkb_client",
    version=pkb_client.__version__,
    author="infinityofspace",
    url="https://github.com/infinityofspace/pkb_client",
    description="Python client for the Porkbun API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Utilities",
        "Topic :: System :: Systems Administration",
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["setuptools>=39.0.1", "requests>=2.20.0", "dnspython~=2.7"],
    entry_points={
        "console_scripts": [
            "pkb-client = pkb_client.cli.cli:main",
        ]
    },
)

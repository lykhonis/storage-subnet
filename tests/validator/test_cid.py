import unittest
import hashlib
import requests

# https://github.com/thunderstore-io/ipfs-cid
# https://stackoverflow.com/questions/75803958/how-to-compute-the-ipfs-content-identifier-cid-from-file-content-in-python
from ipfs_cid import cid_sha256_hash  # pip install ipfs-cid
from py_ipfs_cid import compute_cid  # pip install py-ipfs-cid
from storage.validator.cid import make_cid, decode_cid
from storage.validator.cid import *


def fetch_ipfs_content(cid):
    gateway_url = f"https://ipfs.io/ipfs/{cid}"
    response = requests.get(gateway_url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(
            f"Failed to retrieve content. Status code: {response.status_code}"
        )


AARDVARK_CIDv0 = "QmcRD4wkPPi6dig81r5sLj9Zm1gDCL4zgpEj9CfuRrGbzF"
aardvark = fetch_ipfs_content(AARDVARK_CIDv0)
aardvark_cidv0: str = compute_cid(aardvark)
aardvark_cidv1: str = cid_sha256_hash(aardvark)
print(f"IPFS CIDv0: {aardvark_cidv0}")
print(f"IPFS OGCID: {AARDVARK_CIDv0}")
print(f"IPFS CIDv1: {aardvark_cidv1}")

assert (
    aardvark_cidv0 == AARDVARK_CIDv0
), f"IPFS CIDv0 {aardvark_cidv0} does not match OG CID {AARDVARK_CIDv0}"
assert (
    decode_cid(aardvark_cidv1) == hashlib.sha256(aardvark).digest()
), f"IPFS CIDv1 {decode_cid(aardvark_cidv1)} hash does not match expected hash {hashlib.sha256(aardvark).digest()}"
assert (
    make_cid(aardvark, version=0).multihash.decode() == AARDVARK_CIDv0
), f"CIDv0 {make_cid(aardvark, version=0).multihash.decode()} does not match IPFS CIDv0 {AARDVARK_CIDv0}"
assert (
    decode_cid(aardvark_cidv0) == hashlib.sha256(aardvark).digest()
), f"IPFS CIDv0 hash {decode_cid(aardvark_cidv0) } does not match expected hash {hashlib.sha256(aardvark).digest()}"


class TestCIDFunctions(unittest.TestCase):
    def test_cid(self):
        # Testing both CIDv0 and CIDv1
        for version in [0, 1]:
            with self.subTest(version=version):
                raw_data = "abcdef"
                cid = make_cid(raw_data, version=version)
                decoded_hash = decode_cid(cid)
                self.assertEqual(
                    decoded_hash, hashlib.sha256(raw_data.encode()).digest()
                )

    def test_cid_with_different_inputs(self):
        # Testing both CIDv0 and CIDv1
        for version in [0, 1]:
            test_data = [
                "",  # Empty string
                "Hello World",  # Simple string
                "😊🌍🚀",  # Unicode string
                "a" * 1000,  # Long string
            ]

            for data in test_data:
                with self.subTest(data=data, version=version):
                    cid = make_cid(data, version=version)
                    decoded_hash = decode_cid(cid)
                    self.assertEqual(
                        decoded_hash,
                        hashlib.sha256(data.encode()).digest(),
                        f"Test failed for data: {data} with version: {version}",
                    )


class TestIPFSParity(unittest.TestCase):
    def setUp(self):
        self.aardvark = fetch_ipfs_content(AARDVARK_CIDv0)

    def test_cid_parity(self):
        # Generate CIDv0 using your implementation
        your_cid_v0 = make_cid(self.aardvark, version=0)
        self.assertEqual(
            your_cid_v0.multihash.decode(),
            AARDVARK_CIDv0,
            "CIDv0 does not match IPFS CIDv0",
        )

        # Generate CIDv1 using your implementation
        your_cid_v1 = make_cid(self.aardvark, version=1)
        self.assertEqual(
            decode_cid(your_cid_v1),
            hashlib.sha256(self.aardvark).digest(),
            "CIDv1 hash does not match expected hash",
        )


if __name__ == "__main__":
    unittest.main()

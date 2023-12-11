'''Tests the Python hashes
'''
from hashlib import md5, sha1, sha256
from pathlib import Path

import pytest

from pyfilehash import hasher


@pytest.mark.parametrize(
    'test_file',
    (1024, 1024*1024, 1024*1024*1024),
    indirect=True
)
def test_sha256(test_file: Path):
    """Tests the SHA256 hash

    Args:
        test_file (Path): File to hash
    """
    with open(test_file, 'rb') as handle:
        digest = sha256(handle.read()).hexdigest()
    py_digest = hasher.compute_sha256(test_file)
    assert digest == py_digest


@pytest.mark.parametrize(
    'test_file',
    (1024, 1024*1024, 1024*1024*1024),
    indirect=True
)
def test_sha1(test_file: Path):
    """Tests the SHA1 hash

    Args:
        test_file (Path): File to hash
    """
    with open(test_file, 'rb') as handle:
        digest = sha1(handle.read()).hexdigest()
    py_digest = hasher.compute_sha1(test_file)
    assert digest == py_digest


@pytest.mark.parametrize(
    'test_file',
    (1024, 1024*1024, 1024*1024*1024),
    indirect=True
)
def test_md5(test_file: Path):
    """Tests the MD5 hash

    Args:
        test_file (Path): File to hash
    """
    with open(test_file, 'rb') as handle:
        digest = md5(handle.read()).hexdigest()
    py_digest = hasher.compute_md5(test_file)
    assert digest == py_digest

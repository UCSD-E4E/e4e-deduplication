'''Tests the C hashes
'''
from pathlib import Path
from hashlib import sha256, sha1, md5
import pytest

import file_hasher


@pytest.mark.parametrize(
    'test_file',
    (1024, 2048, 4096, 1024*1024, 1024*1024*1024),
    indirect=True
)
def test_sha256(test_file: Path):
    """Tests the C SHA256 hash

    Args:
        test_file (Path): File to hash
    """
    with open(test_file, 'rb') as handle:
        digest = sha256(handle.read()).hexdigest()
    c_digest = file_hasher.compute_digest(
        file_hasher.HashType.SHA256, test_file.as_posix())
    assert digest == c_digest


@pytest.mark.parametrize(
    'test_file',
    (1024, 2048, 4096, 1024*1024, 1024*1024*1024),
    indirect=True
)
def test_sha1(test_file: Path):
    """Tests the C SHA1 hash

    Args:
        test_file (Path): File to hash
    """
    with open(test_file, 'rb') as handle:
        digest = sha1(handle.read()).hexdigest()
    c_digest = file_hasher.compute_digest(
        file_hasher.HashType.SHA1, test_file.as_posix())
    assert digest == c_digest


@pytest.mark.parametrize(
    'test_file',
    (1024, 2048, 4096, 1024*1024, 1024*1024*1024),
    indirect=True
)
def test_md5(test_file: Path):
    """Tests the c MD5 hash

    Args:
        test_file (Path): File to hash
    """
    with open(test_file, 'rb') as handle:
        digest = md5(handle.read()).hexdigest()
    c_digest = file_hasher.compute_digest(
        file_hasher.HashType.MD5, test_file.as_posix())
    assert digest == c_digest

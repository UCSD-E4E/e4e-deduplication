'''Python Interface
'''
from pathlib import Path

from file_hasher import HashType, compute_digest


def compute_sha256(path: Path) -> str:
    """Computes the SHA256 hash of the given path

    Args:
        path (Path): File to hash

    Raises:
        RuntimeError: Not a file

    Returns:
        str: SHA256 hash digest
    """
    if not path.is_file():
        raise RuntimeError("Not a file")
    return compute_digest(HashType.SHA256, path.as_posix())


def compute_sha1(path: Path) -> str:
    """Computes the SHA1 hash of the given path

    Args:
        path (Path): File to hash

    Raises:
        RuntimeError: Not a file

    Returns:
        str: SHA1 hash digest
    """
    if not path.is_file():
        raise RuntimeError("Not a file")
    return compute_digest(HashType.SHA1, path.as_posix())


def compute_md5(path: Path) -> str:
    """Computes the MD5 hash of the given path

    Args:
        path (Path): File to hash

    Raises:
        RuntimeError: Not a file

    Returns:
        str: MD5 hash digest
    """
    if not path.is_file():
        raise RuntimeError("Not a file")
    return compute_digest(HashType.MD5, path.as_posix())

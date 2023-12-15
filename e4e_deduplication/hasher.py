'''File based hashers
'''
from hashlib import sha256
from pathlib import Path


def compute_sha256(path: Path) -> str:
    """Computes the SHA256 sum

    Args:
        path (Path): Path to hash

    Returns:
        str: Digest
    """
    hasher = sha256()
    with open(path, 'rb') as handle:
        while blob := handle.read(2*1024*1024):
            hasher.update(blob)
    return hasher.hexdigest()

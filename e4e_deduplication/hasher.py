'''File based hashers
'''
import logging
from hashlib import sha256
from pathlib import Path


def compute_sha256(path: Path) -> str:
    """Computes the SHA256 sum

    Args:
        path (Path): Path to hash

    Returns:
        str: Digest
    """
    logger = logging.getLogger('compute_sha256')
    hasher = sha256()
    with open(path, 'rb') as handle:
        try:
            while blob := handle.read(2*1024*1024):
                hasher.update(blob)
        except OSError:
            logger.exception(f'Exception when reading from {path}')
    return hasher.hexdigest()

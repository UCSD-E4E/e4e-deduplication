'''Tests hashing under multiprocessing
'''
import logging
import time
from hashlib import md5, sha1, sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Tuple

import pytest
from utils import create_random_file

from e4e_deduplication.analyzer import ParallelHasher
from pyfilehash.hasher import compute_md5, compute_sha1, compute_sha256


# Note that for 4 files, the setup time for Pool does not outweigh the time penalty of Python
@pytest.mark.parametrize(
    'n_files',
    (8, 16)
)
def test_sha256_parallel(n_files: int):
    """Tests parallel sha256

    Args:
        n_files (int): Number of files to test
    """
    logger = logging.getLogger('sha256_parallel')
    with TemporaryDirectory() as tmp_dir:
        files: List[Path] = []
        for file_idx in range(n_files):
            new_file = Path(tmp_dir, f'rand_{file_idx:03d}')
            create_random_file(new_file, 128*1024*1024)
            files.append(new_file)
        digests: List[Tuple[Path, str]] = []
        start = time.perf_counter()
        ParallelHasher(lambda x, y: digests.append(
            (x, y)), None, hash_fn=python_sha256).run(files, n_files)
        end = time.perf_counter()
        python_digests = dict(digests)
        python_time = end - start

        digests: List[Tuple[Path, str]] = []
        start = time.perf_counter()
        ParallelHasher(lambda x, y: digests.append(
            (x, y)), None, hash_fn=compute_sha256).run(files, n_files)
        end = time.perf_counter()
        c_time = end - start
        c_digests = dict(digests)

        assert python_digests == c_digests
        if c_time > python_time:
            logger.critical(f'C takes {c_time}, python takes {python_time}')


def python_sha256(file: Path) -> str:
    """Python SHA256 hasher

    Args:
        file (Path): File to hash

    Returns:
        str: SHA256 Hash
    """
    with open(file, 'rb') as handle:
        return sha256(handle.read()).hexdigest()


@pytest.mark.parametrize(
    'n_files',
    (8, 16)
)
def test_sha1_parallel(n_files: int):
    """Tests sha1 in parallel

    Args:
        n_files (int): Number of files to test
    """
    logger = logging.getLogger('sha1_parallel')
    with TemporaryDirectory() as tmp_dir:
        files: List[Path] = []
        for file_idx in range(n_files):
            new_file = Path(tmp_dir, f'rand_{file_idx:03d}')
            create_random_file(new_file, 128*1024*1024)
            files.append(new_file)
        digests: List[Tuple[Path, str]] = []
        start = time.perf_counter()
        ParallelHasher(lambda x, y: digests.append(
            (x, y)), None, hash_fn=python_sha1).run(files, n_files)
        end = time.perf_counter()
        python_digests = dict(digests)
        python_time = end - start

        digests: List[Tuple[Path, str]] = []
        start = time.perf_counter()
        ParallelHasher(lambda x, y: digests.append(
            (x, y)), None, hash_fn=compute_sha1).run(files, n_files)
        end = time.perf_counter()
        c_time = end - start
        c_digests = dict(digests)

        assert python_digests == c_digests
        if c_time > python_time:
            logger.critical(f'C takes {c_time}, python takes {python_time}')


def python_sha1(file: Path) -> str:
    """Python SHA1 hasher

    Args:
        file (Path): Path to file to hash

    Returns:
        str: SHA1 digest
    """
    with open(file, 'rb') as handle:
        return sha1(handle.read()).hexdigest()


@pytest.mark.parametrize(
    'n_files',
    (8, 16)
)
def test_md5_parallel(n_files: int):
    """Tests parallel MD5 hashing

    Args:
        n_files (int): Number of files
    """
    logger = logging.getLogger('md5_parallel')
    with TemporaryDirectory() as tmp_dir:
        files: List[Path] = []
        for file_idx in range(n_files):
            new_file = Path(tmp_dir, f'rand_{file_idx:03d}')
            create_random_file(new_file, 128*1024*1024)
            files.append(new_file)
        digests: List[Tuple[Path, str]] = []
        start = time.perf_counter()
        ParallelHasher(lambda x, y: digests.append(
            (x, y)), None, hash_fn=python_md5).run(files, n_files)
        end = time.perf_counter()
        python_digests = dict(digests)
        python_time = end - start

        digests: List[Tuple[Path, str]] = []
        start = time.perf_counter()
        ParallelHasher(lambda x, y: digests.append(
            (x, y)), None, hash_fn=compute_md5).run(files, n_files)
        end = time.perf_counter()
        c_time = end - start
        c_digests = dict(digests)

        assert python_digests == c_digests
        if c_time > python_time:
            logger.critical(f'C takes {c_time}, python takes {python_time}')


def python_md5(file: Path) -> str:
    """Python MD5 Hash

    Args:
        file (Path): File to hash

    Returns:
        str: MD5 Hash
    """
    with open(file, 'rb') as handle:
        return md5(handle.read()).hexdigest()

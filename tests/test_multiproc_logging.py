'''Tests parallel logging
'''
import logging
import time
from hashlib import sha256
from multiprocessing import Pool
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import multiprocessing_logging
from tqdm import tqdm
from utils import create_random_file

from pyfilehash import hasher


def __parallel_create_file(path: Path) -> None:
    create_random_file(path, 128*1024)


def test_sha256_parallel_logging():
    """Tests parallel sha256

    Args:
        n_files (int): Number of files to test
    """
    n_files: int = 1024*512
    logger = logging.getLogger('sha256_parallel')
    # multiprocessing_logging.install_mp_handler()
    with TemporaryDirectory() as tmp_dir:
        files: List[Path] = [
            Path(tmp_dir, f'rand_{file_idx:03d}') for file_idx in range(n_files)]
        with Pool() as pool:
            tqdm(pool.imap_unordered(__parallel_create_file, files), total=n_files)
        start = time.perf_counter()
        with Pool() as pool:
            digests = list(
                tqdm(pool.imap(python_sha256, files), total=n_files))
        end = time.perf_counter()
        python_digests = {files[idx]: digests[idx]
                          for idx in range(len(files))}
        python_time = end - start

        start = time.perf_counter()
        with Pool() as pool:
            digests = pool.map(hasher.compute_sha256, files)
        end = time.perf_counter()
        c_time = end - start
        c_digests = {files[idx]: digests[idx] for idx in range(len(files))}

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

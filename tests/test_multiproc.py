'''Tests hashing under multiprocessing
'''
import time
from hashlib import sha256, sha1, md5
from multiprocessing import Pool
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytest
from utils import create_random_file

from pyfilehash import hasher


# Note that for 4 files, the setup time for Pool does not outweigh the time penalty of Python
@pytest.mark.parametrize(
    'n_files',
    (8, 16)
)
def test_sha256_parallel(n_files: int):
    with TemporaryDirectory() as tmp_dir:
        files: List[Path] = []
        for file_idx in range(n_files):
            new_file = Path(tmp_dir, f'rand_{file_idx:03d}')
            create_random_file(new_file, 512*1024*1024)
            files.append(new_file)
        start = time.perf_counter()
        with Pool() as pool:
            digests = pool.map(python_sha256, files)
        end = time.perf_counter()
        python_digests = {files[idx]:digests[idx] for idx in range(len(files))}
        python_time = end - start

        start = time.perf_counter()
        with Pool() as pool:
            digests = pool.map(hasher.compute_sha256, files)
        end = time.perf_counter()
        c_time = end - start
        c_digests = {files[idx]:digests[idx] for idx in range(len(files))}

        assert python_digests == c_digests
        assert c_time <= python_time

def python_sha256(file: Path):
    with open(file, 'rb') as handle:
        return sha256(handle.read()).hexdigest()

@pytest.mark.parametrize(
    'n_files',
    (8, 16)
)
def test_sha1_parallel(n_files: int):
    with TemporaryDirectory() as tmp_dir:
        files: List[Path] = []
        for file_idx in range(n_files):
            new_file = Path(tmp_dir, f'rand_{file_idx:03d}')
            create_random_file(new_file, 512*1024*1024)
            files.append(new_file)
        start = time.perf_counter()
        with Pool() as pool:
            digests = pool.map(python_sha1, files)
        end = time.perf_counter()
        python_digests = {files[idx]:digests[idx] for idx in range(len(files))}
        python_time = end - start

        start = time.perf_counter()
        with Pool() as pool:
            digests = pool.map(hasher.compute_sha1, files)
        end = time.perf_counter()
        c_time = end - start
        c_digests = {files[idx]:digests[idx] for idx in range(len(files))}

        assert python_digests == c_digests
        assert c_time <= python_time

def python_sha1(file: Path):
    with open(file, 'rb') as handle:
        return sha1(handle.read()).hexdigest()

@pytest.mark.parametrize(
    'n_files',
    (8, 16)
)
def test_md5_parallel(n_files: int):
    with TemporaryDirectory() as tmp_dir:
        files: List[Path] = []
        for file_idx in range(n_files):
            new_file = Path(tmp_dir, f'rand_{file_idx:03d}')
            create_random_file(new_file, 512*1024*1024)
            files.append(new_file)
        start = time.perf_counter()
        with Pool() as pool:
            digests = pool.map(python_md5, files)
        end = time.perf_counter()
        python_digests = {files[idx]:digests[idx] for idx in range(len(files))}
        python_time = end - start

        start = time.perf_counter()
        with Pool() as pool:
            digests = pool.map(hasher.compute_md5, files)
        end = time.perf_counter()
        c_time = end - start
        c_digests = {files[idx]:digests[idx] for idx in range(len(files))}

        assert python_digests == c_digests
        assert c_time <= python_time

def python_md5(file: Path):
    with open(file, 'rb') as handle:
        return md5(handle.read()).hexdigest()

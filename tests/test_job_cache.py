'''Testing Job Cache
'''
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from utils import create_random_file

from e4e_deduplication.job_cache import JobCache
from pyfilehash.hasher import compute_sha256


def test_create_db():
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        job_db = temp_dir.joinpath('test.db')
        with JobCache(job_db) as cache:
            assert cache
            cache.add('asdf', job_db)
            assert 'asdf' in cache
            rows = cache['asdf']
            assert len(rows) == 1


def test_loading():
    n_files = 1024
    file_size = 1024
    n_duplicate = 4
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        job_db = temp_dir.joinpath('test.db')
        with JobCache(job_db) as cache:
            with TemporaryDirectory() as workingdir:
                working_dir = Path(workingdir).resolve()
                for file_idx in range(n_files):
                    new_file = working_dir.joinpath(f'{file_idx:06d}.bin')
                    create_random_file(new_file, file_size)
                    cache.add(compute_sha256(new_file), new_file)
                for file_idx in range(n_duplicate):
                    src_file = working_dir.joinpath(f'{file_idx:06d}.bin')
                    dupe_file = working_dir.joinpath(
                        f'{file_idx:06d}_dupe.bin')
                    shutil.copy(src_file, dupe_file)
                    cache.add(compute_sha256(dupe_file), dupe_file)
                assert len(cache.get_duplicates()) == n_duplicate

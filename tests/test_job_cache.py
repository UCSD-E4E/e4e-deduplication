'''Testing Job Cache
'''
import socket
from hashlib import sha256
from pathlib import Path
from random import randbytes
from tempfile import TemporaryDirectory
from time import perf_counter

from tqdm import tqdm

from e4e_deduplication.job_cache import JobCache


def test_create_db():
    """Tests creating the database
    """
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        job_db = temp_dir.joinpath('test')
        with JobCache(job_db) as cache:
            assert cache
            cache.add(job_db, 'baadf00d')
            assert 'baadf00d' in cache
            rows = cache['baadf00d']
            assert len(rows) == 1


def test_loading():
    """Load tests the sqlite server
    """
    n_files = 1024*1024
    n_duplicate = 4
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        job_db = temp_dir.joinpath('test')
        with JobCache(job_db) as cache:
            with TemporaryDirectory() as workingdir:
                working_dir = Path(workingdir).resolve()
                for file_idx in tqdm(range(n_files), desc='Creating Hashes'):
                    new_file = working_dir.joinpath(f'{file_idx:06d}.bin')
                    cache.add(new_file, sha256(
                        new_file.as_posix().encode()).hexdigest())
                for file_idx in tqdm(range(n_duplicate), desc='Creating Duplicates'):
                    src_file = working_dir.joinpath(f'{file_idx:06d}.bin')
                    dupe_file = working_dir.joinpath(
                        f'{file_idx:06d}_dupe.bin')
                    cache.add(dupe_file, sha256(
                        src_file.as_posix().encode()).hexdigest())
                assert len(cache.get_duplicates()) == n_duplicate


def test_drop_tree():
    """Tests dropping a tree in hashes
    """
    n_files = 5
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        job_cache_path = temp_dir.joinpath('hashes.csv')

        with JobCache(job_cache_path) as job_cache:
            for idx in range(n_files):
                job_cache.add(temp_dir.joinpath('files', 'tree',
                              f'{idx:06d}.bin'), f'c_{idx:06d}')
                job_cache.add(temp_dir.joinpath(
                    'files', f'{idx:06d}.bin'), f'{idx:06d}')
        with JobCache(job_cache_path) as job_cache:
            job_cache.drop_tree(
                host=socket.gethostname(),
                directory=temp_dir.joinpath('files', 'tree')
            )

        with JobCache(job_cache_path) as job_cache:
            for idx in range(n_files):
                assert f'{idx:06d}' in job_cache
                assert f'c_{idx:06d}' not in job_cache


def test_comma_filepaths():
    n_files = 5
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        job_cache_path = temp_dir.joinpath('hashes.csv')

        with JobCache(job_cache_path) as job_cache:
            for idx in range(n_files):
                job_cache.add(temp_dir.joinpath('files', 'tree',
                              f'{idx:06d},{idx}.bin'), f'c_{idx:06d}')
                job_cache.add(temp_dir.joinpath(
                    'files', f'{idx:06d},{idx}.bin'), f'{idx:06d}')

        with JobCache(job_cache_path) as job_cache:
            job_cache.drop_tree(
                host=socket.gethostname(),
                directory=temp_dir.joinpath('files', 'tree')
            )

        with JobCache(job_cache_path) as job_cache:
            for idx in range(n_files):
                assert f'{idx:06d}' in job_cache
                assert f'c_{idx:06d}' not in job_cache


if __name__ == '__main__':
    test_loading()

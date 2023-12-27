'''Testing Job Cache
'''
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from random import randbytes

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


def test_big_cache(big_hash_cache: Path):
    """Tests that the cache object can take in a big hash cache

    Args:
        big_hash_cache (Path): Path to big hash cache
    """
    with JobCache(big_hash_cache) as cache:
        start = perf_counter()
        in_cache = 'fffffe9151b1b72580f81ef81391ad0e74c3c39f5af784ba68a0594754b790ae' in cache
        paths = cache['fffffe9151b1b72580f81ef81391ad0e74c3c39f5af784ba68a0594754b790ae']
        end = perf_counter()
        assert in_cache is True
        assert paths
        assert (end - start) < 10


def test_hostname_agnostic_load():
    """Tests loading a hostname agnostic cache
    """
    n_lines = 1024
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        hash_map = {}
        with open(temp_dir.joinpath('hashes.csv'), 'w', encoding='utf-8') as handle:
            for idx in range(n_lines):
                digest = randbytes(32).hex()
                path = temp_dir.joinpath(f'{idx}.bin')
                handle.write(f'{digest},{path.as_posix()}')
                handle.write('\n')
                hash_map[digest] = path
        cache = JobCache(temp_dir)
        cache.open()
        for digest, path in hash_map.items():
            assert digest in cache
            assert len(cache[digest]) == 1
        cache.close()


def test_upgrade_cache(big_hash_cache: Path):
    """Tests that we can upgrade the cache

    Args:
        big_hash_cache (Path): Path to 2 column hash cache
    """
    with open(big_hash_cache.joinpath('hashes.csv'), 'r', encoding='utf-8') as handle:
        assert any(len(line.strip().split(',')) != 3 for line in handle)
    with JobCache(big_hash_cache) as job_cache:
        job_cache.set_unknown_hostnames()
    with open(big_hash_cache.joinpath('hashes.csv'), 'r', encoding='utf-8') as handle:
        assert all(len(line.strip().split(',')) == 3 for line in handle)


if __name__ == '__main__':
    test_loading()

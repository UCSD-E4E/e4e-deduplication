'''Testing Job Cache
'''
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

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


if __name__ == '__main__':
    test_loading()

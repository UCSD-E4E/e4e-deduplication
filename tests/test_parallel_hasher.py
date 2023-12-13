'''Tests Parallel hasher
'''
import os
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from tqdm import tqdm
from utils import create_random_file

from file_hasher import ParallelHasher
from e4e_deduplication.utils import path_to_str


class ParallelHashTester:
    """Parallel hasher accumulator
    """

    def __init__(self):
        self.data = {}

    def process_fn(self, path: str, digest: str):
        """Digest Processing Function

        Args:
            path (str): File path
            digest (str): File digest
        """
        self.data[path] = digest

    def hash_fn(self, path: str) -> str:
        """Hashing Function

        Args:
            path (str): Path to hash

        Returns:
            str: Hash Digest
        """
        with open(path, 'rb') as handle:
            return sha256(handle.read()).hexdigest()


def test_c_parallel_hasher():
    """Tests the C Parallel hasher
    """
    n_files = 1024
    file_size = 1024
    test_class = ParallelHashTester()
    hasher = ParallelHasher(
        test_class.process_fn, test_class.hash_fn, os.cpu_count())
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        file_paths = [temp_dir.joinpath(
            f'{idx:06d}.bin') for idx in range(n_files)]
        for file in file_paths:
            create_random_file(file, file_size)
        hasher.run(n_files)
        for path in path_to_str(tqdm(temp_dir.rglob('*'))):
            hasher.put(path)
        hasher.join()
    assert len(test_class.data) == n_files


if __name__ == '__main__':
    test_c_parallel_hasher()

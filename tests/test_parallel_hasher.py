'''Tests Parallel hasher
'''
import os
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from tqdm import tqdm
from utils import create_random_file

from file_hasher import ParallelHasher, HashType
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
        print("Python process_fn")
        self.data[path] = digest
        print("Python process_fn done")


def test_c_parallel_hasher():
    """Tests the C Parallel hasher
    """
    n_files = 1024
    file_size = 1024
    test_class = ParallelHashTester()
    hasher = ParallelHasher(
        test_class.process_fn, HashType.SHA256, 2)
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

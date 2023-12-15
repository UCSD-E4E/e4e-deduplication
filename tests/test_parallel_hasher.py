'''Tests Parallel hasher
'''
from pathlib import Path
from tempfile import TemporaryDirectory

from utils import create_random_file

from e4e_deduplication.parallel_hasher import ParallelHasher


class ParallelHashTester:
    """Parallel hasher accumulator
    """
    # pylint: disable=too-few-public-methods
    # test function

    def __init__(self):
        self.data = {}

    def process_fn(self, path: str, digest: str):
        """Digest Processing Function

        Args:
            path (str): File path
            digest (str): File digest
        """
        self.data[path] = digest


def test_c_parallel_hasher():
    """Tests the C Parallel hasher
    """
    n_files = 1024
    file_size = 1024
    test_class = ParallelHashTester()
    hasher = ParallelHasher(test_class.process_fn, None)
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        file_paths = [temp_dir.joinpath(
            f'{idx:06d}.bin') for idx in range(n_files)]
        for file in file_paths:
            create_random_file(file, file_size)
        hasher.run(temp_dir.rglob('*'), n_files)
    assert len(test_class.data) == n_files


if __name__ == '__main__':
    test_c_parallel_hasher()

'''Test Utilities
'''
from pathlib import Path
from random import randbytes


def create_random_file(temp_file: Path, size: int):
    """Creates a file with specified size using random data

    Args:
        temp_file (Path): File to create
        size (int): Size of file in bytes
    """
    with open(temp_file, 'wb') as handle:
        idx = 0
        while idx < size:
            rand_buffer = randbytes(min(2*1024*1024, size))
            if (size - idx) < len(rand_buffer):
                handle.write(rand_buffer[:size - idx])
                idx += size - idx
            else:
                handle.write(rand_buffer)
                idx += len(rand_buffer)
    assert temp_file.stat().st_size == size

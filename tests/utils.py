'''Test Utilities
'''
from pathlib import Path
from random import randbytes


def create_random_file(temp_file: Path, size: int):
    with open(temp_file, 'wb') as handle:
        idx = 0
        while idx < size:
            rand_buffer = randbytes(2*1024*1024)
            if (size - idx) < len(rand_buffer):
                handle.write(rand_buffer[:size - idx])
                idx += size - idx
            else:
                handle.write(rand_buffer)
                idx += len(rand_buffer)
    assert temp_file.stat().st_size == size


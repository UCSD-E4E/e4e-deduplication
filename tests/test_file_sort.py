'''Tests File Sort
'''
from pathlib import Path
from random import randbytes
from tempfile import TemporaryDirectory

from e4e_deduplication.file_sort import sort_file


def test_file_sort():
    """Tests the file sorting algorithm
    """
    n_lines = 1024*1024*4
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        file_to_sort = temp_dir.joinpath('files.csv')
        sorted_file = temp_dir.joinpath('sorted.csv')
        with open(file_to_sort, 'w', encoding='utf-8', newline='\n') as handle:
            for _ in range(n_lines):
                handle.write(randbytes(32).hex() + '\n')
        sort_file(file_to_sort, sorted_file)
        with open(sorted_file, 'r', encoding='utf-8', newline='\n') as handle:
            prev_line = ''
            for line in handle:
                assert line >= prev_line
                prev_line = line

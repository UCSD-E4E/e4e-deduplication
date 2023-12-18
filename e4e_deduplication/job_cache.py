'''Job Cache
'''
from __future__ import annotations

import os
from io import FileIO
from pathlib import Path
from typing import Dict, Set, List

from tqdm import tqdm
from e4e_deduplication.file_sort import sort_file


class JobCache:
    """Sqlite3 backed job cache
    """

    def __init__(self, path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True)
        if path.exists():
            if not path.is_dir():
                raise RuntimeError('Not a directory!')
        self.__hash_path = path.joinpath('hashes.csv')
        self.__hash_handle: FileIO = None
        self.__hash_cache: Dict[str, List[int]] = {}

    def __enter__(self) -> JobCache:
        self.open()
        return self

    def open(self):
        """Opens the cache
        """
        # pylint: disable=consider-using-with
        self.__hash_handle = open(self.__hash_path, 'a+', encoding='utf-8')
        # Resource needs to exist beyond the scope of this function
        self.__hash_handle.seek(0)
        prev_line = 0
        pb = tqdm(desc='Loading hash cache',
                  total=self.__hash_path.stat().st_size,
                  dynamic_ncols=True,
                  unit='B',
                  unit_scale=True)
        while line := self.__hash_handle.readline():
            digest = line.split(',')[0]
            if digest in self.__hash_cache:
                self.__hash_cache[digest].append(prev_line + len(digest) + 1)
            else:
                self.__hash_cache[digest] = [prev_line + len(digest) + 1]
            prev_line = self.__hash_handle.tell()
            pb.update(len(line) + 1)
        pb.close()
        self.__hash_handle.seek(0)

    def __exit__(self, exc, exv, exp) -> None:
        self.close()

    def close(self):
        """Closes the cache
        """
        self.__hash_handle.close()

    def __contains__(self, digest: str) -> bool:
        return digest in self.__hash_cache

    def __getitem__(self, digest: str) -> Set[Path]:
        paths: Set[Path] = set()
        for offset in self.__hash_cache[digest]:
            self.__hash_handle.seek(offset)
            paths.add(Path(self.__hash_handle.readline()))
        self.__hash_handle.seek(0)
        return paths

    def add(self, path: Path, digest: str):
        """Adds the path and digest to the job cache

        Args:
            path (Path): Path of file
            digest (str): File digest
        """
        self.__hash_handle.seek(0, os.SEEK_END)
        line_start = self.__hash_handle.tell()
        self.__hash_handle.writelines([f'{digest},{path.as_posix()}'])
        self.__hash_handle.write('\n')
        self.__hash_handle.seek(0)
        if digest in self.__hash_cache:
            self.__hash_cache[digest].append(line_start + len(digest) + 1)
        else:
            self.__hash_cache[digest] = [line_start + len(digest) + 1]

    def get_duplicates(self) -> Dict[str, Set[Path]]:
        """Generates the mapping of duplicates

        Returns:
            Dict[str, Set[Path]]: duplicates mapping
        """
        result: Dict[str, Set[Path]] = {}
        self.__hash_handle.close()
        sort_file(self.__hash_path, self.__hash_path)
        # pylint: disable=consider-using-with
        self.__hash_handle = open(self.__hash_path, 'a+', encoding='utf-8')
        # resource needs to exist beyond the scope of this function
        self.__hash_handle.seek(0)
        n_lines = sum(1 for _ in self.__hash_handle)
        self.__hash_handle.seek(0)
        current_digest = None
        file_set = set()
        for line in tqdm(self.__hash_handle,
                         desc='Discovering Duplicates',
                         total=n_lines,
                         dynamic_ncols=True):
            line_digest = line.split(',')[0]
            if not current_digest:
                current_digest = line_digest
            if line_digest != current_digest:
                if len(file_set) > 1:
                    result[current_digest] = file_set
                file_set = set()
                current_digest = line_digest
            file_set.add(Path(line.split(',')[1]))
        if len(file_set) > 1:
            result[current_digest] = file_set
        return result

    def clear(self) -> None:
        """Clears the job cache
        """
        self.__hash_handle.close()
        self.__hash_path.unlink()
        # pylint: disable=consider-using-with
        self.__hash_handle = open(self.__hash_path, 'a+', encoding='utf-8')
        # resource needs to exist beyond the scope of this function
        self.__hash_handle.seek(0)
        self.__hash_cache.clear()

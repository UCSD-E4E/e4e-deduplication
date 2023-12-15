'''Job Cache
'''
from __future__ import annotations

import os
from io import FileIO
from pathlib import Path
from typing import Dict, Set

from tqdm import tqdm


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
        self.__hash_cache: Set[bytes] = set()

    def __enter__(self) -> JobCache:
        self.open()
        return self

    def open(self):
        """Opens the cache
        """
        self.__hash_handle = open(self.__hash_path, 'w+', encoding='utf-8')
        for line in self.__hash_handle:
            digest = line.split(',')[0]
            self.__hash_cache.add(bytes.fromhex(digest))
        self.__hash_handle.seek(0)

    def __exit__(self, exc, exv, exp) -> None:
        self.close()

    def close(self):
        """Closes the cache
        """
        self.__hash_handle.close()

    def __contains__(self, digest: str) -> bool:
        return bytes.fromhex(digest) in self.__hash_cache

    def __getitem__(self, digest: str) -> Set[Path]:
        paths: Set[Path] = set()
        self.__hash_handle.seek(0)
        for line in self.__hash_handle:
            line_digest = line.split(',')[0]
            if line_digest != digest:
                continue
            paths.add(Path(line.split(',')[1]))
        self.__hash_handle.seek(0)
        return paths

    def add(self, path: Path, digest: str):
        """Adds the path and digest to the job cache

        Args:
            path (Path): Path of file
            digest (str): File digest
        """
        self.__hash_handle.seek(0, os.SEEK_END)
        self.__hash_handle.writelines([f'{digest},{path.as_posix()}'])
        self.__hash_handle.write('\n')
        self.__hash_handle.seek(0)
        self.__hash_cache.add(bytes.fromhex(digest))

    def get_duplicates(self) -> Dict[str, Set[Path]]:
        """Generates the mapping of duplicates

        Returns:
            Dict[str, Set[Path]]: duplicates mapping
        """
        result: Dict[str, Set[Path]] = {}
        for hash_value in tqdm(self.__hash_cache, desc='Finding Duplicates', dynamic_ncols=True):
            digest = hash_value.hex()
            self.__hash_handle.seek(0)
            paths = []
            for line in self.__hash_handle:
                line_digest = line.split(',')[0]
                if line_digest == digest:
                    paths.append(Path(line.split(',')[1]))
            if len(paths) > 1:
                result[digest] = set(paths)
        return result

    def clear(self) -> None:
        """Clears the job cache
        """
        self.__hash_handle.close()
        self.__hash_path.unlink()
        self.__hash_handle = open(self.__hash_path, 'w+', encoding='utf-8')
        self.__hash_cache.clear()

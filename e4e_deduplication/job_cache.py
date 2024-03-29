'''Job Cache
'''
from __future__ import annotations

import json
import logging
import os
import shutil
import socket
from io import FileIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List, Set, Tuple

from tqdm import tqdm

from e4e_deduplication.file_sort import sort_file


class JobCache:
    """Sqlite3 backed job cache
    """

    def __init__(self, path: Path) -> None:
        self.__log = logging.getLogger(f'Job Cache {path.name}')
        if not path.exists():
            path.mkdir(parents=True)
        if path.exists():
            if not path.is_dir():
                raise RuntimeError('Not a directory!')
        self.__hash_path = path.joinpath('hashes.csv')
        self.__hash_handle: FileIO = None
        self.__hash_cache: Dict[str, List[int]] = {}
        self.__current_hostname = socket.gethostname()
        self.__n_lines: int = None
        self.__sorted: bool = False

    def __enter__(self) -> JobCache:
        self.open()
        return self

    def open(self):
        """Opens the cache
        """
        # pylint: disable=consider-using-with
        self.__hash_handle = open(
            self.__hash_path, 'a+', encoding='utf-8', newline='\n')
        # Resource needs to exist beyond the scope of this function
        self.__rebuild_cache()
        self.__hash_handle.seek(0)

    def __rebuild_cache(self):
        self.__hash_handle.seek(0)
        self.__hash_cache.clear()
        prev_line_idx = 0
        self.__n_lines = 0
        prev_line = ''
        pb_ = tqdm(desc='Loading hash cache',
                   total=self.__hash_path.stat().st_size,
                   dynamic_ncols=True,
                   unit='B',
                   unit_scale=True)
        self.__sorted = True
        while line := self.__hash_handle.readline():
            document: Dict = json.loads(line)
            digest = document['digest']
            if digest in self.__hash_cache:
                self.__hash_cache[digest].append(
                    prev_line_idx)
            else:
                self.__hash_cache[digest] = [prev_line_idx]
            prev_line_idx = self.__hash_handle.tell()
            pb_.update(len(line) + 1)
            self.__n_lines += 1
            if line < prev_line:
                self.__sorted = False
            prev_line = line
        pb_.close()

    def __exit__(self, exc, exv, exp) -> None:
        self.close()

    def close(self):
        """Closes the cache
        """
        self.__hash_handle.close()

    def __contains__(self, digest: str) -> bool:
        return digest in self.__hash_cache

    def __getitem__(self, digest: str) -> Set[Tuple[Path, str]]:
        paths: Set[Path] = set()
        for offset in self.__hash_cache[digest]:
            paths.add(self.__extract_path_hostname(offset))
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
        document = json.dumps({
            'digest': digest,
            'path': path.as_posix(),
            'host': self.__current_hostname
        })
        self.__hash_handle.write(document + '\n')
        self.__hash_handle.seek(0)
        if digest in self.__hash_cache:
            self.__hash_cache[digest].append(line_start)
        else:
            self.__hash_cache[digest] = [line_start]
        self.__n_lines += 1
        self.__sorted = False

    def get_duplicates(self) -> Dict[str, Set[Tuple[Path, str]]]:
        """Generates the mapping of duplicates

        Returns:
            Dict[str, Set[Path]]: duplicates mapping
        """
        result: Dict[str, Set[Path]] = {}
        if not self.__sorted:
            self.__hash_handle.close()
            sort_file(self.__hash_path, self.__hash_path)
            # pylint: disable=consider-using-with
            self.__hash_handle = open(
                self.__hash_path, 'a+', encoding='utf-8', newline='\n')
            # resource needs to exist beyond the scope of this function
            self.__hash_handle.seek(0)
            self.__rebuild_cache()
            self.__sorted = True
        if not self.__n_lines:
            self.__hash_handle.seek(0)
            self.__n_lines = sum(1 for _ in self.__hash_handle)
            self.__hash_handle.seek(0)
        self.__log.info(
            f'Cache has {self.__n_lines} lines, {len(self.__hash_cache)} cache entries')
        n_offsets = 0
        for digest, offsets in tqdm(self.__hash_cache.items(),
                                    dynamic_ncols=True,
                                    desc='Discovering Duplicates'):
            if len(offsets) == 1:
                n_offsets += 1
                continue
            file_set = set()
            for offset in offsets:
                path_hostname_pair = self.__extract_path_hostname(offset)
                file_set.add(path_hostname_pair)
                n_offsets += 1
            result[digest] = file_set
        self.__log.debug(f'{n_offsets} offsets discovered')

        return result

    def __extract_path_hostname(self, offset: int) -> Tuple[Path, str]:
        self.__hash_handle.seek(offset)
        line = self.__hash_handle.readline().strip()
        document: Dict = json.loads(line)
        return Path(document['path']), document['host']

    def clear(self) -> None:
        """Clears the job cache
        """
        self.__hash_handle.close()
        self.__hash_path.unlink()
        # pylint: disable=consider-using-with
        self.__hash_handle = open(
            self.__hash_path, 'a+', encoding='utf-8', newline='\n')
        # resource needs to exist beyond the scope of this function
        self.__hash_handle.seek(0)
        self.__hash_cache.clear()
        self.__n_lines = 0

    def drop_tree(self, host: str, directory: Path):
        """Drops any paths that match the specified host/directory

        Args:
            host (str): Host to drop from
            directory (Path): Path to drop from
        """
        # pylint: disable=consider-using-with
        # resource needs to exist beyond the scope of this function
        # Need to modify the CSV
        with TemporaryDirectory() as tmpdir:
            temp_dir = Path(tmpdir).resolve()
            self.__hash_handle.seek(0)
            with open(file=temp_dir.joinpath('hashes.csv'),
                      mode='w',
                      encoding='utf-8',
                      newline='\n') as handle:
                shutil.copyfileobj(self.__hash_handle, handle)
            with open(file=temp_dir.joinpath('hashes.csv'),
                      mode='r',
                      encoding='utf-8',
                      newline='\n') as handle:
                self.__hash_handle.close()
                self.__hash_handle = open(
                    self.__hash_path, 'w', encoding='utf-8', newline='\n')
                for line in tqdm(handle,
                                 total=self.__n_lines,
                                 desc='Dropping Tree',
                                 dynamic_ncols=True):
                    if line.strip() == '':
                        continue
                    document = json.loads(line)
                    line_host = document['host']
                    line_path = Path(document['path'])
                    if line_host != host:
                        self.__hash_handle.write(line)
                        continue
                    if directory not in line_path.parents:
                        self.__hash_handle.write(line)
                        continue
        self.__hash_handle.close()
        self.__hash_handle = open(
            self.__hash_path, 'a+', encoding='utf-8', newline='\n')
        self.__hash_handle.seek(0)
        self.__rebuild_cache()

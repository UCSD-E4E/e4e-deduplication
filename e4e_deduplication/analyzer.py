'''File Analyzer
'''
from __future__ import annotations

import json
import logging
import re
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import schema
from pyfilehash.hasher import compute_sha256
from tqdm import tqdm


class Analyzer:

    def __init__(self, ignore_pattern: re.Pattern, job_path: Path):
        self.__ignore_pattern: re.Pattern = ignore_pattern
        self.__job_path = job_path
        self.__cache: Dict[str, Set[Path]] = {}
        self.logger = logging.getLogger('Analyzer')

    def parallel_process_hashes(self, working_dir: Path) -> List[Tuple[Path, str]]:
        paths_to_analyze = list(working_dir.rglob('*'))
        self.logger.info(f'Processing {len(paths_to_analyze)} files')
        with Pool(1) as pool:
            results = list(tqdm(map(
                self._compute_file_hash, paths_to_analyze),
                total=len(paths_to_analyze),
                desc='Computing File Hashes'))
        return [pair for pair in results if pair]

    def analyze(self, working_dir: Path) -> Dict[str, Set[Path]]:
        results = self.parallel_process_hashes(working_dir=working_dir)
        for path, digest in results:
            if digest in self.__cache:
                self.__cache[digest].add(path.resolve())
            else:
                self.__cache[digest] = set([path.resolve()])
        duplicate_paths: Dict[str, Set[Path]] = {}
        for digest, paths in self.__cache.items():
            if len(paths) > 1:
                duplicate_paths[digest] = paths
        return duplicate_paths

    def delete(self, working_dir, *, dry_run: bool = False) -> Dict[Path, str]:
        results = self.parallel_process_hashes(working_dir=working_dir)
        paths_to_remove: Dict[Path, str] = {}
        for path, digest in results:
            if digest not in self.__cache:
                continue
            matching_paths = self.__cache[digest]
            if path not in matching_paths:
                paths_to_remove[path] = digest
                if not dry_run:
                    path.unlink()
            else:
                if len(matching_paths) > 1:
                    paths_to_remove[path] = digest
                    if not dry_run:
                        path.unlink()
        return paths_to_remove

    def _compute_file_hash(self, path: Path) -> Optional[Tuple[Path, str]]:
        self.logger.info(f'Processing {path}')
        if self.__ignore_pattern and self.__ignore_pattern.search(path.as_posix()):
            self.logger.debug(f'Dropping {path} due to regex')
            return None
        if not path.is_file():
            self.logger.debug(f'Dropping {path} due to not a file')
            return None
        return path, compute_sha256(path)

    def __enter__(self) -> Analyzer:
        self.load()
        return self

    def __exit__(self, exc, exv, exp):
        self.save()

    def load(self) -> None:
        expected_schema = schema.Schema(
            {
                str: [str]
            }
        )
        if self.__job_path.is_file():
            with open(self.__job_path, 'r', encoding='utf-8') as handle:
                data: Dict[str, List[str]] = expected_schema.validate(
                    json.load(handle))
            for digest, paths in data.items():
                if digest not in self.__cache:
                    self.__cache[digest] = set([Path(path) for path in paths])
                else:
                    self.__cache[digest].update([Path(path) for path in paths])

    def save(self) -> None:
        self.__job_path.parent.mkdir(exist_ok=True, parents=True)
        with open(self.__job_path, 'w', encoding='utf-8') as handle:
            json.dump({digest: [path.as_posix() for path in paths]
                      for digest, paths in self.__cache.items()}, handle, indent=4)

    def clear_cache(self) -> None:
        self.__cache = {}

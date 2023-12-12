'''File Analyzer
'''
from __future__ import annotations

import json
import logging
import re
from multiprocessing.pool import ThreadPool as Pool
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import schema
from tqdm import tqdm

from pyfilehash.hasher import compute_sha256


class Analyzer:
    """Hash Analyzer Application
    """

    def __init__(self, ignore_pattern: re.Pattern, job_path: Path):
        self.__ignore_pattern: re.Pattern = ignore_pattern
        self.__job_path = job_path
        self.__cache: Dict[str, Set[Path]] = {}
        self.logger = logging.getLogger('Analyzer')

    def analyze(self, working_dir: Path) -> Dict[str, Set[Path]]:
        """Analyzes the working directory for duplicated files.  Also updates the job cache with
        every file encountered.

        Args:
            working_dir (Path): Directory to process

        Returns:
            Dict[str, Set[Path]]: Dictionary of digests and corresponding duplicated paths
        """
        n_files = sum(1 for _ in working_dir.rglob('*'))
        self.logger.info(f'Processing {n_files} files')
        with Pool() as pool:
            for path, digest in tqdm(pool.imap(self._compute_file_hash, working_dir.rglob('*')),
                                     total=n_files,
                                     desc='Computing File Hashes'):
                if digest is None:
                    continue
                if digest in self.__cache:
                    self.__cache[digest].add(path.resolve())
                else:
                    self.__cache[digest] = set([path.resolve()])
        duplicate_paths: Dict[str, Set[Path]] = {}
        for digest, paths in tqdm(self.__cache.items(), desc='Retrieving Duplicates'):
            if len(paths) > 1:
                duplicate_paths[digest] = paths
        return duplicate_paths

    def delete(self, working_dir: Path, *, dry_run: bool = False) -> Dict[Path, str]:
        """Deletes any files in the working directory that are duplicated elsewhere in this job.
        Does not add any new files to the cache.

        Args:
            working_dir (Path): Directory to search for and delete duplicates in
            dry_run (bool, optional): Dry run - suppress deletion if True. Defaults to False.

        Returns:
            Dict[Path, str]: Dictionary of paths and digests that were deleted
        """
        results = self.parallel_process_hashes(working_dir=working_dir)
        paths_to_remove: Dict[Path, str] = {}
        for path, digest in tqdm(results, desc='Deleting Duplicates'):
            if digest not in self.__cache:
                continue
            matching_paths = self.__cache[digest]
            if path not in matching_paths:
                # Hash matches, and this file is not in the reference set
                paths_to_remove[path] = digest
                if not dry_run:
                    path.unlink()
            else:
                if len(matching_paths) > 1:
                    # Hash matches, reference set has more than just this file
                    paths_to_remove[path] = digest
                    if not dry_run:
                        path.unlink()
        return paths_to_remove

    def _compute_file_hash(self, path: Path) -> Tuple[Path, Optional[str]]:
        self.logger.info(f'Processing {path}')
        if self.__ignore_pattern and self.__ignore_pattern.search(path.as_posix()):
            self.logger.debug(f'Dropping {path} due to regex')
            return (path, None)
        if not path.is_file():
            self.logger.debug(f'Dropping {path} due to not a file')
            return (path, None)
        return path, compute_sha256(path)

    def __enter__(self) -> Analyzer:
        self.load()
        return self

    def __exit__(self, exc, exv, exp):
        self.save()

    def load(self) -> None:
        """Loads the job cache from the job file
        """
        expected_schema = schema.Schema(
            {
                schema.Optional(str): [str]
            }
        )
        if self.__job_path.is_file():
            with open(self.__job_path, 'r', encoding='utf-8') as handle:
                data: Dict[str, List[str]] = expected_schema.validate(
                    json.load(handle))
            for digest, paths in data.items():
                if digest not in self.__cache:
                    self.__cache[digest] = {Path(path) for path in paths}
                else:
                    self.__cache[digest].update([Path(path) for path in paths])

    def save(self) -> None:
        """Saves the current cache to the job path
        """
        self.__job_path.parent.mkdir(exist_ok=True, parents=True)
        with open(self.__job_path, 'w', encoding='utf-8') as handle:
            json.dump({digest: [path.as_posix() for path in paths]
                      for digest, paths in self.__cache.items()}, handle, indent=4)

    def clear_cache(self) -> None:
        """Clears the job cache
        """
        self.__cache.clear()

'''File Analyzer
'''
from __future__ import annotations

import logging
import re
import socket
from pathlib import Path
from typing import Dict, List, Set, Tuple

from tqdm import tqdm

from e4e_deduplication.hasher import compute_sha256
from e4e_deduplication.job_cache import JobCache
from e4e_deduplication.parallel_hasher import ParallelHasher


class Analyzer:
    """Hash Analyzer Application
    """

    def __init__(self, ignore_pattern: re.Pattern, job_path: Path):
        self.__ignore_pattern: re.Pattern = ignore_pattern
        self.__job_path = job_path
        self.__cache: JobCache = JobCache(self.__job_path)
        self.__paths_to_remove: Dict[Path, str] = {}
        self.logger = logging.getLogger('Analyzer')
        self.__current_hostname = socket.gethostname()

    def analyze(self, working_dir: Path):
        """Analyzes the working directory for duplicated files.  Also updates the job cache with
        every file encountered.

        Args:
            working_dir (Path): Directory to process
        """
        n_files = 0
        n_bytes = 0

        for path in tqdm(working_dir.rglob('*'),
                         desc='Discovering files',
                         dynamic_ncols=True):
            n_files += 1
            if path.is_file():
                n_bytes += path.stat().st_size
        self.logger.info(f'Processing {n_files} files ({n_bytes} bytes)')

        hasher = ParallelHasher(
            self.__cache.add,
            self.__ignore_pattern,
            hash_fn=compute_sha256,
            n_bytes=n_bytes)
        hasher.run(working_dir.rglob('*'), n_files)

    def get_duplicates(self, *,
                       ignore_hashes: List[str] = None) -> Dict[str, Set[Tuple[Path, str]]]:
        """Return the report of duplicated files

        Returns:
            Dict[str, Set[Tuple[Path, str]]]: Dict of digests and corresponding duplicated paths
        """
        report = self.__cache.get_duplicates()
        if ignore_hashes:
            for digest in ignore_hashes:
                if digest in report:
                    report.pop(digest)
        return report

    def delete(self, working_dir: Path) -> Dict[Path, str]:
        """Deletes any files in the working directory that are duplicated elsewhere in this job.
        Does not add any new files to the cache.

        Args:
            working_dir (Path): Directory to search for and delete duplicates in

        Returns:
            Dict[Path, str]: Dictionary of paths and digests that were deleted
        """
        n_files = 0
        n_bytes = 0
        for path in tqdm(working_dir.rglob('*'),
                         desc='Discovering files',
                         dynamic_ncols=True):
            n_files += 1
            if path.is_file():
                n_bytes += path.stat().st_size
        self.logger.info(f'Processing {n_files} files ({n_bytes} bytes)')
        self.__paths_to_remove: Dict[Path, str] = {}
        hasher = ParallelHasher(
            self.__add_result_to_delete_queue,
            self.__ignore_pattern,
            hash_fn=compute_sha256,
            n_bytes=n_bytes)
        hasher.run(working_dir.rglob('*'), n_files)

        return self.__paths_to_remove

    def __add_result_to_delete_queue(self, path: Path, digest: str) -> None:
        if digest not in self.__cache:
            return
        matching_paths = self.__cache[digest]
        if (path, self.__current_hostname) not in matching_paths:
            # Hash matches, and this file is not in the reference set
            self.__paths_to_remove[path] = digest
        else:
            if len(matching_paths) > 1:
                # Hash matches, reference set has more than just this file
                self.__paths_to_remove[path] = digest

    def __enter__(self) -> Analyzer:
        self.load()
        return self

    def __exit__(self, exc, exv, exp):
        self.save()

    def load(self) -> None:
        """Loads the job cache from the job file
        """
        self.__cache.open()

    def save(self) -> None:
        """Saves the current cache to the job path
        """
        self.__cache.close()

    def clear_cache(self) -> None:
        """Clears the job cache
        """
        self.__cache.clear()

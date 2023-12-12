'''File Analyzer
'''
from __future__ import annotations

import json
import logging
import re
from multiprocessing import Event, Queue
from pathlib import Path
from threading import Thread
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

import schema
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

from pyfilehash.hasher import compute_sha256


class ParallelHasher:
    """Parallel Hashing Class
    """
    # pylint: disable=too-few-public-methods
    # This is meant to be a single method class

    def __init__(self,
                 process_fn: Callable[[Path, str], None],
                 ignore_pattern: re.Pattern):
        """Initializes the Parallel Hashing Class

        Args:
            process_fn (Callable[[Path, str], None]): Processing Function to retrieve the results
            ignore_pattern (re.Pattern): Regex pattern to use for ignore
        """
        self._result_queue = Queue()
        self._process_fn = process_fn
        self._ignore_pattern = ignore_pattern
        self.__result_run_event = Event()

    def run(self, paths: Iterable[Path], n_iter: int):
        """Runs the parallel hasher

        Args:
            paths (Iterable[Path]): Iterable of paths to hash
            n_iter (int): Number of iterations expected
        """
        self.__result_run_event.set()
        accumulator = Thread(target=self._result_accumulator)
        accumulator.start()
        thread_map(self._compute_file_hash, paths,
                   total=n_iter,
                   desc='Computing File Hashes')
        self.__result_run_event.clear()
        accumulator.join()

    def _result_accumulator(self):
        while self.__result_run_event.is_set() or not self._result_queue.empty():
            if not self._result_queue.empty():
                pair = self._result_queue.get(timeout=0.1)
                path, digest = pair
                self._process_fn(path, digest)

    def _compute_file_hash(self, path: Path) -> None:
        if self._ignore_pattern and self._ignore_pattern.search(path.as_posix()):
            return
        if not path.is_file():
            return
        result = (path, compute_sha256(path))
        self._result_queue.put(result)


class Analyzer:
    """Hash Analyzer Application
    """

    def __init__(self, ignore_pattern: re.Pattern, job_path: Path):
        self.__ignore_pattern: re.Pattern = ignore_pattern
        self.__job_path = job_path
        self.__cache: Dict[str, Set[Path]] = {}
        self.__dry_run = False
        self.__paths_to_remove: Dict[Path, str] = {}
        self.logger = logging.getLogger('Analyzer')

    def __add_result_to_cache(self, path: Path, digest: str) -> None:
        if digest in self.__cache:
            self.__cache[digest].add(path.resolve())
        else:
            self.__cache[digest] = set([path.resolve()])

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
        hasher = ParallelHasher(
            self.__add_result_to_cache, self.__ignore_pattern)
        hasher.run(working_dir.rglob('*'), n_files)
        duplicate_paths: Dict[str, Set[Path]] = {}
        for digest, paths in tqdm(self.__cache.items(), desc='Retrieving Duplicates'):
            if len(paths) > 1:
                duplicate_paths[digest] = paths
        return duplicate_paths

    def __add_result_to_delete_queue(self, path: Path, digest: str) -> None:
        if digest not in self.__cache:
            return
        matching_paths = self.__cache[digest]
        if path not in matching_paths:
            # Hash matches, and this file is not in the reference set
            self.__paths_to_remove[path] = digest
            if not self.__dry_run:
                path.unlink()
        else:
            if len(matching_paths) > 1:
                # Hash matches, reference set has more than just this file
                self.__paths_to_remove[path] = digest
                if not self.__dry_run:
                    path.unlink()

    def delete(self, working_dir: Path, *, dry_run: bool = False) -> Dict[Path, str]:
        """Deletes any files in the working directory that are duplicated elsewhere in this job.
        Does not add any new files to the cache.

        Args:
            working_dir (Path): Directory to search for and delete duplicates in
            dry_run (bool, optional): Dry run - suppress deletion if True. Defaults to False.

        Returns:
            Dict[Path, str]: Dictionary of paths and digests that were deleted
        """
        n_files = sum(1 for _ in working_dir.rglob('*'))
        self.logger.info(f'Processing {n_files} files')
        self.__dry_run = dry_run
        self.__paths_to_remove: Dict[Path, str] = {}
        hasher = ParallelHasher(
            self.__add_result_to_delete_queue, self.__ignore_pattern)
        hasher.run(working_dir.rglob('*'), n_files)

        return self.__paths_to_remove

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

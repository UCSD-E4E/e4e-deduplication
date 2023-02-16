"""
Represents a Directory.  Can be iterated over.
"""
from pathlib import Path
from typing import Generator, Set

from e4e_deduplication.file import File


class Directory:  # pylint: disable=too-few-public-methods
    """
    Represents a Directory.  Can be iterated over.
    """

    def __init__(self, path: Path, excluded_files: Set[str], root: Path = None):
        self._path = path
        self._excluded_files = excluded_files
        self._root = root if root else self._path
        self._file_iterator = None

    def _get_files(self) -> Generator[File, None, None]:
        for path in self._path.iterdir():
            if path.name in self._excluded_files:
                continue

            if path.is_dir():
                for file in Directory(path.absolute(), root=self._root.absolute()):
                    yield file
            elif path.is_file():
                yield File(path.absolute(), self._root.absolute())
            else:
                raise NotImplementedError

    def __iter__(self) -> Generator[File, None, None]:
        return self._get_files()

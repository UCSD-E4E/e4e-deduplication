"""
Represents a Directory.  Can be iterated over.
"""
from pathlib import Path
from typing import Generator, Set

from e4e_deduplication.file import File


# We are opting to disable too-few-public-methods because this object
# is intended to only be used as an iterator.
class Directory:  # pylint: disable=too-few-public-methods
    """
    Represents a Directory.  Can be iterated over.
    """

    def __init__(self, path: Path, excluded_paths: Set[Path], root: Path = None):
        self._path = path
        self._excluded_paths = excluded_paths
        self._root = root if root else self._path
        self._file_iterator = None

    def _get_files(self) -> Generator[File, None, None]:
        for path in self._path.iterdir():
            if path in self._excluded_paths:
                continue

            if path.is_dir():
                # This calls _get_files recurisvely, making the iterating over files recursive.
                for file in Directory(
                    path.absolute(), self._excluded_paths, root=self._root.absolute()
                ):
                    yield file
            elif path.is_file():
                yield File(path.absolute(), self._root.absolute())
            else:
                raise NotImplementedError

    def __iter__(self) -> Generator[File, None, None]:
        return self._get_files()

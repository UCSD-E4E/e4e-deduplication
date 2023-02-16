"""
Represents a Directory.  Can be iterated over.
"""
from pathlib import Path
from typing import Generator

from file import File


class Directory:
    """
    Represents a Directory.  Can be iterated over.
    """

    def __init__(self, path: Path, root: Path = None):
        self._path = path
        self._file_iterator = None
        self._root = root if root else self._path

    def _get_files(self) -> Generator[Path, None, None]:
        for p in self._path.iterdir():
            if p.is_dir():
                for f in Directory(p.absolute(), root=self._root.absolute()):
                    yield f
            elif p.is_file():
                yield File(p.absolute(), self._root.absolute())
            else:
                raise NotImplementedError

    def __iter__(self) -> Generator[Path, None, None]:
        return self._get_files()
